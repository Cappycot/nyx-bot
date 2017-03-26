################################################################################
# Module Code Template
################################################################################

import asyncio
import discord


################################################################################
# Command Functions
################################################################################


statuses = {"green" : discord.Status.online, "yellow" : discord.Status.idle, "red" : discord.Status.dnd}

async def game(client = None, message = None, **_):
    try:
        args = message.content.split(" ", 2)
        title = args[2].strip().replace(client.user.mention, "@" + client.user.name)
        status = None
        for key in statuses:
            if args[1].lower().startswith(key):
                status = statuses[key]
                break
        if status is None:
            return "Specify a status color! (green/yellow/red)"
        await client.change_presence(game = discord.Game(name = title), status = status)
        return "I've changed my status to \"" + title + "\"..."
    except:
        pass # wtf how did I just learn this?
    return "What?"

commands = [[["set"], game, "Changes my Discord presence text.", "set <green/yellow/red> <text>", -1]]


################################################################################
# Event Functions
################################################################################

async def clock(client = None, time = None, **_):
    pass


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
    module.set_listener(clock, "clock")
    return True




