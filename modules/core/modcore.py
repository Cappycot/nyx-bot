########################################################################
# The Heart of Nyx
########################################################################

from nyxutils import print_line
import sys


########################################################################
# Command Functions
########################################################################
# Root Server Commands:
#  - @Nyx $debug
#  - @Nyx $echo message...
#  - @Nyx $exec
#  - @Nyx $shutdown


async def debug(nyx=None, **_):
    """Toggles debug on and off.
    
Usage: $debug
    """
    nyx.debug = not nyx.debug
    return "Debug mode set to " + str(nyx.debug) + "."
    
    
async def echo(client=None, message=None, **_):
    """Repeats whatever the user says, deleting the user's original
message if possible in servers.
    
Usage: $echo <text>
    """
    await client.send_message(message.channel,
                            message.content.split(" ", 1)[1].strip())
    if message.server is not None:
        user = message.server.get_member(client.user.id)
        if message.channel.permissions_for(user).manage_messages:
            await client.delete_message(message)
    
    
async def execute(client=None, message=None, nyx=None, **_):
    """Remotely executes Python 3 code from a Discord user.
    
Usage: $exec <code>
    """
    result = "```"
    try:
        code = message.content.split(" ", 1)
        if len(code) < 2:
            return "There was no code to execute!"
        code = code[1].strip()
        if code.startswith("```Python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        log = []
        nyx.loadstring(code, output=log)
        
        if len(log) == 0:
            result += "No output."
        else:
            result += log[0]
            # for i in range(0, len(log)):
                # result += "\n" + str(log[i])
    except:
        error = exc_info()
        for e in error:
            result += "\n" + str(e)
    result += "```"
    return result
    
    
async def shutdown(client=None, message=None, nyx=None, **_):
    """Stops all bot functions by stopping the clock.
    
Usage: $shutdown
    """
    await client.send_message(message.channel,
                                "Light cannot be without dark!!!")
    nyx.shutdown = True


commands = [[debug, ["debug"], -1],
            [echo, ["echo"], -1],
            [execute, ["exec"], -1],
            [shutdown, ["shutdown"], -1]]


########################################################################
# Listener Functions
########################################################################

async def on_ready(client=None, **_):
    print("Connection established.")
    print("\033[35mNyx has awoken. Only fools fear not of darkness...\033[0m")
    if client is not None:
        print("Currently serving " + str(len(client.servers)) + " servers.")
    print_line()


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
    module.add_listener(on_ready, "on_ready")
    return True








