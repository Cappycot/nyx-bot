################################################################################
# Experimental Event Tracker
################################################################################

import asyncio
execute = None


################################################################################
# Event Functions
################################################################################

async def on_message_delete(client = None, message = None, **_):
    if client is None or message is None:
        return
    elif message.server is None:
        return
    await client.send_message(message.channel, "Someone deleted a message!")

async def on_message_edit(client = None, message = None, **_):
    if client is None or message is None:
        return
    elif len(message) != 2:
        return
    elif message[1].server is None:
        return
    await client.send_message(message.channel, "Someone edited a message!")

async def on_reaction_add(client = None, message = None, reaction = None, **_):
    if client is None or message is None or reaction is None:
        return
    emoji = reaction.emoji
    if reaction.custom_emoji:
        emoji = "<:" + emoji.name + ":" + emoji.id + ">"
    await client.send_message(message.channel, "Someone reacted with a " + emoji + "!")


################################################################################
# Module Functions
################################################################################

def init(module = None, **_):
    if module is None:
        return False
    module.make_primary()
    #module.set_listener(on_message_delete, "on_message_delete")
    #module.set_listener(on_message_edit, "on_message_edit")
    #module.set_listener(on_reaction_add, "on_reaction_add")
    for lis in module.listeners:
        print(lis)
    return True
