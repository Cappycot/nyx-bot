# Event time manager for Nyx

import asyncio
from datetime import datetime
from nyxaliases import get_key
from utilsnyx import binary_search
from os import getcwd
from sys import exc_info

################################################################################
# Main/Global Variables
################################################################################

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday"] + \
            ["Friday", "Saturday", "Sunday"]
event_filename = "Events.dat"
events = []
ongoing = []

################################################################################
# Stock Functions
################################################################################

# Let's try not to use this one...
def between(val, lower, upper):
    return lower <= val < upper
    # return val >= lower and val < upper
    # Wow I'm a shitty Python coder


def clear_zeroes(string):
    while string.startswith("0") and len(string) > 1:
        string = string[1:]
    return string


def datetime_match(event, time, day):
    start = event[0]
    end = event[1]
    if start < 10000: # Test for daily events like GvG
        shift = day * 10000
        start += shift
        end += shift
        print("Calc daily occurrence for day: " + str(start))
        print("Current time: " + str(time))
        print("Current day: " + str(day))
    start_time = start % 10000
    end_time = end % 10000
    start_day = int(start / 10000)
    end_day = int(end / 10000) # I hate it when events straddle between days...
    dayfit = day == start_day or ((day == end_day or day + 7 == end_day) and end_time > 0) or day == -1
    timefit = time >= 10000 and (between(time, start, end) or between(time + 70000, start, end)) or time < 10000 and ((start_day != end_day and (time >= start_time or time < end_time)) or between(time, start_time, end_time)) or time == -1
    return dayfit and timefit


# Gets the difference between two five digit format times
def delta(time1, time2):
    if time2 < time1: # Weekly rollover
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


# Gives the difference between five digit format times in readable form
def delta_string(time1, time2):
    dt = delta(time1, time2)
    result = ""
    if dt[0] > 0:
        result += str(dt[0]) + " day" + (dt[0] != 1 and "s, " or ", ")
    result += str(dt[1]) + " hour" + (dt[1] != 1 and "s and " or " and ")
    result += str(dt[2]) + " minute" + (dt[2] != 1 and "s" or "")
    return result


# Gets a specific event iteration from a code
def get_event(code):
    code = code.replace(",", "").strip()
    if len(code) != 4:
        return None
    code = code.upper()
    try:
        key = code[:2]
        itr = int(clear_zeroes(code[2:])) + 1
        for event in events:
            if event[0] == key:
                return event[itr]
    except:
        return None


# Gets the full name of an event code
def get_full_name(key):
    global events
    for event in events:
        if event[0] in key:
            return event[1];
    return "Unknown Quest"


# Matches a set of queries with the two character event type key
def letter_match(queries, key):
    if queries is None:
        return True
    return any(any(b in key for b in a.split(",")) for a in queries)


# Pads a single zero for a two digit string
def pad(integer):
    return integer < 10 and "0" + str(integer) or str(integer)


def is_day(string):
    val = 1
    for day in days:
        if day in string:
            return val
        val += 1
    if "today" in string:
        return datetime.now().weekday() + 1
    return -1


def half_day(string, hour):
    check = string.replace(".", "")
    if check == "am" and hour >= 12:
        return -1200
    elif check == "pm" and hour < 12:
        return 1200
    return 0


def is_event_code(string):
    global events
    return any(string == a[0].lower() for a in events)

def is_time(string):
    try:
        parts = string.split(":")
        hour = int(clear_zeroes(parts[0]))
        minute = int(clear_zeroes(parts[1]))
        if 0 <= hour < 24 and 0 <= minute < 60:
            return hour * 100 + minute
        return -1
    except:
        if "now" in string:
            dtime = datetime.now()
            day = dtime.weekday() + 1
            hour = dtime.hour
            minute = dtime.minute
            return day * 10000 + hour * 100 + minute
        elif "noon" in string:
            return 1200
        elif "midnight" in string:
            return 0
        return -1


def time_string(number, show_day = False):
    result = ""
    if number >= 80000:
        number -= 70000
    if number >= 10000 and show_day:
        result += days_full[int(number / 10000) - 1] + " "
    elif show_day:
        result += "(Daily) "
    number %= 10000
    return result + pad(int(number / 100)) + ":" + pad(number % 100)    

################################################################################
# Command Functions
################################################################################

def parse_args(message):
    results = [None, -1, -1]
    text = message.content.split(" ", 1)
    if len(text) < 2:
        return results
    results[0] = []
    # I doubt this will even work...
    args = text[1].lower().split(" ")
    check = lambda q: get_key(q) or ((not get_event(q) is None or is_event_code(q)) and q.upper().replace(",", "") or None)
    query = ""
    was_time = False
    # Keyword parsing
    for arg in args:
        find_day = is_day(arg)
        find_time = is_time(arg)
        if was_time:
            results[1] += half_day(arg, int(results[1] / 100))
            was_time = False
        find_key = find_day != -1 or find_time != -1 or query.endswith(",")
        if find_key:
            if find_day != -1:
                results[2] = find_day
            elif find_time != -1:
                results[1] = find_time
                if find_time >= 10000:
                    results[2] = int(find_time / 10000)
                was_time = True
            print(query)
            find_key = check(query)
            if not find_key is None:
                results[0].append(find_key)
            query = ""
        query = (query + " " + arg).strip()
    find_key = check(query)
    if not find_key is None:
        results[0].append(find_key)
    if len(results[0]) == 0:
        results[0] = None
    return results

# Searches events that occur at a given time
def find_events(keys = None, time = -1, day = -1):
    global events
    results = []
    if time >= 10000:
        day = int(time / 10000)
    elif day != -1 and time != -1:
        time += day * 10000
    if not keys is None:
        for key in keys:
            event = get_event(key)
            if not event is None and datetime_match(event, time, day):
                results.append(event)
        results.sort(key = lambda a: a[2])
    for event in events:
        # print("Searching " + event[1] + "...") # Fat debug log kek
        if letter_match(keys, event[0]):
            for i in range(2, len(event)):
                if (datetime_match(event[i], time, day) and binary_search(results, event[i][2], key = lambda a: a[2]) is None):
                    results.append(event[i])
    return results


# Searches for the next occurring event after a given time
def find_next_events(keys = None, time = -1, day = -1):
    global events
    results = []
    if time >= 10000:
        day = int(time / 10000)
    elif day != -1:
        if time != -1:
            time += day * 10000
        else:
            time = day * 10000
    # print("Searching for events after " + str(time) + " and day " + str(day) + "...")
    for event in events:
        if letter_match(keys, event[0]) and len(event) > 2:
            next_event = event[2]
            for i in range(2, len(event)):
                start = event[i][0]
                start_time = start % 10000
                timefit = time >= 10000 and start >= time or time < 10000 and start_time >= time
                if timefit:
                    next_event = event[i]
                    break;
            results.append(next_event)
    return results


# List events occurring at a given time
async def list_events(message = None, desc = False, usage = False, **_):
    if desc:
        return "Lists the events occurring at a given time."
    elif usage:
        return "Usage: $events [name1], [name2]... [time] [day]\nInputting no arguments will list the current events."
    args = parse_args(message)
    # print(args)
    dtime = datetime.now()
    hour = dtime.hour
    minute = dtime.minute
    day = dtime.weekday() + 1
    stamp = day * 10000 + hour * 100 + minute
    current = args[0] is None and (args[1] == -1 and args[2] == -1 or args[1] == stamp)
    if current:
        args[1] = stamp
    events = find_events(args[0], args[1], args[2])
    if len(events) > 40:
        too_many = "I found too many events matching your query. Try narrowing your search..."
        too_many += "\nExample: $events reforge today"
        return too_many
    elif len(events) > 0:
        results = "**Current Events:**"
        if not current:
            results = "**Events" + (args[2] != -1 and " on " + days_full[args[2] - 1] or "")
            results += (args[1] != -1 and " at " + time_string(args[1]) or "") + ":**"
        for event in events:
            eid = event[2]
            results += "\n - " + get_full_name(event[2]) + " (" + eid + "): "
            if current:
                results += delta_string(stamp, event[1]) + " remaining."
            else:
                results += time_string(event[0], True) + " to " + time_string(event[1])
        return results
    else:
        return current and "This is awkward, but I don't have all the events listed yet. >.<" or "I couldn't find any events matching your query..."


# List the next occurrences of given events
async def list_next_events(message = None, desc = False, usage = False, **_):
    args = message.content.lower().strip().split(" ")
    usage_text = "Usage: $next <name1>, [name2]... [time] [day]\nAt least one event name or time must be input.\nExample: $next eggs"
    not_found = "I couldn't find any events matching your query...\nTry checking your spelling of event names or broaden your search..."
    if desc:
        return "Lists the next recurrence of a given event."
    elif usage or len(args) < 2:
        return usage_text
    args = parse_args(message)
    # print(args)
    dtime = datetime.now()
    hour = dtime.hour
    minute = dtime.minute
    day = dtime.weekday() + 1
    stamp = day * 10000 + hour * 100 + minute
    current = args[1] == -1 and args[2] == -1 or args[1] == stamp
    if current:
        args[1] = stamp
    elif args[2] != -1:
        if args[1] == -1:
            args[1] = args[2] * 10000
        else:
            args[1] += args[2] * 10000
    if args[0] is None and current:
        return not_found
    events = find_next_events(args[0], args[1], args[2])
    if len(events) > 0:
        results = "**Upcoming Events"
        if current:
            results += ":**"
        else:
            results += " After" + (args[2] != -1 and " " + days_full[args[2] - 1] or "")
            results += (args[1] != -1 and args[2] != -1 and " at" or "")
            results += (args[1] != -1 and " " + time_string(args[1]) or "") + ":**"
        for event in events:
            eid = event[2]
            results += "\n - " + get_full_name(event[2]) + " (" + eid + "): "
            start_day = int(event[0] / 10000)
            if start_day != day:
                results += time_string(event[0], True) + " - "
            # print(str(args[1]) + " to " + str(event[0]))
            results += "in " + delta_string(args[1], event[0]) + "."
        return results
    else:
        return not_found


async def time(message = None, desc = False, usage = False, **_):
    if desc:
        return "Displays the current Unison League time."
    elif usage:
        return "Usage: $time"
    dtime = datetime.now()
    stamp = (dtime.weekday() + 1) * 10000 + dtime.hour * 100 + dtime.minute
    return "Unison Time (Eastern Time): " + time_string(stamp, True)


################################################################################
# Module Functions
################################################################################

commands = [[["events", "event"], list_events, True],
           [["next", "incoming", "upcoming"], list_next_events, True],
           [["time", "clock"], time, True]]


def load(folder):
    # Define variables...
    global events
    print("Loading events and times...")
    location = folder + "/" + event_filename
    try:
        efile = open(location, "r")
        events = []
        event_set = []
        init = 0
        key = ""
        for l in efile:
            # Who the hell knows what line breaking chars there are? I don't.
            line = l.replace("\n", "").replace("\r", "")
            if not line or line.startswith("#"):
                continue
            elif line.startswith("END"):
                print(event_set[1] + " (" + key + ") loaded.")
                events.append(event_set)
                event_set = []
                init = 0
            elif init == 0:
                init = 1
                sp = line.split(": ")
                event_set.extend(sp)
                key = sp[0]
            else:
                sp = line.split("-")
                timeslot = []
                timeslot.append(int(sp[0]))
                timeslot.append(int(sp[1]))
                timeslot.append(key + pad(init))
                event_set.append(timeslot)
                init += 1
        # print(events) # Fat debug log kek
        return True
    except:
        print("Error found while reading event file!")
        error = exc_info()
        for e in error:
            print(e)
        return False


async def clock(client, time):
    return




