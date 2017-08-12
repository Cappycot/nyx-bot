"""
I've forever given up on optimizing the Unison League events timers, as the old
code is too much trouble to optimize at this point. Thus, I will port and
implement UTC timing with as little effort as possible. :<
"""

from asyncio import sleep
from configparser import ConfigParser
from datetime import datetime
from io import BytesIO
from os import listdir, mkdir
from os.path import isdir, isfile, join

import aiohttp
from PIL import Image
from discord import File
from discord.ext import commands
from discord.ext.commands import BucketType

from nyxcommands import has_privilege
from nyxutils import get_member, get_predicate, list_string, reply

folder = "unison"
events_folder = "events"
aliases_file = "Aliases.dat"
events_file = "Events.dat"
remind_folder = "reminders"
reminder_type = ".rem"
aliases = {}
events = {}
# Dictionary of {uid:{time:{code:ReminderTime}}}
# Times are integer stamps.
# Code-boolean pairings indicate if (True) continuous reminder or if
# it's (False) a one-time reminder.
reminders = {}
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]
elements = ["fire", "water", "wind", "light", "dark"]
times_list_threshold = 10


class Event:
    def __init__(self, name, daily, disabled, utc):
        self.name = name
        self.daily = daily
        self.disabled = disabled
        self.times = []  # Array of EventTime
        self.utc = utc


class EventTime:
    def __init__(self, code, start, end, utc):
        self.code = code
        self.start = start
        self.end = end
        self.utc = utc


class ReminderTime:
    def __init__(self, event, repeat):
        self.event = event
        self.repeat = repeat


def add_times(time1, minutes):
    day1 = time1 // 10000
    hour1 = (time1 % 10000) // 100
    min1 = time1 % 100 + minutes
    hour1 += min1 // 60
    min1 %= 60
    day1 += hour1 // 24
    hour1 %= 24
    while day1 > 7:
        day1 -= 7
    return day1 * 10000 + hour1 * 100 + min1


def add_utc(time, offset):
    if offset < 0:
        return sub_utc(time, offset)
    daily = time >= 10000
    time += offset * 100
    if time % 10000 >= 24:
        if daily:
            time -= 2400
        else:
            time += 7600
    if time >= 80000:
        time -= 70000
    return time


def sub_utc(time, offset):
    if offset < 0:
        return add_utc(time, offset)
    daily = time >= 10000
    hour = time % 10000
    if hour < offset * 100:
        if daily:
            time -= 10000
        time += 2400 - offset * 100
    else:
        time -= offset * 100
    if daily and time < 10000:
        time += 70000
    return time


def delta(time1: int, time2: int):
    """Gets the difference between two five-digit format times."""
    if time1 < 10000 or time2 < 10000:
        time1 %= 10000
        time2 %= 10000
        if time2 < time1:
            time2 += 2400
    elif time2 < time1:  # Weekly rollover
        time2 += 70000
    elif time2 >= 80000:
        time2 -= 70000
    day_diff = int(time2 / 10000) - int(time1 / 10000)
    hour_diff = int(time2 % 10000 / 100) - int(time1 % 10000 / 100)
    minute_diff = int(time2 % 100) - int(time1 % 100) - 1
    if minute_diff < 0:
        minute_diff += 60
        hour_diff -= 1
    if hour_diff < 0:
        hour_diff += 24
        day_diff -= 1
    return day_diff, hour_diff, minute_diff


def delta_string(time1: int, time2: int):
    """Gives the difference between five digit format times in readable
    form.
    """
    day, hour, minute = delta(time1, time2)
    result = ""
    if day > 0:
        result += str(day) + " day" + ("s, " if day != 1 else ", ")
    result += str(hour) + " hour" + ("s and " if hour != 1 else " and ")
    result += str(minute) + " minute" + ("s" if minute != 1 else "")
    return result


def datetime_match(event: EventTime, time, day, utc_offset):
    start = event.start
    end = event.end
    if event.utc:
        start = sub_utc(start, utc_offset)
        end = sub_utc(end, utc_offset)
    # Daily events will have start integers that are less than 10000.
    if start < 10000 and day != -1:  # Test for daily events like GvG
        start += day * 10000
        end += day * 10000
    start_day = start // 10000
    end_day = end // 10000
    start_time = start % 10000
    end_time = end % 10000
    # If the starting day of the event is the same day as the time.
    day_fit = day == -1 or day == start_day
    if not day_fit:
        # Or if the ending day of the event is the same day as the time
        # and the event end is beyond the top of the hour.
        day_fit = (day == end_day or day + 7 == end_day) and end_time > 0
    time_fit = time >= 10000 and (
        start <= time < end or start <= time + 70000 < end) or time == -1
    if not time_fit and time < 10000:
        if start_day != end_day:
            time_fit = time >= start_time or time < end_time
        else:
            time_fit = start_time <= time < end_time
    return day_fit and time_fit


def get_event(code, force_enable=False):
    """Gets a specific EventTime from an event from a 4-digit code."""
    if len(code) != 4:
        return None
    code = code.upper()
    key = code[:2]
    try:
        itr = int(code[2:]) - 1
        event = events.get(key)
        if event is not None and (not event.disabled or force_enable):
            return event.times[itr]
            # for eid in events:
            #     if eid == key and not events[eid].disabled:
            #         return events[eid].times[itr]
    except ValueError:
        return None


def get_full_name(key):
    event = events.get(key)
    if event is None:
        return "Unknown Quest"
    return event.name


def get_key(string):
    for key in aliases:
        if any(a in string for a in key[1]) or string in key[0]:
            return key[0]
    return None


def get_times():
    d_time = datetime.now()
    u_time = datetime.utcnow()
    return d_time, u_time


def half_day(string, hour):
    check = string.replace(".", "")
    if check == "am" and hour >= 12:
        return -1200
    elif check == "pm" and hour < 12:
        return 1200
    return 0


def letter_match(queries, key):
    """Matches a set of queries with the two character event type key."""
    if queries is None:
        return True
    return any(any(b in key for b in a.split(",")) for a in queries)


def is_day(string):
    val = 1
    for day in days:
        if day in string:
            return val
        val += 1
    if "today" in string:
        return datetime.now().weekday() + 1
    return -1


def is_event_code(string, force_enable=False):
    def enabled(a):
        return not events[a].disabled or force_enable

    # enabled = not events[a].disabled or force_enable
    return any(string == a.lower() and enabled(a) for a in events)


def time_stamp(datetime):
    day = datetime.weekday() + 1
    hour = datetime.hour
    minute = datetime.minute
    return day * 10000 + hour * 100 + minute


def is_time(string):
    try:
        parts = string.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        if 0 <= hour < 24 and 0 <= minute < 60:
            return hour * 100 + minute
    except (IndexError, ValueError):
        if "now" in string:
            return time_stamp(datetime.now())
        elif "noon" in string:
            return 1200
        elif "midnight" in string:
            return 0
    return -1


def pad(integer):
    """Pads a single zero for a two digit string."""
    return "0" + str(integer) if integer < 10 else str(integer)


def time_string(number, show_day=False):
    result = ""
    if number >= 80000:
        number -= 70000
    if number >= 10000 and show_day:
        result += days_full[int(number / 10000) - 1] + " "
    elif show_day:
        result += "(Daily) "
    number %= 10000
    return result + pad(int(number / 100)) + ":" + pad(number % 100)


def find_events(keys, time, day, utc_offset, force_enable=False):
    results = []
    if time >= 10000:
        day = time // 10000
    elif day != -1 and time != -1:
        time += day * 10000
    if keys is not None:
        for key in keys:
            event = get_event(key)
            if event is not None and event not in results and datetime_match(
                    event, time, day, utc_offset):
                results.append(event)
    for eid in events:
        if (not events[eid].disabled or force_enable) and letter_match(keys,
                                                                       eid):
            for e_time in events[eid].times:
                if datetime_match(e_time, time, day,
                                  utc_offset) and e_time not in results:
                    results.append(e_time)
    return results


def find_next_events(keys, time, day, utc_offset, force_enable=False):
    results = []
    if time < 10000 and day != -1:
        if time != -1:
            time += day * 10000
        else:
            time = day * 10000
    for eid in events:
        if (not events[eid].disabled or force_enable) and letter_match(keys,
                                                                       eid):
            next_time = None
            min_day = -1
            min_hour = -1
            min_min = -1  # lol min min wtf
            for e_time in events[eid].times:
                start_time = e_time.start
                if e_time.utc:
                    start_time = sub_utc(start_time, utc_offset)
                d, hour, minute = delta(time, start_time)
                day_less = d < min_day or min_day == -1
                same_day = d <= min_day
                hour_less = same_day and hour < min_hour
                min_less = same_day and hour <= min_hour and minute < min_min
                if day_less or hour_less or min_less:
                    next_time = e_time
                    min_day = d
                    min_hour = hour
                    min_min = minute
            results.append(next_time)
    return results


def parse_args(*args, force_enable=False):
    keys = []
    time = -1
    day = -1
    find_next = False

    def check(q):
        if not q:
            return None
        exists = get_event(q, force_enable) is not None
        exists = exists or is_event_code(q, force_enable)
        return get_key(q) or (q.upper().replace(",", "") if exists else None)

    query = ""
    was_time = False
    for arg in args:
        arg = arg.lower()
        if arg == "next":
            find_next = True
            continue
        find_day = is_day(arg)
        find_time = is_time(arg)
        if was_time:
            time += half_day(arg, time // 100)
            was_time = False
        find_key = find_day != -1 or find_time != -1 or query.endswith(",")
        if find_key:
            if find_day != -1:
                day = find_day
            elif find_time != -1:
                time = find_time
                if find_time >= 10000:
                    day = find_time // 10000
                was_time = True
            find_key = check(query)
            if find_key is not None:
                keys.append(find_key)
            query = ""
        query = " ".join([query, arg]).strip()
    find_key = check(query)
    if find_key is not None:
        keys.append(find_key)
    if len(keys) == 0:
        keys = None
    return keys, time, day, find_next


def fetch_reminders(uid, stamp, utc):
    global reminders
    times = reminders.get(uid)
    if times is None:
        return []
    codes = times.get(stamp)
    if codes is None:
        return []
    listing = []
    remove = []
    for code in codes:
        if get_event(code) is None:
            continue
        event = codes[code].event
        if event.utc == utc:
            if get_event(code) is not None:
                listing.append(event)
            if not codes[code].repeat:
                remove.append(code)
    for code in remove:
        codes.pop(code)
    if len(codes) == 0:
        times.pop(stamp)
        if len(times) == 0:
            reminders.pop(uid)
    return listing


def load_aliases():
    global aliases
    aliases = []
    config = ConfigParser()
    config.read(join(folder, events_folder, aliases_file))
    for eid in config["Aliases"]:
        aliases.append([eid.upper(), config["Aliases"][eid].split(";")])


def load_events():
    global events
    config = ConfigParser()
    events = {}
    config.read(join(folder, events_folder, events_file))
    for section in config.sections():
        name = section
        section = config[name]
        count = 1
        data = open(join(folder, events_folder, section["file"]))
        eid = section["id"]
        utc = section.getboolean("utc")
        event = Event(name, section.getboolean("daily"),
                      section.getboolean("disabled"), utc)
        for line in data:
            line = line.strip("\n ")
            if not line or line.startswith("#"):
                continue
            if count < 10:
                code = "{}0{}".format(eid, count)
            else:
                code = "{}{}".format(eid, count)
            times = line.split("-")
            event.times.append(
                EventTime(code, int(times[0]), int(times[1]), utc))
            count += 1
        # event.times.sort(key=lambda a: a.start)
        events[eid] = event


def load_reminders():
    global reminders
    reminder_dir = join(folder, remind_folder)
    if not isdir(reminder_dir):
        mkdir(reminder_dir)
    for item in listdir(reminder_dir):
        data = join(reminder_dir, item)
        if isfile(data) and item.endswith(reminder_type):
            try:
                uid = int(item[:-len(reminder_type)])
            except ValueError:
                continue
            user_reminders = {}
            data = open(data)
            for line in data:
                line = line.strip("\r\n ")
                if not line or line.startswith("#"):
                    continue
                listing = line.split(": ")
                stamp = int(listing[0])
                events = listing[1].split(", ")
                remind_time = user_reminders.get(stamp)
                if remind_time is None:
                    remind_time = {}
                    user_reminders[stamp] = remind_time
                for code in events:
                    event = get_event(code, True)
                    if event is not None and event.start == stamp:
                        remind_time[code] = ReminderTime(event, True)
            if len(user_reminders) > 0:
                reminders[uid] = user_reminders


def load_old_reminders():
    """Convert old Nyx reminders to new Nyx reminder codes."""
    global reminders
    reminder_dir = join(folder, "oldreminders")
    for item in listdir(reminder_dir):
        data = join(reminder_dir, item)
        if isfile(data) and item.endswith(reminder_type):
            try:
                uid = int(item[:-len(reminder_type)])
            except ValueError:
                continue
            user_reminders = {}
            data = open(data)
            for line in data:
                line = line.strip("\r\n ")
                if not line or line.startswith("#") or line.startswith("Name"):
                    continue
                listing = line.split(": ")
                events = listing[1].split(", ")
                # remind_time = user_reminders.get(stamp)
                # if remind_time is None:
                #     remind_time = {}
                #     user_reminders[stamp] = remind_time
                for code in events:
                    code = code.replace("GP", "PP")
                    try:
                        event = get_event(code, True)
                    except IndexError:
                        print(code)
                        continue
                    if event is not None:
                        stamp = event.start
                        remind_time = user_reminders.get(stamp)
                        if remind_time is None:
                            remind_time = {}
                            user_reminders[stamp] = remind_time
                        remind_time[code] = ReminderTime(event, True)
            if len(user_reminders) > 0:
                reminders[uid] = user_reminders
                save_reminders(uid)


def save_reminders(uid, debug_name=None):
    if reminders.get(uid) is None:
        return
    file_name = join(folder, remind_folder, str(uid) + reminder_type)
    user_file = open(file_name, "w")
    if debug_name is not None:
        user_file.write("# Name: {}".format(debug_name))
    for time in reminders[uid]:
        e_time = reminders[uid][time]
        if e_time is not None:
            event_string = []
            for code in e_time:
                if e_time[code] is not None and e_time[code].repeat:
                    event_string.append(code)
            event_string = ", ".join(event_string)
            if event_string:
                user_file.write("{}: {}\n".format(time, event_string))
    user_file.flush()
    user_file.close()


async def list_events(ctx, *args):
    d_time, u_time = get_times()
    stamp = time_stamp(d_time)
    utc_offset = (u_time - d_time).seconds // 3600
    keys, time, day, find_next = parse_args(*args)
    if find_next:
        if len(args) < 2:
            await reply(ctx, "You didn't tell me what events to find...")
            return
        elif keys is None:
            await reply(ctx, "I couldn't find any events with that name...")
            return
    current = (keys is None or find_next) and time == -1 and day == -1
    # or time == stamp) # this is a pointless check
    if current:
        time = stamp
    events = find_next_events(keys, time, day,
                              utc_offset) if find_next else find_events(
        keys, time, day, utc_offset)
    if len(events) == 0:
        await reply(ctx, "I couldn't find any events matching your query...")
    elif find_next:
        results = ["**Upcoming Events"]
        if not current:
            results.append(" After")
            if day != -1:
                results.append(" " + days_full[day - 1])
                if time != -1:
                    results.append(" at")
            if time != -1:
                results.append(" " + time_string(time))
        results.append(":**")
        events.sort(key=lambda a: a.code)
        for event in events:
            eid = event.code
            results.extend(
                ["\n - ", get_full_name(eid[:2]), " (" + eid + "): "])
            start_time = sub_utc(event.start,
                                 utc_offset) if event.utc else event.start
            if start_time >= 10000 and start_time // 10000 != day:
                results.extend([time_string(start_time, True), " - "])
            results.extend(["in ", delta_string(time, start_time), "."])
        results = "".join(results)
        await reply(ctx, results)
    else:
        results = ["**Current Events:**"]
        if not current:
            results = ["**Events",
                       " on " + days_full[day - 1] if day != -1 else "",
                       " at " + time_string(time) if time != -1 else "",
                       ":**"]
        events.sort(key=lambda a: a.code)
        for event in events:
            eid = event.code
            results.extend(
                ["\n - ", get_full_name(eid[:2]), " (" + eid + "): "])
            end_time = sub_utc(event.end,
                               utc_offset) if event.utc else event.end
            if current:
                results.append(delta_string(stamp, end_time))
                results.append(" remaining.")
            else:
                start_time = event.start
                if event.utc:
                    start_time = sub_utc(event.start, utc_offset)
                results.append(" ".join(
                    [time_string(start_time, True), "to",
                     time_string(end_time)]))
        if current:
            results.append(
                "\n**For Guild Battles, use ``{}".format(
                    ctx.prefix.replace(ctx.bot.user.mention,
                                       "@" + ctx.bot.user.name)))
            results.append("help events remind`` for more help!**")
        results = "".join(results)
        await reply(ctx, results)


async def add_reminders(ctx, *args):
    if len(args) == 0:
        await reply(ctx, "You didn't tell me what events to find...")
        return
    d_time, u_time = get_times()
    stamp = time_stamp(d_time)
    utc_offset = (u_time - d_time).seconds // 3600
    keys, time, day, find_next = parse_args(*args)
    # The only time we need cooldowns is if the command results in writing out
    # to file to prevent excessive I/O operations.
    if find_next and len(args) < 2:
        await reply(ctx, "You didn't tell me what events to find...")
        ctx.command.reset_cooldown(ctx)
        return
    elif keys is None:
        await reply(ctx, "I couldn't find any events with that name...")
        ctx.command.reset_cooldown(ctx)
        return
    if find_next:
        if time == -1 and day == -1:
            time = stamp
        events = find_next_events(keys, time, day, utc_offset)
    else:
        events = find_events(keys, time, day, utc_offset)
    if len(events) > 0:
        global reminders
        listing = {}
        imminent = {}
        uid = ctx.author.id
        reminder_set = reminders.get(uid)
        if reminder_set is None:
            reminder_set = {}
            reminders[uid] = reminder_set
        for event in events:
            start_time = event.start
            if find_next:
                start_delta = sub_utc(start_time,
                                      utc_offset) if event.utc else start_time
                d, h, m = delta(stamp, start_delta)
                delta_stamp = d * 10000 + h * 100 + m
                if delta_stamp <= 5:
                    imminent[event.code[:2]] = delta_string(stamp, start_delta)
                    continue
            reminder_time = reminder_set.get(start_time)
            if reminder_time is None:
                reminder_time = {
                    event.code: ReminderTime(event, not find_next)}
                reminder_set[start_time] = reminder_time
            else:
                reminder = reminder_time.get(event.code)
                if reminder is None or not reminder:
                    reminder_time[event.code] = ReminderTime(event,
                                                             not find_next)
                else:
                    continue
            if listing.get(event.code[:2]) is None:
                listing[event.code[:2]] = [event]
            else:
                listing[event.code[:2]].append(event)
        if len(listing) == 0 and len(imminent) == 0:
            await reply(ctx,
                        "I already have reminders set for those events...")
            return
        results = []
        if len(imminent) > 0:
            results.append("The following events are already imminent:")
            for eid in imminent:
                results.extend(
                    ["\n - ", get_full_name(eid), "(", get_event(eid).code,
                     "): in ", imminent[eid], "."])
        if len(listing) > 0:
            save_reminders(uid)
            results.append("\nI've added reminders for the following events:")
            for eid in listing:
                times_list = listing[eid]
                results.extend(["\n - ", get_full_name(eid)])
                if find_next:
                    event = times_list[0]
                    start_time = event.start
                    if event.utc:
                        start_time = sub_utc(event.start, utc_offset)
                    results.append(" ({}): In {}.".format(event.code,
                                                          delta_string(
                                                              time_stamp(
                                                                  d_time),
                                                              start_time)))
                elif len(times_list) > times_list_threshold:
                    results.extend([": ", str(len(times_list)), " times..."])
                else:
                    def key(a):
                        return time_string(
                            sub_utc(a.start, utc_offset) if a.utc else a.start,
                            True)

                    results.extend([": ", list_string(times_list, key=key)])
            results.extend(["\nI will DM you reminders for these events 5 ",
                            "minutes before they start. :>"])
        results = "".join(results)
        await reply(ctx, results)
    else:
        await reply(ctx, "I couldn't find any events matching your query...")
        ctx.command.reset_cooldown(ctx)


async def list_reminders(ctx, *args):
    pass


async def remove_reminders(ctx, *args):
    global reminders
    uid = ctx.author.id
    reminder_set = reminders.get(uid)
    if len(args) == 0:
        await reply(ctx,
                    "You didn't tell me what event reminders to remove...")
        return
    elif reminder_set is None:
        await reply(ctx, "You don't have any reminders...")
        return
    elif len(args) == 1 and any(
                    args[0].lower() == a for a in ["all", "everything"]):
        # Clear all reminders...
        reminders[uid] = {}
        save_reminders(uid)
        reminders.pop(uid)
        await reply(ctx, "I've removed all reminders you may have had.")
        return
    d_time, u_time = get_times()
    utc_offset = (u_time - d_time).seconds // 3600
    keys, time, day, _ = parse_args(*args, force_enable=True)
    if keys is None:
        await reply(ctx,
                    "I couldn't find any events with that name...")
        return
    events = find_events(keys, time, day, utc_offset, True)
    if len(events) == 0:
        await reply(ctx,
                    "I couldn't find any events matching your query...")
        return
    listing = {}
    for event in events:
        stamp = event.start
        codes = reminder_set.get(stamp)
        if codes is not None and codes.pop(event.code, None) is not None:
            if listing.get(event.code[:2]) is None:
                listing[event.code[:2]] = [event]
            else:
                listing[event.code[:2]].append(event)
            if len(codes) == 0:
                reminder_set.pop(stamp)
    if len(listing) == 0:
        await reply(ctx, "I couldn't find any reminders to remove...")
    else:
        save_reminders(uid)
        if len(reminder_set) == 0:
            reminders.pop(uid)
        results = ["I've removed reminders for the following events:"]
        for eid in listing:
            times_list = listing[eid]
            results.extend(["\n - ", get_full_name(eid), ": "])
            if len(times_list) > times_list_threshold:
                results.extend([str(len(times_list)), " times..."])
            else:
                def key(a):
                    return time_string(
                        sub_utc(a.start, utc_offset) if a.utc else a.start,
                        True)

                results.append(list_string(times_list, key=key))
        results = "".join(results)
        await reply(ctx, results)


class Unison:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.group(aliases=["event"])
    async def events(self, ctx):
        """Lists current event quests or events at a specified time.
        Use no arguments to get current events.
        Include the word "next" in your search to find the next occurring event
        after now or a specified time.

        e.g. "aug monday" will list all Augment Quests for Monday.
           - "aug noon" will list all Augment Quests that happen at noon.
           - "next aug monday noon" will find the Augment Quest that starts
                                    after Monday at 12:00.
        """
        if ctx.invoked_subcommand is not None:
            return
        predicate = get_predicate(ctx)
        await list_events(ctx, *tuple(predicate.split(" ")))
        # TODO: Figure out what to do with old code below.
        if True:
            return
        mention = ctx.bot.user.mention
        if ctx.guild is not None:
            mention = ctx.guild.get_member(ctx.bot.user.id).mention
        prefix = ctx.prefix.replace(mention, "@" + ctx.bot.user.name)
        results = "".join(["This command is still under construction...\n",
                           "To search events, use ``{}events list``.\n".format(
                               prefix),
                           "For other commands like ``remind``, use ",
                           "``{}help events`` for more info.".format(prefix)])
        await reply(ctx, results)

    @events.command(name="next")
    async def events_next(self, ctx, *args):
        """Finds the next iterations of specified events.
        It's a good idea to see what events are currently happening though.
        You can separate event names with a comma to specify multiple events.

        You can also enter a time to find events after a certain time.
        e.g. "aug" will list the next Augment Quest that happens from now.
           - "aug tuesday 2:00 p.m." will list the next Augment Quest that
                                     happens after Tuesday 14:00.
           - "reforge, aug" will list the next occurring enhancement quests.
        """
        await list_events(ctx, *("next",) + args)

    @events.command(name="remind")
    @commands.cooldown(1, 5, BucketType.user)
    async def events_remind(self, ctx, *args):
        """Sets reminders for specified events.
        Using the next keyword will change the reminder to be a one-time
        reminder for whatever events you name.
        You can separate event names with a comma to specify multiple events.

        e.g. "super aug" will set a reminder for all Super Augment Quests.
           - "guild battle a" will set a reminder for all Guild Battles in
                              schedule A.
           - "next eggs and key" will set a one-time reminder for the next
                                 Eggs and Keymin. (WIP)
        """
        await add_reminders(ctx, *args)

    @events.command(name="unremind")
    @commands.cooldown(1, 5, BucketType.user)
    async def events_unremind(self, ctx, *args):
        """Remove reminders for events you've set reminders for.
        Using the next keyword will permanently remove a reminder for the
        next occurrence of the specified event. (Even if it's not one-time.)
        You can separate event names with a comma to specify multiple events.

        e.g. "super gold" will remove all Super Gold Quests reminders.
           - "next aug" will permanently remove the next upcoming Augment
                        Quest from your reminders.
           - "all" will remove all reminders you have set.
        """
        await remove_reminders(ctx, *args)

    @commands.command()
    async def next(self, ctx, *args):
        """Finds the next iterations of specified events.
        It's a good idea to see what events are currently happening though.
        You can separate event names with a comma to specify multiple events.

        You can also enter a time to find events after a certain time.
        e.g. "aug" will list the next Augment Quest that happens from now.
           - "aug tuesday 2:00 p.m." will list the next Augment Quest that
                                     happens after Tuesday 14:00.
           - "reforge, aug" will list the next occurring enhancement quests.
        """
        await list_events(ctx, *("next",) + args)

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def remind(self, ctx, *args):
        """Sets reminders for specified events.
        Using the next keyword will change the reminder to be a one-time
        reminder for whatever events you name.
        You can separate event names with a comma to specify multiple events.

        e.g. "super aug" will set a reminder for all Super Augment Quests.
           - "guild battle a" will set a reminder for all Guild Battles in
                              schedule A.
           - "next eggs and key" will set a one-time reminder for the next
                                 Eggs and Keymin. (WIP)
        """
        await add_reminders(ctx, *args)

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def unremind(self, ctx, *args):
        """Remove reminders for events you've set reminders for.
        Using the next keyword will permanently remove a reminder for the
        next occurrence of the specified event. (Even if it's not one-time.)
        You can separate event names with a comma to specify multiple events.

        e.g. "super gold" will remove all Super Gold Quests reminders.
           - "next aug" will permanently remove the next upcoming Augment
                        Quest from your reminders.
           - "all" will remove all reminders you have set.
        """
        await remove_reminders(ctx, *args)

    @commands.command()
    @has_privilege(privilege=-1)
    async def reload(self, ctx):
        """For Cappy: Reload event times..."""
        load_events()
        await reply(ctx, "I've attempted to reload all event files.")

    @commands.command()
    async def gob(self, ctx):
        """GOB GOB"""
        await reply(ctx, "http://bit.ly/2fQLlbB")

    @commands.command(aliases=["bitch"])
    async def grey(self, ctx):
        await reply(ctx, "http://i.imgur.com/vvDBlmz.png")

    @commands.command(aliases=["r", "sr", "ssr", "ura"])
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def ur(self, ctx, *args):
        """Creates a UR monster of yourself or another user.
        Credit to Bevgebra for the templates...
        You can optionally specify an element and/or a name.

        e.g. "light" will make you a as a light element monster.
           - "dark Nyx" will make the user 'Nyx' as a dark element monster.
           - ""Witch Doctor"" will make the user 'Witch Doctor' as a monster.
        """
        if len(args) > 3:
            await reply(ctx, "Too many arguments you baka!")
            ctx.command.reset_cooldown(ctx)
            return

        element = None
        user = None

        for arg in args:
            if element is None:
                for ele in elements:
                    if ele in arg.lower():
                        element = ele[:1].upper() + ele[1:]
                        break
                if element is not None:
                    continue
            user = await get_member(ctx, arg)
            if user is None:
                await reply(ctx, "I don't know who you are talking about...")
                ctx.command.reset_cooldown(ctx)
                return
        if user is None:
            user = ctx.author

        rarity = ctx.invoked_with.upper()
        url = user.avatar_url or user.default_avatar_url
        # print(url)

        async with ctx.message.channel.typing(), aiohttp.ClientSession(
                loop=self.nyx.loop) as session, session.get(url) as req:
            if req.status == 200:
                imfile = BytesIO(await req.read())
                img = Image.open(imfile)
                snum = 5
                ednum = snum + 426
                base = Image.open(join(folder, rarity + "Base.png"))
                over = Image.open(
                    join(folder, rarity + "Overlay" + (
                        "" if element is None else "E") + ".png"))
                img = img.resize((426, 426), Image.LANCZOS)
                mask = img if "RGBA" in img.mode else None
                base.paste(img, (snum, snum, ednum, ednum), mask=mask)
                base.paste(over, mask=over)
                if element is not None:
                    element = Image.open(join(folder, element + ".png"))
                    base.paste(element, mask=element)
                # Save in-memory filestream and send to Discord
                imfile = BytesIO()
                base.save(imfile, format="png")
                # Move pointer to beginning so Discord can read pic.
                imfile.seek(0)
                msg = "New monster released in Unison League!"
                if ctx.guild is not None:
                    msg = ctx.message.author.mention + ", n" + msg[1:]
                await ctx.send(msg,
                               file=File(imfile, filename=rarity + ".png"))
                imfile.close()
            else:
                await reply(ctx, "Image loading failed! :<")

    async def clock(self):
        await self.nyx.wait_until_ready()
        last_minute = -1
        while True:
            await sleep(1)
            d_time = datetime.now()
            if d_time.minute != last_minute:
                last_minute = d_time.minute
                u_time = datetime.utcnow()
                d_stamp = add_times(time_stamp(d_time), 5)
                u_stamp = add_times(time_stamp(u_time), 5)
                for uid in reminders:
                    user = self.nyx.get_user(uid)
                    if user is None:
                        continue
                    listing = fetch_reminders(uid, d_stamp % 10000, False)
                    listing.extend(fetch_reminders(uid, d_stamp, False))
                    listing.extend(fetch_reminders(uid, u_stamp % 10000, True))
                    listing.extend(fetch_reminders(uid, u_stamp, True))
                    if len(listing) > 0:
                        remind_message = ["{}, the ".format(user.name),
                                          "following events will be up in ",
                                          "five minutes:"]
                        for event in listing:
                            remind_message.extend(
                                ["\n - ", get_full_name(event.code[:2])])
                        remind_message = "".join(remind_message)
                        await user.send(remind_message)


def setup(nyx):
    load_aliases()
    load_events()
    load_reminders()
    # load_old_reminders()
    unison = Unison(nyx)
    nyx.add_cog(unison)
    nyx.loop.create_task(unison.clock())
