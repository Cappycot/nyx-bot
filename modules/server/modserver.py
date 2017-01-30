################################################################################
# Nyx's Server Management
################################################################################

import asyncio
from utilsnyx import list_string

execute = None


################################################################################
# Core Functions
################################################################################

def get_privilege(person):
    level = [1]
    execute("""
person = kwargs["person"]
user = find_user(person)
if not user is None:
    kwargs["level"][0] = user.privilege
    """, person = person, level = level)
    return level[0]
    
def set_privilege(person, level):
    if level < 0:
        level = 1
    execute("""
person = kwargs["args"][0]
user = find_user(person)
if user is None:
    user = add_user(person)
privilege = kwargs["args"][1]
if user.privilege > 0 and privilege == 1 or user.privilege >= 0 and privilege != 1:
    user.privilege = privilege
    """, args = [person, level])


################################################################################
# Command Functions
################################################################################
#  - @Nyx $import module, module2...
#                 list
#  - @Nyx $deport module, module2...
#  - @Nyx $deportall
#  - @Nyx $prefix
#  - @Nyx $prefixadd/prefixrem symbol1, symbol2...
#  - @Nyx $leave


async def import_mod(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to import!"
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for name in kwargs["modules"]:
    module = get_module(name)
    if module and not module in server.modules and server.import_mod(module):
        kwargs["results"].append(name)
""", modules = modules, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't import any of the modules!"
    return "Imported module(s) " + list_string(results) + "."


async def deport(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    modules = message.content.lower().split(" ")[1:]
    if len(modules) == 0:
        return "You didn't tell me what modules to deport!"
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for name in kwargs["modules"]:
    module = get_module(name)
    if module and module in server.modules and server.deport_mod(module):
        kwargs["results"].append(name)
""", modules = modules, results = results, server = message.server)
    if len(results) == 0:
        if "mexico" in modules:
            return "I was not able to build a wall..."
        return "I couldn't deport any of the modules!"
    return "Deported module(s) " + list_string(results) + "."


async def deport_all(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    permission = message.author.server_permissions.manage_server or get_privilege(message.author) == -1
    if not permission:
        return "You do not have access to that command."
    results = []
    execute("""
server = binary_search(servers, kwargs["server"].id, lambda a: a.id)
for module in server.modules:
    if server.deport_mod(module):
        kwargs["results"].append(module.name)
""", results = results, server = message.server)
    if len(results) == 0:
        return "There was nothing to deport!"
    return "Deported module(s) " + list_string(results) + "."


async def prefix(client = None, message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
kwargs["results"].extend(server.prefixes)
""", results = results, server = message.server)
    if len(results) == 0 and client:
        return "This server has no prefixes... Use \"" + client.user.mention + " $prefixadd <symbol>\" to add some."
    elif len(results) == 0:
        return "This server has no prefixes..."
    return "Prefixes for this server are " + list_string(results, key = lambda a: "'" + a + "'")


async def prefixadd(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    if not (message.author.server_permissions.manage_server or get_privilege(message.author) == -1):
        return "You do not have access to that command."
    prefixes = message.content.lower().split(" ")[1:]
    if len(prefixes) == 0:
        return "You didn't tell me what prefixes to add!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
for prefix in kwargs["prefixes"]:
    if prefix in command_prefixes and not prefix in server.prefixes:
        server.prefixes.append(prefix)
        kwargs["results"].append(prefix)
""", prefixes = prefixes, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't add any of the prefixes! (Either invalid or added already.)"
    return "Added prefix(es) " + list_string(results, key = lambda a: "'" + a + "'")


async def prefixremove(message = None, **_):
    if message.server is None:
        return "This can't be done here!"
    if not (message.author.server_permissions.manage_server or get_privilege(message.author) == -1):
        return "You do not have access to that command."
    prefixes = message.content.lower().split(" ")[1:]
    if len(prefixes) == 0:
        return "You didn't tell me what prefixes to remove!"
    results = []
    execute("""
server = get_server(kwargs["server"].id)
for prefix in kwargs["prefixes"]:
    if prefix in server.prefixes:
        server.prefixes.remove(prefix)
        kwargs["results"].append(prefix)
""", prefixes = prefixes, results = results, server = message.server)
    if len(results) == 0:
        return "I couldn't find such a prefix to remove!"
    return "Removed prefix(es) " + list_string(results, key = lambda a: "'" + a + "'")


async def leave(client = None, message = None, **_):
    if message is None:
        return
    elif message.server is None:
        return "I can't do that here!"
    await client.leave_server(message.server)


commands = [[["import"], import_mod, "Imports a module into the current server.", "import <module> [module2]", 1],
            [["deportall"], deport_all, "Deports all modules from the current server.", "deportall", 1],
            [["deport"], deport, "Deports a module from the current server.", "deport <module> [module2]", 1],
            [["prefix"], prefix, "Gets a list of prefixes for the current server.", "prefix", 1],
            [["prefixadd", "addprefix"], prefixadd, "Adds a prefix to the current server.", "prefixadd <symbol> [symbol2]", 1],
            [["prefixrem", "removeprefix"], prefixremove, "Removes a prefix from the current server.", "prefixrem <symbol> [symbol2]", 1],
            [["leave", "die"], leave, "Leaves the current server.", "leave", -1]]


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




