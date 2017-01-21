################################################################################
# Module Code Template
################################################################################

import asyncio

async def sample(client = None, message = None, **_):
    return "Sample text."

commands = [[["sample"], sample, "Sample text.", "sample", 1]]


################################################################################
# Module Functions
################################################################################

def init(module = None, loadstring = None, **_):
    if module is None:
        return False
    for cmd in commands:
        command = module.add_command(cmd[1], cmd[0])
        command.desc = cmd[2]
        command.usage = cmd[3]
        command.privilege = cmd[4]
    return True




