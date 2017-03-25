# Reminder manager for Nyx

import asyncio
from datetime import datetime
import discord
from nyxevents import delta, delta_string, get_event, get_full_name, find_events, parse_args, time_string
from utilsnyx import binary_search, list_string
from os import listdir, mkdir
from os.path import isfile, join
from sys import exc_info

################################################################################
# Main/Global Variables
################################################################################

ap_max = 144 # Never exceed number
ap_time_max = int(ap_max / 20) * 100 + (ap_max * 3) % 60
ap_reminders = [] # Format: [time, uid, name]
debug = False
# expd_reminders = [] # Format: [time, uid, name]
file_type = ".rem"
reminder_dir = "reminders"
reminder_folder = None
users = []

################################################################################
# Userdata Class
################################################################################

class ReminderSet:
    def __init__(self, time):
        self.time = time
        self.events = []
    def add_event(self, code):
        if binary_search(self.events, code) is None:
            self.events.append(code)
            self.events.sort()
            return True
        return False
    def remove_event(self, code):
        to_remove = binary_search(self.events, code)
        if to_remove is None:
            return False
        else:
            self.events.remove(to_remove)
            return True


class User:
    def __init__(self, uid, naem = "User"):
        self.id = uid
        self.name = naem
        self.reminders = []
    def add_reminder(self, time, code):
        rem_set = binary_search(self.reminders, time, key = lambda a: a.time)
        if rem_set is None:
            rem_set = ReminderSet(time)
            self.reminders.append(rem_set)
            self.reminders.sort(key = lambda a: a.time)
        return rem_set.add_event(code)
    def remove_reminder(self, time, code):
        rem_set = binary_search(self.reminders, time, key = lambda a: a.time)
        if rem_set is None:
            return False
        else:
            removed = rem_set.remove_event(code)
            if len(rem_set.events) == 0:
                self.reminders.remove(rem_set)
            return removed

################################################################################
# Module Functions
################################################################################

def add_times(time1, minutes):
    day1 = int(time1 / 10000)
    hour1 = int((time1 % 10000) / 100)
    min1 = time1 % 100 + minutes
    hour1 += int(min1 / 60)
    min1 %= 60
    day1 += int(hour1 / 24)
    hour1 %= 24
    while day1 > 7:
        day1 -= 7
    return day1 * 10000 + hour1 * 100 + min1


# Create or modify AP reminder
def ap_remind(time, uid, name):
    found = False
    for ar in ap_reminders:
        if ar[1] == uid:
            ar[0] = time
            ar[2] = name
            found = True
            break
    if not found:
        ap_reminders.append([time, uid, name])
    sorted(ap_reminders, key = lambda a: a[0])


# Get AP reminder for certain user
def ap_get_remind(uid):
    for ar in ap_reminders:
        if ar[1] == uid:
            return ar
    return None


# Delete AP reminder
def ap_unremind(uid):
    ar = ap_get_remind(uid)
    if not ar is None:
        ap_reminders.remove(ar)
        return True
    return False


def append_reminder(user, time, event):
    file_name = reminder_folder + "/" + user.id + file_type
    user_file = open(file_name, "a")
    user_file.write("\n" + str(time) + ": " + event)
    user_file.flush()


def list_events(events):
    to_return = ""
    for event in events:
        print(event)
    return to_return
    
    
def save_reminders(user):
    file_name = reminder_folder + "/" + user.id + file_type
    user_file = open(file_name, "w")
    user_file.write("Name: " + user.name)
    user_file.write("\n# Generated user reminders. Possible bugs?")
    for slot in user.reminders:
        user_file.write("\n" + str(slot.time) + ": ")
        event_string = ""
        for event in slot.events:
            event_string += event + ", "
        user_file.write(event_string[:-2]) # Trims last comma space
    user_file.flush()


################################################################################
# Command Functions
################################################################################

async def ap(message = None, desc = False, usage = False, **_):
    global ap_max
    global ap_reminders
    args = message.content.lower().strip().split(" ")
    dtime = datetime.now()
    hour = dtime.hour
    minute = dtime.minute
    day = dtime.weekday() + 1
    stamp = day * 10000 + hour * 100 + minute
    uid = message.author.id
    premind = ap_get_remind(uid)
    usage_text = "Usage: $ap <stats/remind/unremind> [current AP] [max AP]"
    if desc:
        return "AP regenerates by one every three minutes; tracks times."
    elif len(args) == 2 and "remind" in args[1]:
        if "un" in args[1] and not premind is None:
            ap_reminders.remove(premind)
            return "Your AP reminder has been removed..."
        elif not premind is None:
            return "I have a AP reminder for you scheduled for " + time_string(premind[0]) + " in Unison Time, which is in " + delta_string(stamp, premind[0]) + "."
        return "I don't have a reminder for your AP..."
    elif usage or len(args) != 4:
        return usage_text
    current_AP = 0
    max_AP = 0
    try:
        current_AP = int(args[2])
        max_AP = int(args[3])
        if max_AP > ap_max:
            max_AP = ap_max
        difference = max_AP - current_AP - 1
        if difference <= 0:
            return "Your AP is pretty much full already! What are you asking of me? >.<"
        else:
            dest_time = add_times(stamp, difference * 3)
            uid = message.author.id
            premind = ap_get_remind(uid)
            to_return = "Your AP will be (almost) full at " + time_string(dest_time) + " in Unison Time, which is in " + delta_string(stamp, dest_time) + "."
            if args[1].startswith("remind"):
                ap_remind(dest_time, uid, message.author.name)
                to_return += premind is None and "\nI will PM you a reminder at this time. :>" or "\nI have modified your existing AP reminder to match this time."
            elif not premind is None:
                to_return += "\nYou already have an AP reminder set for " + time_string(premind[0]) + ", however."
            return to_return
    except:
        return usage_text


async def list_reminders(message = None, desc = False, usage = False, **_):
    return "Oh crap I don't have this code written yet... Forgive me! >.<"


async def remove_reminders(message = None, desc = False, usage = False, **_):
    global users
    args = message.content.lower().strip().split(" ")
    usage_text = "**Usage:** $unremind <name1>, [name2]... [time] [day]\nAt least one event name must be input.\nExample: ``$unremind eggs``"
    usage_text += "\n**For Guild Battles, use ``$unremind gb``**"
    if desc:
        return "Removes event reminders."
    elif usage or len(args) < 2:
        return usage_text
    remove_all = any(args[1] == a for a in ["all", "everything"])
    args = parse_args(message)
    events = find_events(args[0], args[1], args[2])
    no_args = args[0] is None and args[1] == -1 and args[2] == -1
    remove_all = remove_all and no_args
    if no_args and not remove_all or len(events) == 0:
        return "I couldn't find any events matching your query..."
    # elif len(events) > 40 and not remove_all:
        # too_many = "I found too many events matching your query. Try narrowing your search..."
        # too_many += "\nExample: ``$unremind keymin monday``"
        # return too_many
    else:
        uid = message.author.id
        user = binary_search(users, uid, key = lambda a: a.id)
        none_removed = "I couldn't find any reminders to remove..."
        if user is None:
            return none_removed
        listing = []
        for event in events:
            removed = user.remove_reminder(event[0], event[2])
            if not removed:
                continue
            category = event[2][:2]
            c_list = binary_search(listing, category, key = lambda a: a[0])
            if c_list is None:
                c_list = [category, [event[0]]]
                listing.append(c_list)
                listing.sort(key = lambda a: a[0])
            else:
                c_list[1].append(event[0])
                c_list[1].sort()
        if len(listing) == 0:
            return none_removed
        else:
            save_reminders(user)
        reply = remove_all and "I've removed all set reminders." or "I've removed reminders for the following events:"
        if not remove_all:
            for elist in listing:
                reply += "\n - " + get_full_name(elist[0]) + ": "
                if len(elist[1]) <= 10:
                    reply += list_string(elist[1], key = lambda a: time_string(a, True))
                else:
                    reply += str(len(elist[1])) + " times..."
        return reply


async def set_reminders(message = None, desc = False, usage = False, **_):
    global users
    args = message.content.lower().strip().split(" ")
    usage_text = "**Usage:** $remind <name1>, [name2]... [time] [day]\nAt least one event name must be input.\nExample: ``$remind eggs``"
    usage_text += "\n**For Guild Battles, be sure to specify the schedule!**"
    usage_text += "\nExample: ``$remind guild battle a`` or ``$remind gba``"
    if desc:
        return "Sets reminders for events."
    elif usage or len(args) < 2:
        return usage_text
    elif args[1].startswith("list"):
        return list_reminders(message, desc, usage)
    args = parse_args(message)
    events = find_events(args[0], args[1], args[2])
    no_args = args[0] is None and args[1] == -1 and args[2] == -1
    if no_args or len(events) == 0:
        return "I couldn't find any events matching your query..."
    # if len(events) > 20 and not message.server is None or len(events) > 40:
        # too_many = "I found too many events matching your query. Try narrowing your search..."
        # too_many += "\nExample: ``$remind keymin monday``"
        # too_many += "\n**For Guild Battles, be sure to specify the schedule!**"
        # too_many += "\nExample: ``$remind guild battle a`` or ``$remind gba``"
        # return too_many
    elif len(events) > 0:
        uid = message.author.id
        user = binary_search(users, uid, key = lambda a: a.id)
        new_user = user is None
        if new_user:
            user = User(uid, naem = message.author.name)
            users.append(user)
            users.sort(key = lambda a: a.id)
        listing = []
        for event in events:
            added = user.add_reminder(event[0], event[2])
            if not added:
                continue
            elif not new_user:
                append_reminder(user, event[0], event[2])
            category = event[2][:2]
            c_list = binary_search(listing, category, key = lambda a: a[0])
            if c_list is None:
                c_list = [category, [event[0]]]
                listing.append(c_list)
                listing.sort(key = lambda a: a[0])
            else:
                c_list[1].append(event[0])
                c_list[1].sort()
        if len(listing) == 0:
            return "I already have reminders set for all the events you've specified..."
        elif new_user:
            save_reminders(user)
        reply = "I've added reminders for the following events:"
        for elist in listing:
            reply += "\n - " + get_full_name(elist[0]) + ": "
            if len(elist[1]) <= 10:
                reply += list_string(elist[1], key = lambda a: time_string(a, True))
            else:
                reply += str(len(elist[1])) + " times..."
        reply += "\nI will PM you reminders for these events five minutes before they start. :>"
        return reply        

################################################################################
# Module Functions
################################################################################

commands = [[["ap", "cost"], ap, True],
            # [["$expd", "$exped"], expd, True]
            [["reminders", "list"], list_reminders, False],
            [["remind", "notif"], set_reminders, True],
            [["unremind"], remove_reminders, True]]


def load(folder):
    print("Loading reminders...")
    global debug
    global reminder_folder
    global users
    remind_folder = folder + "/" + reminder_dir
    reminder_folder = remind_folder
    user_ids = []
    try:
        users = []
        for item in listdir(remind_folder):
            data = join(remind_folder, item)
            if isfile(data) and item.endswith(file_type):
                user_ids.append(str(item)[:-len(file_type)])
        user_ids.sort()
        print(user_ids)
        for uid in user_ids:
            print("Reading data for ID " + uid + "...")
            file_name = remind_folder + "/" + uid + file_type
            data = open(file_name, "r")
            user = User(uid)
            for l in data:
                line = l.replace("\n", "").replace("\r", "")
                if not line or line.startswith("#"):
                    continue
                elif line.startswith("Name: "):
                    user.name = line[6:]
                    print("Read name as " + user.name + ".")
                else:
                    listing = line.split(": ")
                    stamp = int(listing[0])
                    events = listing[1].split(", ")
                    for code in events:
                        event = get_event(code)
                        if not event is None and event[0] == stamp:
                            print("Adding event " + event[2] + " (" + code + ") at " + time_string(stamp, True) + ".")
                            user.add_reminder(stamp, code)
                        else:
                            print("Unable to reference event code " + code + " correctly. It has been removed.")
            users.append(user)
            users.sort(key = lambda a: a.id)
            save_reminders(user)
        return not debug
    except FileNotFoundError:
        mkdir(remind_folder)
        print("The directory for reminder folder \"" + reminder_dir + "\" does not exist and has been created.")
        return True
    except:
        print("Error found while reading reminder userdata!")
        error = exc_info()
        for e in error:
            print(e)
        return False


async def clock(client, time):
    global ap_reminders
    global users
    del_ap_reminders = []
    stamp = (time.weekday() + 1) * 10000 + time.hour * 100 + time.minute
    # AP Reminders
    for ar in ap_reminders:
        if ar[0] == stamp:
            to_remind = discord.User(id = ar[1])
            await client.send_message(to_remind, "Umm... " + ar[2] + ", your AP is almost full by now.")
            del_ap_reminders.append(ar)
        else:
            dt = delta(stamp, ar[0])
            delta_stamp = dt[0] * 10000 + dt[1] * 100 + dt[2]
            if delta_stamp > ap_time_max:
                del_ap_reminders.append(ar)
    for ar in del_ap_reminders:
        ap_reminders.remove(ar)
    # Event Reminders
    if time.minute % 5 == 0:
        stamp = add_times(stamp, 5)
        for user in users:
            reminders = binary_search(user.reminders, stamp, key = lambda a: a.time)
            if not reminders is None:
                remind_message = "Umm... " + user.name + ", the following events will be up in five minutes:"
                to_remind = discord.User(id = user.id)
                for event in reminders.events:
                    remind_message += "\n - " + get_full_name(event)
                await client.send_message(to_remind, remind_message)




