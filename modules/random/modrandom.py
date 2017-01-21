################################################################################
# Miscellaneous, random functions for Nyx...
################################################################################

import asyncio
import discord
from os import getcwd
from random import random

################################################################################
# Main/Global Variables
################################################################################



################################################################################
# Command Functions
################################################################################

async def bitch(**_):
    return "http://i.imgur.com/vvDBlmz.png"


async def gob(**_):
    return "http://bit.ly/2fQLlbB"


memenums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

async def memetext(message = None, **_):
    #if desc:
        #return "Generates VERY LARGE GOB text."
    #elif usage or len(message.content.split(" ")) < 2:
        #return "Usage: $meme <text>"
    toreturn = "Meme created!\n"
    message.content = message.content.split(" ", 1)[1]
    for ch in message.content.lower():
        if ch >= 'a' and ch <= 'z':
            toreturn += ":regional_indicator_" + ch + ":"
        elif ch >= '0' and ch <= '9':
            toreturn += ":" + memenums[int(ch)] + ":"
        elif ch == " ":
            toreturn += "   "
        else:
            toreturn += ch
    if len(toreturn) > 1980:
        return "Your text is too long! >.<"
    return toreturn


async def ping(**_):
    return "Pong! :>"


commands = [[["bitch", "grey"], bitch],
            [["gob"], gob],
            [["memetext"], memetext],
            [["ping"], ping]]


################################################################################
# Module Functions
################################################################################

def init(module, **_):
    for cmd in commands:
        module.add_command(cmd[1], cmd[0])
    return True




