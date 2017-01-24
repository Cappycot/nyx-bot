################################################################################
# Module Command Probe
################################################################################

import asyncio

execute = None

################################################################################
# Command Functions
################################################################################
#  - @Nyx $help [module/command keyword]


async def help(message = None, **_):
    return "Sample text."


commands = [[["help"], help, "Sample text.", "sample", 1]]


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




