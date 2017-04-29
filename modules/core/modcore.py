########################################################################
# The Heart of Nyx
########################################################################

import sys


########################################################################
# Command Functions
########################################################################

async def echo(client=None, message=None, **_):
    """Repeats whatever the user says, deleting the user's original
    message if possible in servers.
    
    Usage: $echo <text>
    """
    if client is None or message is None:
        return
    await client.send_message(message.channel,
                            message.content.split(" ", 1)[1].strip())
    if message.server is not None:
        user = message.server.get_member(client.user.id)
        if message.channel.permissions_for(user).manage_messages:
            await client.delete_message(message)
    
    
async def shutdown(client=None, message=None, nyx=None, **_):
    """Stops all bot functions by stopping the clock."""
    if client is None or message is None or nyx is None:
        return
    await client.send_message(message.channel,
                                "Light cannot be without dark!!!")
    nyx.shutdown = True


commands = [[echo, ["echo"], -1],
            [shutdown, ["shutdown"], -1]]


########################################################################
# Module Functions
########################################################################

def init(module=None, **_):
    if module is None:
        return False
    module.primary = True
    for command in commands:
        module.add_command(function=command[0],
                            names=command[1], privilege=command[2])
    return True








