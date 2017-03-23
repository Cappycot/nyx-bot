################################################################################
# Nyx! A (Mostly Unison League themed) bot...
# https://discordapp.com/oauth2/authorize?client_id=201425813965373440&scope=bot&permissions=0
################################################################################
# Current Task:
# - Rewriting framework to have client as an object (line 160)
#   rather than a set of global variables.


################################################################################
# Main/Global Variables
################################################################################

command_prefixes = ["$", "~", "!", "%", "^", "&", "*", "-", "=", ".", ">", "/"]
debug = True
mod_folder = "modules"
servers_file = "servers.nyx"
users_file = "users.nyx"
mod_prefix = "mod"  # Prefix and/or suffix should be used to distinguish names
mod_suffix = ""     # from preexisting Python libraries...
token = None
try:
    info = open("info.nyx", "r")
    for line in info:
        if line.startswith("~TOKEN:"):
            token = line[7:]
            while token[-1:] == "\r" or token[-1:] == "\n":
                token = token[:-1]
except:
    print("[FATAL] Unable to find or read token in info file.")
version = "0.0.1" # We'll probably never get this past 0.0.X to be honest.


################################################################################
# Python Libraries
################################################################################

import asyncio
from datetime import datetime
import discord
from importlib import reload
from os import getcwd, listdir, mkdir
from os.path import isfile
from utilsnyx import binary_search
import sys
try: # Bypass ANSI escape sequences on output file.
    import colorama
    colorama.init()
except:
    print("[WARN] Color init failed. Output may not display properly on Windows or output files...")


################################################################################
# Main Object Types
################################################################################

class Command:
    def __init__(self, function, names, **args):
        self.desc = None
        self.function = function
        self.name = names[0]
        self.names = names
        self.privilege = 1
        self.usage = None


class Module:
    def __init__(self, name, module):
        self.commands = [] # list of Command objects this module has
        # self.dir = None # removed in place of the folder variable
        self.disabled = False
        self.folder = getcwd() + "/" + mod_folder + "/" + name
        self.module = module
        self.name = name
        self.names = [name]
        self.listeners = {}
        
    def remove_command(self, name):
        to_remove = binary_search(self.commands, name, lambda a: a.names[0])
        if to_remove is None:
            return False
        self.commands.remove(to_remove)
        return True
    def add_command(self, function, names):
        self.remove_command(names[0])
        command = Command(function, names)
        self.commands.append(command)
        self.commands.sort(key = lambda a: a.names[0])
        return command
    
    def set_listener(self, function, name):
        self.listeners[name] = function
    def has_listener(self, name):
        return name in self.listeners
    async def call_listener(self, name, **kwargs):
        return await self.listeners[name](**kwargs)
    
    def set_primary(self, primary):
        global primary_modules
        exist = binary_search(primary_modules, self.name, lambda a: a.name)
        if primary and exist is None:
            global modules
            primary_modules.append(self)
            primary_modules.sort(key = lambda a: a.name)
            index = 0
            while index < len(modules):
                if cmdcollision(modules[index], self):
                    if modules[index] in primary_modules:
                        print("[FATAL] Name collision between primary modules!")
                        sys.exit(0)
                    print("[WARN] Removing module \"" + modules[index].name + "\"...")
                    modules.remove(modules[index])
                else:
                    index += 1
        else:
            primary_modules.remove(self)
    def make_primary(self):
        self.set_primary(True)
    def remove_primary(self):
        self.set_primary(False)


class Server:
    """Class for holding preference data for Discord servers in terms of custom
    modules imported and prefixes to use.
    """
    def __init__(self, id):
        self.id = id
        self.modules = []
        self.prefixes = []
        
    def import_mod(self, module):
        if module is None:
            return False
        for mod in modules:
            for cmd in module.commands:
                if any(cmd in a.names for a in mod.commands) or cmd == mod.name:
                    return False
        self.modules.append(module)
        return True
    
    def deport_mod(self, module):
        if module in self.modules:
            self.modules.remove(module)
            return True
        return False
    def deport(self, module):
        return self.deport_mod(module)

    def get_server(self):
        global client
        client.servers.sort(key = lambda a: a.id)
        return binary_search(client.servers, self.id, lambda a: a.id)


class User:
    def __init__(self, id):
        self.data = {"privilege": 1}
        self.id = id
        self.privilege = 1


################################################################################
# Main Client
################################################################################

class Nyx:
    """The main class for holding a client and its modules.
    More information later. This is a placeholder for multiline doc.
    """
    
    def __init__(self):
        # I/O Naming
        self.mod_folder = "modules"
        self.servers_file = "servers.nyx"
        self.users_file = "users.nyx"
        self.mod_prefix = "mod" # Prefix and/or suffix should be used to distinguish names from preexisting Python libraries...
        self.mod_suffix = ""
        # Discord Server Info
        self.client = discord.Client()
        self.modules = []
        self.servers = []
        self.token = None
        self.users = []
        # Runtime Status
        self.debug = False
        self.ready = False
        self.shutdown = False
    
    
    def init(self, info_file = None):
        """Loads naming information into the object
        
        Arguments:
        info_file - path of the file to read for information
        """
        if info_file is None:
            info_file = "info.nyx"
        info = open(info_file, "r")
        return True
        
    
    
    def loadstring(self, code, **kwargs):
        """Remote execute code from the Discord client
        or other sources for debugging.
        Returns true if the code to execute runs completely without error.
        Also reroutes print statements if kwargs contains a list named "output".
        
        Arguments:
        code - the Python 3 code to run within self
        """
        print_holder = print # Holds the almightly built-in function print.
        successful = True
        if "output" in kwargs and type(kwargs["output"]) is list:
            print = kwargs["output"].append # Reroute output accordingly.
        try:
            exec(code) # Attempt to run the code. See if exceptions are thrown???
        except:
            error = sys.exc_info()
            for e in error:
                print(e) # Will tack error to whatever print is routed to.
            successful = False
        print = print_holder # This statement is probably unnecessary but I need to reassure myself here.
        return successful
    
    
    def get_module(self, name):
        """Retrieves a module by name. First tries to search for modules by
        their main name (O(logn)), but searches all modules by multiple names
        if the initial search fails. (O(n^2))
        
        Arguments:
        name - the name of the module to retrieve
        """
        to_return = binary_search(self.modules, name, lambda a: a.name)
        if not to_return is None:
            return to_return
        for module in modules:
            if any(name == a for a in module.names):
                return module
        return None


    def load_module(name, path = None):
        """Loads a custom Nyx module into existence.
        If the path is not specified (None),
        then the default modules folder is used.
        
        Arguments:
        name - the primary name of the module to load or reload
        path - the file location of the module .py file (default None)
        """
        pass
    
    
    def get_server(id):
        server = binary_search(servers, id, lambda a: a.id)
        if server is None:
            server = Server(id)
            servers.append(server)
            servers.sort(key = lambda a: a.id)
        return server


################################################################################
# Code to deprecate below...
################################################################################
# Runtime Variables
################################################################################

client = discord.Client()
mention = None
modules = []
primary_modules = [] # TODO: Remove this list and use boolean flag primary on modules.
ready = False
servers = []
shutdown = False
users = []


################################################################################
# Core Functions
################################################################################

def cmdcollision(module, *pmods):
    for pmod in pmods:
        if module == pmod:
            continue
        if any(module.name in a.names for a in pmod.commands):
            print("[WARN] Collision between module " + module.name + " and primary module " + pmod.name + "...")
            return True
    return False


def has_access(user, command):
    return user.privilege < 0 or command.privilege >= 0 and user.privilege >= command.privilege


def loadstring(code, **kwargs):
    """Remote operate code from the Discord client."""
    exec(code)


def print_line():
    print("--------------------------------------------------------------------------------")


def trim(string):
    while string[-1:] == "\r" or string[-1:] == "\n":
        string = string[:-1].strip()
    return string



################################################################################
# Module Functions
################################################################################

def get_module(name):
    to_return = binary_search(modules, name, lambda a: a.name)
    if not to_return is None:
        return to_return
    # We start with O(log2n) then devolve to O(n^2) kek...
    for module in modules:
        if any(name == a for a in module.names):
            return module
    return None


def load_module(name, path = None):
    """
    Loads a custom Nyx module into existence.
    """
    module = binary_search(modules, name, lambda a: a.name)
    if module is None:
        for pmodule in primary_modules:
            if any(name in a.names for a in pmodule.commands):
                return False
        try:
            if path is None:
                path = getcwd() + "/" + mod_folder + "/" + name
            sys.path.append(path)
            mod = __import__(mod_prefix + name + mod_suffix)
            module = Module(name, mod)
            if not mod.init(module = module, loadstring = loadstring):
                return False
            modules.append(module)
            modules.sort(key = lambda a: a.name)
            for cmd in module.commands:
                print(str(cmd.names) + " - " + str(cmd.function))
            return True
        except:
            if module in primary_modules and not module in modules:
                primary_modules.remove(module)
            error = sys.exc_info()
            for e in error:
                print(e)
            return False
    elif debug:
        try:
            print("Attempting reload.")
            modules.remove(module)
            if module in primary_modules: # TODO: Fix this crude stuff please...
                primary_modules.remove(module)
            module = Module(module.name, reload(module.module))
            module.module.init(module = module, loadstring = loadstring)
            modules.append(module)
            modules.sort(key = lambda a: a.name)
            print("Reload successful?")
            return True
        except:
            error = sys.exc_info()
            for e in error:
                print(e)
            return False
    else:
        return False


def load_modules():
    global mod_folder
    global modules
    #global primary_modules
    #modules = []
    #primary_modules = []
    print("Loading modules...")
    folder = getcwd() + "/" + mod_folder + "/"
    for modpath in listdir(folder):
        if isfile(modpath):
            continue
        mod_name = str(modpath)
        print(folder + mod_name)
        print("Module \"" + mod_name + "\" loaded " + ("successfully." if load_module(mod_name, folder + modpath) else "unsuccessfully."))
        print_line()
    return True


def unload_module(name):
    global modules
    global primary_modules
    module = binary_search(modules, name, lambda a: a.name)
    if not module is None and not module in primary_modules:
        module.disabled = True
        return True
    return False


################################################################################
# Server Functions
################################################################################

def get_server(id):
    server = binary_search(servers, id, lambda a: a.id)
    if server is None:
        server = Server(id)
        servers.append(server)
        servers.sort(key = lambda a: a.id)
    return server

def load_servers():
    global servers
    try:
        data = open(servers_file, "r")
        server = None
        for line in data:
            line = trim(line)
            names = line.split(":", 1)[1]
            if line.startswith("server:"):
                server = get_server(names)
                if server is None:
                    server = Server(names)
                    servers.append(server)
            elif line.startswith("modules:"):
                names = names.split("/")
                for name in names:
                    module = binary_search(modules, name, lambda a: a.name)
                    server.import_mod(module)
            elif line.startswith("prefixes:"):
                names = names.split(" ")
                for name in names:
                    server.prefixes.append(name)
        servers.sort(key = lambda a: a.id)
        print("Found data for " + str(len(servers)) + " server(s).")
        data.close()
        return True
    except:
        return False
    
def save_servers():
    global servers
    print("Saving " + str(len(servers)) + " server(s)...")
    try:
        data = open(servers_file, "w")
        for server in servers:
            data.write("server:" + server.id + "\n")
            if len(server.modules) > 0:
                data.write("modules:")
                data.write(server.modules[0].name)
                for i in range(1, len(server.modules)):
                    data.write("/" + server.modules[i].name)
                data.write("\n")
            if len(server.prefixes) > 0:
                data.write("prefixes:")
                data.write(server.prefixes[0])
                for i in range(1, len(server.prefixes)):
                    data.write(" " + server.prefixes[i])
                data.write("\n")
        data.flush()
        data.close()
        return True
    except:
        return False


################################################################################
# User Functions
################################################################################

def get_user(id):
    user = binary_search(users, id, lambda a: a.id)
    if user is None:
        user = User(id)
        users.append(user)
        users.sort(key = lambda a: a.id)
    return user

# Deprecated...
def find_user(person):
    return get_user(person.id)

def load_users():
    global users
    try:
        data = open(users_file, "r")
        for line in data:
            line = trim(line)
            listing = line.split(":")
            user = binary_search(users, listing[0], lambda a: a.id)
            if user is None:
                user = User(listing[0])
                users.append(user)
            user.data["privilege"] = int(listing[1])
            # TODO: Finalize this data loading...
            user.privilege = int(listing[1])
        users.sort(key = lambda a: a.id)
        print("Found data for " + str(len(users)) + " user(s).")
        data.close()
        return True
    except:
        return False

def save_users():
    global users
    print("Saving " + str(len(users)) + " user(s)...")
    try:
        data = open(users_file, "w")
        for user in users:
            data.write(user.id + ":" + str(user.privilege) + "\n")
        data.flush()
        data.close()
        return True
    except:
        ei = sys.exc_info()
        for e in ei:
            print(e)
        return False


################################################################################
# Event Handling
################################################################################

async def trigger(module, name, **kwargs):
    if client:
        await client.wait_until_ready()
    if module.has_listener(name) and not await module.call_listener(name, client = client, **kwargs) is None:
        return True
    return False


async def trigger_modules(name, server = None, **kwargs):
    if server is None:
        for module in modules:
            await trigger(module, name, server = server, **kwargs)
    else:
        imports = binary_search(servers, server.id, lambda a: a.id).modules
        for module in modules:
            if module in primary_modules or module in imports:
                await trigger(module, name, server = server, **kwargs)


@client.event
async def on_resumed():
    await trigger_modules("on_resumed")


@client.event
async def on_error(event, *args, **kwargs):
    await trigger_modules("on_error", args = args, **kwargs)


@client.event
async def on_message_delete(message):
    member = None if message.server is None else message.author
    await trigger_modules("on_message_delete", message = message, server = message.server, channel = message.channel, user = message.author, member = member)


@client.event
async def on_message_edit(message1, message2):
    member = None if message2.server is None else message2.author
    await trigger_modules("on_message_edit", message = [message1, message2], server = message2.server, channel = message2.channel, user = message2.author, member = member)


@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    member = None if message.server is None else user
    await trigger_modules("on_reaction_add", message = message, server = message.server, channel = message.channel, user = user, member = member, reaction = reaction, emoji = reaction.emoji)


@client.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    member = None if message.server is None else user
    await trigger_modules("on_reaction_remove", message = message, server = message.server, channel = message.channel, user = user, member = member, reaction = reaction, emoji = reaction.emoji)


@client.event
async def on_reaction_clear(message, reactions):
    message = reaction.message
    await trigger_modules("on_reaction_remove", message = message, server = message.server, channel = message.channel, reactions = reactions)


@client.event
async def on_channel_create(channel):
    await trigger_modules("on_channel_create", server = channel.server, channel = channel)


@client.event
async def on_channel_delete(channel):
    await trigger_modules("on_channel_delete", server = channel.server, channel = channel)


@client.event
async def on_channel_update(channel1, channel2):
    await trigger_modules("on_channel_delete", server = channel.server, channel = [channel1, channel2])


@client.event
async def on_member_join(member):
    await trigger_modules("on_member_join", server = member.server, user = member, member = member)


@client.event
async def on_member_remove(member):
    await trigger_modules("on_member_remove", server = member.server, user = member, member = member)


@client.event
async def on_member_update(member1, member2):
    await trigger_modules("on_member_update", server = member.server, user = member, member = [member1, member2])


@client.event
async def on_server_join(server):
    await trigger_modules("on_server_join", server = server)


@client.event
async def on_server_remove(server):
    await trigger_modules("on_server_remove", server = server)


@client.event
async def on_server_update(server1, server2):
    await trigger_modules("on_server_update", server = server2)
    # TODO: Change kwargs possibly...


@client.event
async def on_server_role_create(role):
    await trigger_modules("on_server_role_create", server = role.server, role = role)


@client.event
async def on_server_role_delete(role):
    await trigger_modules("on_server_role_delete", server = role.server, role = role)


@client.event
async def on_server_role_update(role1, role2):
    await trigger_modules("on_server_role_delete", server = role2.server, role = [role1, role2])


@client.event
async def on_server_emojis_update(list1, list2):
    server = None
    if len(list1) > 0:
        server = list1[0].server
    else: # TODO: Confirm the theory that either list has at least 1 emoji in it.
        server = list2[0].server
    await trigger_modules("on_server_emojis_update", server = server, emoji = [list1, list2])


@client.event
async def on_server_available(server):
    await trigger_modules("on_server_available", server = server)


@client.event
async def on_server_unavailable(server):
    await trigger_modules("on_server_unavailable", server = server)


@client.event
async def on_voice_state_update(member1, member2):
    await trigger_modules("on_voice_state_update", server = member2.server, member = [member1, member2])


@client.event
async def on_member_ban(member):
    await trigger_modules("on_member_ban", server = server, user = member, member = member)


@client.event
async def on_member_unban(server, user):
    await trigger_modules("on_member_unban", server = server, user = user)


@client.event
async def on_typing(channel, user, when):
    member = None if channel.server is None else user
    await trigger_modules("on_typing", server = channel.server, channel = channel, user = user, member = member, time = when)


@client.event
async def on_group_join(channel, user):
    await trigger_modules("on_group_join", channel = channel, user = user)


@client.event
async def on_group_remove(channel, user):
    await trigger_modules("on_group_remove", channel = channel, user = user)


################################################################################
# Message Event Handler
################################################################################

# Check primary module event then command list.
@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    server = message.server
    #if server:
        #print("Message from " + str(server) + " (" + server.id + ")...")
    #print(message.author)
    #print(message.content)
    
    responded = False
    for module in primary_modules:
        responded = await trigger(module, "on_message", server = server, message = message)
    if responded:
        return
    
    if message.content and server:
        server = binary_search(servers, server.id, lambda a: a.id)
        if server:
            for module in modules:
                if not module in primary_modules and module in server.modules:
                    responded = await trigger(module, "on_message", message = message)
    if responded:
        return
    
    # global mention
    server = message.server # temp fix
    talk = server is None or message.content.startswith(mention) or message.content.startswith(nmention)
    if message.content.startswith(mention):
        message.content = message.content[len(mention):].strip()
    elif message.content.startswith(nmention):
        message.content = message.content[len(nmention):].strip()
    command = talk and any(message.content.startswith(a) for a in command_prefixes)
    
    # TODO: Revise check for command
    if not command and server:
        server = get_server(server.id)
        command = any(message.content.startswith(a) for a in server.prefixes)
    
    
    #print("Is " + ("" if talk else "not ") + "talking to Nyx.")
    #print("Is " + ("" if command else "not ") + "a command for Nyx.")
    user = find_user(message.author)
    if user is None:
        user = add_user(message.author)
    
    if command:
        cmdtext = message.content[1:].lower() # Removes whatever command symbol the message started with.
        #print(cmdtext)
        execute = None
        
        # check primary modules
        for module in primary_modules:
            for command in module.commands:
                if any(cmdtext.startswith(a.lower()) for a in command.names):
                    #print("Found " + command.names[0])
                    execute = command
            if execute:
                break
        
        # check imported modules
        if execute is None and server:
            for module in server.modules:
                for command in module.commands:
                    if any(cmdtext.startswith(a.lower()) for a in command.names):
                        #print("Found " + command.names[0])
                        execute = command
                if execute:
                    break
        
        # check all modules
        cmdtext = cmdtext.split(" ", 1) # [0] will be possible name of module
        if execute is None and len(cmdtext):
            for module in modules:
                if any(cmdtext[0].startswith(a) for a in module.names):
                    for command in module.commands:
                        if any(cmdtext[1].startswith(b) for b in command.names):
                            #print("Found " + command.names[0])
                            execute = command
                if execute:
                    message.content = message.content.split(" ", 1)[1]
                    break
        
        # Run command.
        if execute:
            output = None
            if has_access(user, execute):
                output = await execute.function(client = client, message = message)
            elif user.privilege > 0:
                output = "You do not have access to that command."
            if output:
                if server:
                    output = message.author.mention + ", " + output
                await client.send_message(message.channel, output)


################################################################################
# Main Background Clock
################################################################################
# Run the clock function on each module.
# Get a list of messages to send and forward all of those at once.

@client.event
async def clock():
    print("Main background clock created.")
    await client.wait_until_ready()
    statuschange = False
    try:
        await client.change_presence(game = discord.Game(name = "code rewriting..."), status = discord.Status.dnd)
    except:
        print("Status write failed...")
    print("Clock started.")
    print_line()
    # TODO: Make this place neater...
    
    last_minute = -1 # Tick modules on main clock every minute.
    while not shutdown:
        await asyncio.sleep(1)
        dtime = datetime.now()
        if last_minute != dtime.minute:
            last_minute = dtime.minute
            #print("minute tick")
            await trigger_modules("clock", time = dtime)
            
            if not statuschange:
                await client.change_presence(game = discord.Game(name = "code rewriting..."), status = discord.Status.dnd)
                statuschange = True
        
    print("The system is going down now!")
    await asyncio.sleep(1)
    print("Logging out of Discord...")
    await client.change_presence(game = discord.Game(name = "shutdown..."), status = discord.Status.idle)
    await asyncio.sleep(1)
    print("Here's your gold. Goodbye.")
    await client.logout()
    if not save_servers():
        print("[FATAL] Something failed while saving servers!")
    if not save_users():
        print("[FATAL] Something failed while saving users!")
    print_line()


################################################################################
# Startup Login
################################################################################

@client.event
@asyncio.coroutine
def on_ready():
    print("Connection established.")
    print("\033[35mNyx has awoken. Only fools fear not of darkness...\033[0m")
    print("Currently serving " + str(len(client.servers)) + " servers.")
    print_line()
    # Update user data.
    global mention
    global nmention
    mention = client.user.mention
    nmention = mention[0:2] + "!" + mention[2:]
    

################################################################################
# Startup
################################################################################

def start():
    print_line()
    import splashnyx # Nyx art splash
    print_line()
    if not load_modules():
        print("[FATAL] Something failed while loading modules!")
        sys.exit(0)
    if not load_servers():
        print("[FATAL] Something failed while loading servers!")
        sys.exit(0)
    if not load_users():
        print("[FATAL] Something failed while loading users!")
        sys.exit(0)
    print_line()
    client.loop.create_task(clock())
    client.run(token)


if __name__ == "__main__":
    start()
else: # Took some prodding around just to tie up loose ends...
    try:
        client.http.session.close()
        client.close()
    except:
        print("[WARN] Unable to close extraneous client...")




