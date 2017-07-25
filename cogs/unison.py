"""
I've forever given up on optimizing the Unison League events timers, as
the old code is too much trouble to optimize at this point. Thus, I port
and implement UTC timing with as little effort as possible. :<
"""

from configparser import ConfigParser
from datetime import datetime
from os.path import join

from discord.ext import commands

from nyxutils import respond

folder = "unison"
events_folder = "events"
aliases_file = "Aliases.dat"
events_file = "Events.dat"
remind_folder = "reminders"
aliases = {}
events = {}
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]


class Event:
    def __init__(self, name, daily, disabled, utc):
        self.name = name
        self.daily = daily
        self.disabled = disabled
        self.times = []  # Array of EventTime
        self.utc = utc

    def find(self, time, utc_time):
        pass

    def find_next(self, time, utc_time):
        pass


class EventTime:
    def __init__(self, code, start, end, utc):
        self.code = code
        self.start = start
        self.end = end
        self.utc = utc


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


def delta(time1: int, time2):
    """Gets the difference between two five-digit format times."""
    if time2 < time1:  # Weekly rollover
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
    return [day_diff, hour_diff, minute_diff]


def delta_string(time1: int, time2):
    """Gives the difference between five digit format times in readable
    form.
    """
    dt = delta(time1, time2)
    result = ""
    if dt[0] > 0:
        result += str(dt[0]) + " day" + ("s, " if dt[0] != 1 else ", ")
    result += str(dt[1]) + " hour" + ("s and " if dt[1] != 1 else " and ")
    result += str(dt[2]) + " minute" + ("s" if dt[2] != 1 else "")
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


def get_event(code):
    """Gets a specific EventTime from an event from a 4-digit code."""
    if len(code) != 4:
        return None
    code = code.upper()
    key = code[:2]
    try:
        itr = int(code[2:]) - 1
        for eid in events:
            if eid == key and not events[eid].disabled:
                return events[eid].times[itr]
    except ValueError:
        return None


def get_full_name(key):
    event = events.get(key)
    if event is None:
        return "Unknown Quest"
    return event.name


def get_key(string):
    for key in aliases:
        if any(a in string for a in aliases[key]) or string in key:
            return key
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


def is_event_code(string):
    return any(string == a.lower() and not events[a].disabled for a in events)


def is_time(string):
    try:
        parts = string.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        if 0 <= hour < 24 and 0 <= minute < 60:
            return hour * 100 + minute
    except (IndexError, ValueError):
        if "now" in string:
            d_time = datetime.now()
            day = d_time.weekday() + 1
            hour = d_time.hour
            minute = d_time.minute
            return day * 10000 + hour * 100 + minute
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


def find_events(keys, time, day, utc_offset):
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
        if not events[eid].disabled and letter_match(keys, eid):
            for e_time in events[eid].times:
                if datetime_match(e_time, time, day,
                                  utc_offset) and e_time not in results:
                    results.append(e_time)
    return results


def parse_args(*args):
    keys = []
    time = -1
    day = -1

    def check(q):
        if not q:
            return None
        return get_key(q) or (q.upper().replace(",", "") if get_event(
            q) is not None or is_event_code(q) else None)

    query = ""
    was_time = False
    for arg in args:
        arg = arg.lower()
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
    return keys, time, day


def load_aliases():
    global aliases
    aliases = {}
    config = ConfigParser()
    config.read(join(folder, events_folder, aliases_file))
    for eid in config["Aliases"]:
        aliases[eid.upper()] = config["Aliases"][eid].split(";")


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
        event.times.sort(key=lambda a: a.start)
        events[eid] = event


class Unison:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.group(aliases=["event"])
    async def events(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
        d_time, u_time = get_times()
        hour = d_time.hour
        minute = d_time.minute
        day = d_time.weekday() + 1
        stamp = day * 10000 + hour * 100 + minute
        utc_offset = (u_time - d_time).seconds // 3600
        events = find_events(None, stamp, day, utc_offset)
        if len(events) > 0:
            results = ["**Current Events:**"]
            for event in events:
                eid = event.code
                results.append(" ".join(
                    ["\n -", get_full_name(eid[:2]), "(" + eid + "): "]))
                end_time = sub_utc(event.end,
                                   utc_offset) if event.utc else event.end
                results.append(delta_string(stamp, end_time))
                results.append(" remaining.")
            results = "".join(results)
            await respond(ctx, results)
        else:
            await ctx.send("I died. Sorry.")

    @events.command()
    async def list(self, ctx, *args):
        d_time, u_time = get_times()
        hour = d_time.hour
        minute = d_time.minute
        day = d_time.weekday() + 1
        stamp = day * 10000 + hour * 100 + minute
        utc_offset = (u_time - d_time).seconds // 3600
        keys, time, day = parse_args(*args)
        print(keys)
        print(time)
        print(day)
        current = keys is None and (time == -1 and day == -1 or time == stamp)
        if current:
            time = stamp
        events = find_events(keys, time, day, utc_offset)
        if len(events) > 0:
            results = ["**Current Events:**"]
            if not current:
                results = ["**Events",
                           " on " + days_full[day - 1] if day != -1 else "",
                           " at " + time_string(time) if time != -1 else "",
                           ":**"]
            for event in events:
                eid = event.code
                results.append(" ".join(
                    ["\n -", get_full_name(eid[:2]), "(" + eid + "): "]))
                end_time = sub_utc(event.end,
                                   utc_offset) if event.utc else event.end
                if current:
                    results.append(delta_string(stamp, end_time))
                    results.append(" remaining.")
                else:
                    start_time = sub_utc(event.start,
                                         utc_offset) if event.utc else event.start
                    results.append(" ".join(
                        [time_string(start_time, True), "to",
                         time_string(end_time)]))
            if current:
                results.append(
                    "\n**For Guild Battles, use ``{}remind``".format(
                        ctx.prefix))
                results.append("for more help!**")
            results = "".join(results)
            await respond(ctx, results)
        else:
            await respond(ctx,
                          "I couldn't find any events matching your query...")

    @events.command()
    async def next(self, ctx, *args):
        print("Next")

    @events.command()
    async def remind(self, ctx, *args):
        print("Remind")


def setup(nyx):
    load_aliases()
    load_events()
    unison = Unison(nyx)
    nyx.add_cog(unison)
