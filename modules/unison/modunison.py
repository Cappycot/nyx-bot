################################################################################
# Unison League Discord
################################################################################

import asyncio

import nyxaliases
import nyxevents
import nyxreminders
import nyxmisc
import nyxspawner
import testspawner
modules = [nyxaliases, nyxevents, nyxreminders, nyxmisc, nyxspawner, testspawner]

def load_modules(folder):
    global modules
    global ready
    ready = False
    loaded = True
    for module in modules:
        loaded = module.load(folder) and loaded
    ready = True
    return loaded


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
        await module.clock(client, time)
    

################################################################################
# Module Functions
################################################################################

def init(module = None, loadstring = None, **_):
    if module is None:
        return False
    folder = module.folder
    if not load_modules(folder):
        return False
    for mod in modules:
        for cmd in mod.commands:
            command = module.add_command(cmd[1], cmd[0])
    module.set_listener(clock, "clock")
    return True




