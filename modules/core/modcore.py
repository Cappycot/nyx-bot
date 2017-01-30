################################################################################
# The Heart of Nyx
################################################################################

import asyncio
from utilsnyx import list_string, remove_bots
from sys import exc_info

execute = None


################################################################################
# Core Functions
################################################################################

def get_privilege(person):
    level = [1]
    execute("""
person = kwargs["person"]
user = find_user(person)
if not user is None:
    kwargs["level"][0] = user.privilege
    """, person = person, level = level)
    return level[0]
    
def set_privilege(person, level):
    if level < 0:
        level = 1
    execute("""
person = kwargs["args"][0]
user = find_user(person)
if user is None:
    user = add_user(person)
privilege = kwargs["args"][1]
if user.privilege > 0 and privilege == 1 or user.privilege >= 0 and privilege != 1:
    user.privilege = privilege
    """, args = [person, level])


################################################################################
# Command Functions
################################################################################
# Root Server Commands:
#  - @Nyx $block @user
#  - @Nyx $unblock @user
#  - @Nyx $debug
#  - @Nyx $echo message...
#  - @Nyx $exec
#  - @Nyx $op @user
#  - @Nyx $deop @user
#  - @Nyx $shutdown


async def debug(message = None, **_):
    result = []
    execute("""
global debug
debug = not debug
kwargs["result"].append(str(debug).lower())
""", result = result)
    return "Debug mode set to " + result[0] + "."


async def fullstop(client = None, message = None, **_):
    if client and message:
        await client.send_message(message.channel, "Light cannot be without dark!!!")
    print("full stop")
    execute("""
global shutdown
shutdown = True
""")


################################################################################
# User Privilege Functions
################################################################################

async def block(message = None, **_):
    if message is None:
        return
    remove_bots(message.mentions)
    for person in message.mentions:
        set_privilege(person, 0)
    return "Attempted to block " + list_string(message.mentions, lambda a: a.mention) + " from communication..."


async def unblock(message = None, **_):
    if message is None:
        return
    remove_bots(message.mentions)
    for person in message.mentions:
        set_privilege(person, 1)
    return "Attempted to reset privileges of " + list_string(message.mentions, lambda a: a.mention) + "..."


async def op(message = None, **_):
    if message is None:
        return
    remove_bots(message.mentions)
    for person in message.mentions:
        set_privilege(person, 2)
    return "Attepted to grant level 2 op privilege to " + list_string(message.mentions, lambda a: a.mention) + "..."


async def deop(message = None, **_):
    if message is None:
        return
    remove_bots(message.mentions)
    for person in message.mentions:
        set_privilege(person, 1)
    return "Attepted to remove operator privilege from " + list_string(message.mentions, lambda a: a.mention) + "..."


async def echo(client = None, message = None, **_):
    try:
        if client:
            await client.send_message(message.channel, message.content.split(" ", 1)[1].strip())
            return
    except:
        pass # wtf how did I just learn this?
    return "What?"


async def exec(message = None, **_):
    result = "```"
    try:
        code = message.content.split(" ", 1)
        if len(code) < 2:
            return "There was no code to execute!"
        code = code[1].strip()
        if code.startswith("```Python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = """
log = kwargs["log"]
""" + code
        
        log = []
        execute(code, log = log)
        
        if len(log) == 0:
            result += "Log empty. (Remember to use log.append() instead of print().)"
        else:
            for i in range(0, len(log)):
                result += "\n" + str(log[i])
    except:
        error = exc_info()
        for e in error:
            result += "\n" + str(e)
    result += "```"
    return result


################################################################################
# Feature Testing Functions
################################################################################

import discord
async def testembed(client = None, message = None, **_):
    try:
        et = discord.Embed(title = message.content.split(" ", 1)[1], color = discord.Color.purple())
        await client.send_message(message.channel, embed = et)
    except:
        error = exc_info()
        for e in error:
            print(e)
        return "Failed"


async def test(message = None, **_):
    try:
        emoji = message.content.split(" ")[1]
        return emoji
    except:
        return "Failed!"


commands = [[["block", "blacklist"], block, "Blacklists a user or users.", "block @user1 @user2...", -1],
            [["unblock"], unblock, "Resets a user or users to normal privileges.", "unblock @user1 @user2...", -1],
            [["debug"], debug, "Turns debug mode on or off.", "debug", -1],
            [["echo"], echo, "I does a copycat.", "echo <text>", -1],
            [["exec"], exec, "Remotely executes Python 3 code. Use log.append() instead of print().", "exec <code>", -1],
            [["op"], op, "Elevates (temporarily) a user or users to level 2 operator.", "op @user1 @user2...", -1],
            [["deop"], deop, "Revokes (temp?) a user or users to normal privileges.", "deop @user1 @user2...", -1],
            [["shutdown"], fullstop, "Kills me for good.", "shutdown", -1],
            [["asdf", "adsf"], testembed, "Asdf", "asdf", -1],
            [["test"], test, "Test", "test <emoji>", -1]]


################################################################################
# Module Functions
################################################################################

def init(module = None, loadstring = None, **_):
    if module is None or loadstring is None:
        return False
    global execute
    execute = loadstring
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    module.make_primary()
    return True




