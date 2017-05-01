########################################################################
# Nyx's Server-related Functions
########################################################################

from nyxutils import list_string


########################################################################
# Command Functions
########################################################################
#  - @Nyx $import module, module2...
#                 list
#  - @Nyx $deport module, module2...
#  - @Nyx $deportall
#  - @Nyx $prefix
#  - @Nyx $prefixadd/prefixrem symbol1, symbol2...
#  - @Nyx $leave


async def import_mod(message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    elif nyx is None:
        return "Something went wrong!"
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to import!"
    results = []
    server_data = nyx.get_server_data(message.server)
    for name in modules:
        module = nyx.get_module(name)
        if module is not None:
            if server_data.import_mod(module):
                results.append(name)
    if len(results) == 0:
        return "I couldn't import any of the modules!"
    return "Imported module(s) " + list_string(results) + "."


async def deport_mod(message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    elif nyx is None:
        return "Something went wrong!"
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to import!"
    results = []
    server_data = nyx.get_server_data(message.server)
    for name in modules:
        module = nyx.get_module(name)
        if module is not None:
            if server_data.deport_mod(module):
                results.append(name)
    if len(results) == 0:
        if "mexicans" in modules:
            return "I was not able to build a wall..."
        return "I couldn't deport any of the modules!"
    server_data.update_command_map()
    return "Deported module(s) " + list_string(results) + "."


async def deport_all(message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    results = []
    server_data = nyx.get_server_data(message.server)
    for module in server_data.modules:
        results.append(module.name)
    server_data.modules.clear()
    if len(results) == 0:
        return "There was nothing to deport!"
    return "Deported module(s) " + list_string(results) + "."


async def prefix(client=None, message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    server_data = nyx.get_server_data(message.server)
    if len(server_data.prefixes) == 0:
        return "This server has no prefixes... Use ``" + \
                client.user.mention + " $prefixadd <symbol>`` to add some."
    return "Prefixes for this server are " + list_string(server_data.prefixes,
                                                key=lambda a: "'" + a + "'")


async def prefixadd(message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    prefixes = message.content.lower().split(" ")[1:]
    results = []
    server_data = nyx.get_server_data(message.server)
    for prefix in prefixes:
        if len(prefix) < 4 and prefix not in server_data.prefixes:
            results.append(prefix)
            server_data.prefixes.append(prefix)
    if len(results) == 0:
        return "I couldn't add any of the prefixes! " + \
                "(Either invalid or added already.)"
    return "Added prefix(es) " + list_string(results,
                                                key=lambda a: "'" + a + "'")


async def prefixremove(message=None, nyx=None, **_):
    if message.server is None:
        return "This can't be done here!"
    prefixes = message.content.lower().split(" ")[1:]
    results = []
    server_data = nyx.get_server_data(message.server)
    for prefix in prefixes:
        if prefix in server_data.prefixes:
            results.append(prefix)
            server_data.prefixes.remove(prefix)
    if len(results) == 0:
        return "I couldn't find such a prefix to remove!"
    return "Removed prefix(es) " + list_string(results,
                                                key=lambda a: "'" + a + "'")


async def leave(client=None, message=None, **_):
    if message.server is None:
        return "I can't do that here!"
    await client.leave_server(message.server)


########################################################################
# Listener Functions
########################################################################

async def help(server=server, client=client, **_):
    pass


async def on_server_join(server=server, client=client, nyx=nyx, **_):
    pass


########################################################################
# Module Functions
########################################################################

def init(module=None, **_):
    if module is None:
        return False
    
    return True








