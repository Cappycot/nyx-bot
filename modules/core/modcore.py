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
#  - @Nyx $import module, module2...
#                 list
#  - @Nyx $deport module, module2...
#  - @Nyx $deportall
#  - @Nyx $prefix
#  - @Nyx $prefixadd/prefixrem symbol1, symbol2...
#  - @Nyx $leave
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
        await client.send_message(message.channel, "Goodbye...")
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
# Server Management Functions
################################################################################

async def import_mod(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to import!"
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for name in kwargs["modules"]:
    module = get_module(name)
    if module and not module in server.modules and server.import_mod(module):
        kwargs["results"].append(name)
""", modules = modules, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't import any of the modules!"
    return "Imported module(s) " + list_string(results) + "."


async def deport(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to deport!"
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for name in kwargs["modules"]:
    module = get_module(name)
    if module and module in server.modules and server.deport_mod(module):
        kwargs["results"].append(name)
""", modules = modules, results = results, server = message.server)
    if len(results) == 0:
        if "mexico" in modules:
            return "I was not able to build a wall..."
        return "I couldn't deport any of the modules!"
    return "Deported module(s) " + list_string(results) + "."


async def deport_all(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for module in server.modules:
    if server.deport_mod(module):
        kwargs["results"].append(module.name)
""", results = results, server = message.server)
    if len(results) == 0:
        return "There was nothing to deport!"
    return "Deported module(s) " + list_string(results) + "."


async def prefix(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
kwargs["results"].extend(server.prefixes)
""", results = results, server = message.server)
    if len(results) == 0:
        return "This server has no prefixes... Use \"@Mary $prefixadd <symbol>\" to add some."
    return "Prefixes for this server are " + list_string(results, key = lambda a: "'" + a + "'")


async def prefixadd(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    if not (message.author.server_permissions.manage_server or get_privilege(message.author) == -1):
        return "You do not have access to that command."
    prefixes = message.content.lower().split(" ")[1:]
    if len(prefixes) == 0:
        return "You didn't tell me what prefixes to add!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
for prefix in kwargs["prefixes"]:
    if prefix in command_prefixes and not prefix in server.prefixes:
        server.prefixes.append(prefix)
        kwargs["results"].append(prefix)
""", prefixes = prefixes, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't add any of the prefixes! (Either invalid or added already.)"
    return "Added prefix(es) " + list_string(results, key = lambda a: "'" + a + "'")


async def prefixremove(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    if not (message.author.server_permissions.manage_server or get_privilege(message.author) == -1):
        return "You do not have access to that command."
    prefixes = message.content.lower().split(" ")[1:]
    if len(prefixes) == 0:
        return "You didn't tell me what prefixes to remove!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
for prefix in kwargs["prefixes"]:
    if prefix in server.prefixes:
        server.prefixes.remove(prefix)
        kwargs["results"].append(prefix)
""", prefixes = prefixes, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't find such a prefix to remove!"
    return "Removed prefix(es) " + list_string(results, key = lambda a: "'" + a + "'")


async def leave(client = None, message = None, **_):
    if message is None:
        return
    elif message.server is None:
        return "I can't do that here!"
    await client.leave_server(message.server)


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
            [["import"], import_mod, "Imports a module into the designated server.", "import <module> [module2]", 1],
            [["deportall"], deport_all, "Deports all modules from the designated server.", "deportall", 1],
            [["deport"], deport, "Deports a module from the designated server.", "deport <module> [module2]", 1],
            [["prefix"], prefix, "Gets a list of prefixes for the designated server.", "prefix", 1],
            [["prefixadd", "addprefix"], prefixadd, "Adds a prefix to the designated server.", "prefixadd <symbol> [symbol2]", 1],
            [["prefixrem", "removeprefix"], prefixremove, "Removes a prefix from the designated server.", "prefixrem <symbol> [symbol2]", 1],
            [["leave", "die"], leave, "Leaves the designated server.", "leave", -1],
            [["op"], op, "Elevates (temporarily) a user or users to level 2 operator.", "op @user1 @user2...", -1],
            [["deop"], deop, "Revokes (temp?) a user or users to normal privileges.", "deop @user1 @user2...", -1],
            [["shutdown"], fullstop, "Kills me for good.", "shutdown", -1],
            [["asdf", "adsf"], testembed, "Asdf", "asdf", -1],
            [["test"], test, "Test", "test <emoji>", -1]]


################################################################################
# Event Functions
################################################################################

async def on_message(client = None, message = None, **_): # lmao at the "**_" part
    if client is None or message is None:
        return
    print("Message from " + str(message.author.id) + ": " + message.content)


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
    module.set_listener(on_message, "on_message")
    module.make_primary()
    return True




