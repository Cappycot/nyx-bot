# Miscellaneous, random functions for Nyx...

import asyncio
import discord
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

async def memetext(message = None, desc = False, usage = False, **_):
    if desc:
        return "Generates VERY LARGE GOB text."
    elif usage or len(message.content.split(" ")) < 2:
        return "Usage: $meme <text>"
    toreturn = "Meme created!\n"
    message.content = message.content.split(" ", 1)[1]
    for ch in message.content.lower():
        if ch >= 'a' and ch <= 'z':
            toreturn += ":regional_indicator_" + ch + ":"
        elif ch >= '0' and ch <= '9':
            toreturn += ":" + memenums[int(ch)] + ":"
        elif ch == " ":
            toreturn += "  "
        else:
            toreturn += ch
    if len(toreturn) > 1980:
        return "Your text is too long! >.<"
    return toreturn


async def ping(**_):
    return "Pong! :>"


async def pokemon(**_):
    song = "You want me to sing? >.< \\*Ahem\\*\n\n"
    song += "*I wanna be the very best*\n*Like no guild ever was*\n"
    song += "*To crush them is my real test*\n*My gear score is my cause*\n\n"
    song += "*I will battle across the land*\n*Crystals far and wide*\n"
    song += "*Legend medals fall in my hand*\n*The gear score lies inside*\n\n"
    song += "*Uni League! (Gotta match 'em all!)*\n"
    song += "*It's you and me...*\n"
    song += "*I know it's my destiny! Uni League!*\n"
    if random() < 0.5:
        song += "*Ooh... a Genesis; it's your teammate's foolishness*\n\n"
    else:
        song += "*Ooh... the Sacred Hand; as the soldier takes his stand*\n\n"
    song += "*Uni League! (Gotta match 'em all!)*\n"
    if random() < 0.5:
        song += "*A sting so true...*\n"
        song += "*Our lancers will break them through!*\n"
        song += "*An archer's strike and mage's skew*\n"
    else:
        song += "*Cleric's dignity...*\n"
        song += "*The healing will set us free!*\n"
        song += "*You EE and I cure thee!*\n"
    song += "***U-NI-LEAGUE!!***"
    return song


talks = ["<.< \\*Looks around\\* >.>"] + \
["Hello darkness my old friend..."] + \
["How do you think I feel when you people come to beat me up every Friday? T-T"] + \
["I am Nyx, Goddess of Twilight. Please check your darkness privilege..."] + \
["Loli? What's a loli? Is it short for lollipop?"] + \
["Me: Here come dat Nyx!!\nYou: Oh sh*t waddup!"] + \
["RNGesus? \*sniffle\* He was my childhood fwiend..."] + \
["The night... will last... forever!! AHAHAHAhaha...\n\\*Whimpers\\* Please don't hurt me... >.<"] + \
["You ask me for medals and I'll give you gold. :>"] + \
["You may ask, \"How many players in this game are named Kirito?\"\nHow many breads have you eaten in your life?"]


async def talk(**_):
    return talks[int(random() * len(talks))]


async def brup(client = None, message = None, **_):
    if client is None or message is None or message.server is None:
        return "WTF?!?"
    try:
        for emo in message.server.emojis:
            if emo.name.lower() == "nyx":
                await client.add_reaction(message, emo)
                break
    except:
        print("failed to add reaction rip")
    await client.send_message(message.channel, message.author.mention + ", timer for 30 seconds started.")
    await asyncio.sleep(30)
    return "timer for 30 seconds finished."


fdir = None

async def done(client = None, message = None, **_):
    done_pic = open(fdir + "/DoneNyx.png", "rb")
    await client.send_file(message.channel, done_pic)
    return


async def rng(client = None, message = None, **_):
    done_pic = open(fdir + "/RNGesusKek.png", "rb")
    await client.send_file(message.channel, done_pic)
    return


commands = [[["bitch", "grey"], bitch, False],
            [["gob"], gob, False],
            [["meme"], memetext, True],
            [["ping"], ping, False],
            [["pokemon", "pokémon"], pokemon, False],
            [["chat", "talk"], talk, False],
            [["jay", "burp", "brup",], brup, False],
            [["done"], done, False],
            [["rng"], rng, False]]


################################################################################
# Module Functions
################################################################################

def load(folder):
    global fdir
    fdir = folder
    return True


async def clock(client, time):
    return




