########################################################################
# Dynamic Nyx Module Loader
########################################################################

from nyxutils import list_string


########################################################################
# Command Functions
########################################################################
#  - @Nyx $load modulename
#  - @Nyx $unload module


async def load(message=None, nyx=None, **_):
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to (re)load!"
    results = []
    for name in modules:
        if nyx.load_module(name):
            results.append(name)
    if len(results) == 0:
        return "I couldn't (re)load any of the modules!"
    nyx.update_maps()
    return "I've (re)loaded " + list_string(results) + "."


async def unload(**_):
    return "I can't really do that."


commands = [[load, ["load", "reload"], -1],
            [unload, ["unload"], -1]]


########################################################################
# Module Functions
########################################################################

def init(module=None, **_):
    if module is None:
        return False
    for command in commands:
        module.add_command(function=command[0],
                            names=command[1], privilege=command[2])
    return True
