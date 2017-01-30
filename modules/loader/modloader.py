################################################################################
# Nyx's Module Loader/Unloader
################################################################################

import asyncio
from utilsnyx import list_string

execute = None


################################################################################
# Command Functions
################################################################################
#  - @Nyx $load modulename
#  - @Nyx $unload module


async def load(message = None, **_):
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to load/reload!"
    results = []
    execute("""
for name in kwargs["modules"]:
    if load_module(name):
        kwargs["results"].append(name)
""", modules = modules, results = results)
    if len(results) == 0:
        return "I couldn't load/reload any of the modules!"
    return "I've loaded/reloaded " + list_string(results) + "."


async def unload(message = None, **_):
    print("unload")
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to unload!"
    results = []
    #execute("""

#""", modules = modules, results = results)
    if len(results) == 0:
        return "I couldn't unload any of the modules!"
    return "I've unloaded " + list_string(results) + "."


commands = [[["load"], load, "Loads/Reloads a Nyx module from Python files.", "load <module> [module2]", -1],
            [["unload"], unload, "Unloads a Nyx module from the modules list.", "unload <module> [module2]", -1]]


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




