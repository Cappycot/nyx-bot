################################################################################
# Module Command Probe
################################################################################

import asyncio
from sys import exc_info
from utilsnyx import list_string

execute = None


################################################################################
# Command Functions
################################################################################
#  - @Nyx $help [module/command keyword]


helpcode = """
global modules
global primary_modules
cmdtext = kwargs["message"].content.split(" ", 2)
result = None
server = None
if kwargs["message"].server:
    server = get_server(kwargs["message"].server.id)

prefix = command_prefixes[0]
if server and len(server.prefixes) > 0:
    prefix = server.prefixes[0]
elif server:
    prefix = client.user.mention + " " + prefix

command = None
module = None
if len(cmdtext) > 1:
    cmdcheck = []
    if server:
        for mod in server.modules:
            if not mod in primary_modules:
                cmdcheck.extend(mod.commands)
    else:
        for mod in modules:
            if cmdtext[1] == mod.name:
                module = mod
    
    if module:
        cmdcheck = module.commands
        if len(cmdtext) > 2:
            for cmd in cmdcheck:
                if any(cmdtext[2].startswith(a) for a in cmd.names):
                    command = cmd
    elif module is None:
        for mod in primary_modules:
            cmdcheck.extend(mod.commands)
        for cmd in cmdcheck:
            if any(cmdtext[1].startswith(a) for a in cmd.names):
                command = cmd

if command:
    result = command.desc if command.desc else "There is no description for this command."
    if command.usage:
        result += "\\nUsage: " + prefix + command.usage
elif module:
    pass
elif server:
    pass
else:
    pass

kwargs["result"][0] = result
"""


async def help(message = None, **_):
    result = [None]
    print("exec")
    try:
        execute(helpcode, message = message, result = result) #args = cmdtext, result = result, server = message.server)
    except:
        e = exc_info()
        for a in e:
            print(a)
    
    if result[0]:
        return result[0]
    return "This is still a work on progress... :<"


async def modules(message = None, **_):
    if message == None:
        return
    mods = []
    execute("""
if kwargs["server"]:
    server = get_server(kwargs["server"].id)
    for mod in server.modules:
        kwargs["result"].append(mod.name)
else:
    global modules
    global primary_modules
    for mod in modules:
        if mod in primary_modules:
            continue
        kwargs["result"].append(mod.name)
""", result = mods, server = message.server)

    if message.server is None:
        return "Available modules: " + list_string(mods) + "."
    else:
        if len(mods) == 0:
            return "This server has no imported mods..."
        return "This server's modules: " + list_string(mods) + "."
    

commands = [[["help"], help, "Displays syntax and usage for commands.", "help [module/command] [command]", 1],
            [["module"], modules, "Displays a list of modules.", "module", 1]]


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




