# Event name manager for Nyx

import asyncio
from os import getcwd
from sys import exc_info

alias_filename = "Aliases.dat"
aliases = []

################################################################################
# Stock Functions
################################################################################

def get_key(string):
    global aliases
    for alias in aliases:
        if any(a in string for a in alias) or string in alias[0]:
            return alias[0]
    return None

################################################################################
# Command Functions
################################################################################

def list_aliases(message, desc = False, usage = False):
    reply = "**List of Aliases for Events:**"
    reply += "Umm... I haven't learned how to do this yet. >.<"
    return reply

################################################################################
# Module Functions
################################################################################

commands = []#[[["$alias", "$aliases", "$names", "$nick"], list_aliases, False]]


def load(folder):
    global aliases
    location = folder + "/" + alias_filename
    try:
        afile = open(location, "r")
        aliases = []
        for l in afile:
            line = l.replace("\n", "").replace("\r", "")
            if not line or line.startswith("#"):
                continue
            nick = line.split(": ")
            nickset = []
            nickset.append(nick[0])
            nick = nick[1].split(", ")
            nickset.extend(nick)
            aliases.append(nickset)
        # print(aliases) # Fat debug log kek
        return True
    except:
        print("Error found while registering event code aliases!")
        error = exc_info()
        for e in error:
            print(e)
        return False


async def clock(client, time):
    return




