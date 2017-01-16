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
save_user(user)
    """, args = [person, level])


################################################################################
# Command Functions
################################################################################
# Root Server Commands:
#  - @Nyx $help
#  - @Nyx $block @user
#  - @Nyx $unblock @user
#  - @Nyx $debug
#  - @Nyx $echo message...
#  - @Nyx $exec
#  - @Nyx $import module, module2...
#                 list
#  - @Nyx $deport module, module2...
#  - @Nyx $deportall
#  - @Nyx $leave
#  - @Nyx $op @user
#  - @Nyx $deop @user
#  - @Nyx $shutdown

helpcode = """
sym = command_prefixes[0]
for module in modules:
""" + """
    if module in primary_modules:
        for command in module.commands:
            print(sym + " " + command.names[0])
    else:
        print(module.name)
"""

async def help(**_):
    print("----help----")
    execute(helpcode)
    print("----help----")


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


async def debug(message = None, **_):
    result = []
    execute("""
global debug
debug = not debug
kwargs["result"].append(str(debug).lower())
""", result = result)
    return "Debug mode set to " + result[0] + "."


async def echo(message = None, **_):
    try:
        return message.content.split(" ", 1)[1].strip()
    except:
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


async def import_mod(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.administrator
    if not permission:
        permission = [message.author]
        execute("""
user = find_user(kwargs["result"][0])
kwargs["result"][0] = False
if user:
    kwargs["result"][0] = user.privilege == -1
""", result = permission)
        permission = permission[0]
    if not permission:
        return "You do not have access to that command."
    modules = message.content.split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to import!"
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for name in kwargs["modules"]:
    module = get_module(name)
    if module and not module in server.modules and server.import_mod(module):
        kwargs["results"].append(name)
save_server(server)
""", modules = modules, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't import any of the modules!"
    return "Imported module(s) " + list_string(results) + "."


async def deport():
    
    return "Deported module(s) " + list_string(results) + "."


async def deport_all():
    return


async def leave(client = None, message = None, **_):
    if message is None:
        return
    elif message.server is None:
        return "I can't do that here!"
    await client.leave_server(message.server)


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


async def fullstop(**_):
    print("full stop")
    execute("""
global shutdown
shutdown = True
""")


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


async def test(**_):
    execute("""
print("Servers and Bots:")
for server in client.servers:
    print(server.name + " (" + server.id + "):")
    for user in server.members:
        if user.bot and user.game and user != client.user:
            stat = " - Bot \\\"" + user.name + "\\\":"
            for pref in command_prefixes:
                if (pref + "h") in user.game.name.lower():
                    stat += " " + pref
            print(stat)
""")
    return "Test :>"

commands = [[["help", "cmd", "command", "?"], help, "Display a list of commands.", "help", 1],
            [["block", "blacklist"], block, "Blacklists a user or users.", "block @user1 @user2...", -1],
            [["unblock"], unblock, "Resets a user or users to normal privileges.", "unblock @user1 @user2...", -1],
            [["debug"], debug, "Turns debug mode on or off.", "debug", -1],
            [["echo"], echo, "I does a copycat.", "echo <text>", -1],
            [["exec"], exec, "Remotely executes Python 3 code. Use log.append() instead of print().", "exec <code>", -1],
            [["import"], import_mod, "Imports a module into the designated server.", "import <module> [module2]", 1],
            [["leave", "die"], leave, "Leaves the designated server.", "leave", -1],
            [["op"], op, "Elevates (temporarily) a user or users to level 2 operator.", "op @user1 @user2...", -1],
            [["deop"], deop, "Revokes (temp?) a user or users to normal privileges.", "deop @user1 @user2...", -1],
            [["shutdown"], fullstop, "Kills me for good.", "shutdown", -1],
            [["asdf", "adsf"], testembed, "Asdf", "asdf", -1],
            [["test"], test, "Test", "test", -1]]


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




