################################################################################
# Unison League Discord
################################################################################

import asyncio
from importlib import reload
from sys import exc_info

module_names = ["nyxaliases", "nyxevents", "nyxreminders", "nyxmisc", "nyxnotices", "nyxspawner", "testspawner"]

folder = None
modules = [None] * len(module_names)

def load_modules(folder):
    global module_names
    global modules
    loaded = True
    for i in range(0, len(module_names)):
        name = module_names[i]
        if modules[i] is None:
            modules[i] = __import__(name)
        else:
            modules[i] = reload(modules[i])
        loaded = modules[i] and modules[i].load(folder) and loaded
    return loaded


async def reset(**_):
    global folder
    if load_modules(folder):
        return "I've finished reloading all files."
    return "Somewhere an error happened, master. >.<\nI think we should restart..."


################################################################################
# Event Functions
################################################################################

last_day = -1
last_hour = -1

async def clock(client = None, time = None, **_):
    global last_day
    global last_hour
    day = time.weekday() + 1
    hour = time.hour
    minute = time.minute
    stamp = day * 10000 + hour * 100 + minute
    for module in modules:
        try:
            await module.clock(client, time)
        except:
            print("[WARN] A Unison module was skipped over! Was it reloading?")
            e = exc_info()
            for a in e:
                print(a)
    

################################################################################
# Module Functions
################################################################################

def init(module = None, loadstring = None, **_):
    if module is None:
        return False
    global folder
    folder = module.folder
    if not load_modules(folder):
        return False
    for mod in modules:
        for cmd in mod.commands:
            command = module.add_command(cmd[1], cmd[0])
    module.add_command(reset, ["reload"])
    module.set_listener(clock, "clock")
    return True




