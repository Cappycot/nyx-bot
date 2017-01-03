################################################################################
# Nyx! A (Mostly Unison League themed) bot...
# 
# https://discordapp.com/oauth2/authorize?client_id=201425813965373440&scope=bot&permissions=0
################################################################################
# Near Goals:
# - 
# Far Goals:
# - Move main bot code to an object instance rather than within nyx.py itself.

################################################################################
# Main/Global Variables
################################################################################

command_prefixes = ["$", "~", "!", "#", "%", "-", ".", ">", "/"]
debug = True
mod_folder = "modules"
server_folder = "servers"
user_folder = "users"
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
version = "0.0.1"


################################################################################
# Python Libraries
################################################################################

import asyncio
# from datetime import datetime
import discord
# from importlib import __import__, reload
from os import getcwd, listdir, mkdir
from os.path import isfile, join
from utilsnyx import binary_search
import sys # exc_info, exit, path.append
try: # Bypass ANSI escape sequences on output file.
    import colorama
    colorama.init()
except:
    print("[WARN] Color init failed. Output may not display properly on Windows or output files...")
    
    
################################################################################
# Runtime Variables
################################################################################

client = discord.Client()
mention = None
modules = []
primary_modules = []
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
        #if any(any(module.name == b for b in a.names) for a in pmod.commands):
            print("[WARN] Collision between module " + module.name + " and primary module " + pmod.name + "...")
            return True
    return False


def is_server_admin(user, server):
    return server.default_channel.permissions_for(user).administrator


def loadstring(code, **kwargs):
    """
    Remote operate code from the Discord client...
    """
    exec(code)


def print_line():
    print("--------------------------------------------------------------------------------")


def trim(string):
    while string[-1:] == "\r" or string[-1:] == "\n":
        string = string[:-1].strip()
    return string


################################################################################
# Main Object Types
################################################################################

class Command:
    def __init__(self, function, names, **args):
        self.desc = None
        self.function = function
        self.names = names
        self.usage = None


class Module:
    def __init__(self, name, module):
        self.commands = []
        #self.dir = None
        self.disabled = False
        self.folder = getcwd() + "/" + name + "/"
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
        self.id = id
        self.privilege = 1
        self.user = None


################################################################################
# Module Functions
################################################################################

def get_module(name):
    to_return = binary_search(modules, name, lambda a: a.name)
    if not to_return is None:
        return to_return
    for module in modules:
        if any(name == a for a in module.names):
            return module
    return None


def load_module(name, path = None):
    """
    Loads a custom Nyx module into existence.
    """
    global client
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
            mod.init(module = module, loadstring = loadstring)
            modules.append(module)
            modules.sort(key = lambda a: a.name)
            for cmd in module.commands:
                print(str(cmd.names) + " - " + str(cmd.function))
            return True
        except:
            error = sys.exc_info()
            for e in error:
                print(e)
            return False
    elif debug:
        try:
            module.__init__(module.name, reload(module.module))
            module.module.init(module = module, loadstring = loadstring)
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

def load_servers():
    global server_folder
    global servers
    servers = []
    print("Loading servers...")
    folder = getcwd() + "/" + server_folder + "/"
    for entry in listdir(folder):
        data = join(folder, entry)
        if isfile(data):
            print(entry)
            server = Server(entry)
            data = open(data, "r")
            for line in data:
                line = trim(line)
                names = line.split(":", 1)[1]
                if len(names) < 2:
                    continue
                if line.startswith("modules:"):
                    names = names.split("/")
                    for name in names:
                        module = binary_search(modules, name, lambda a: a.name)
                        server.import_mod(module)
                        #print(name)
                        #print(module)
                if line.startswith("prefixes:") or line.startswith("prefix:"):
                    names = names.split(" ")
                    for name in names:
                        server.prefixes.append(name)
                        #print(name)
            servers.append(server)
    servers.sort(key = lambda a: a.id)


def save_server(server):
    if server is None:
        return False
    try:
        data = open(getcwd() + "/" + server_folder + "/" + server.id, "w")
        # Module data...
        if len(server.modules) > 0:
            data.write("modules:")
            data.write(server.modules[0].name)
            for i in range(1, len(server.modules)):
                data.write("/" + server.modules[i].name)
            data.write("\n")
        # Prefix data...
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

def find_user(person):
    return binary_search(users, person.id, lambda a: a.id)
    
def load_users():
    global users
    users = []
    print("Loading users...")
    folder = getcwd() + "/" + user_folder + "/"
    for entry in listdir(folder):
        path = join(folder, entry)
        if isfile(path):
            print(entry)
            data = open(path, "r")
            for line in data:
                if line.startswith("privilege:"):
                    try:
                        privilege = int(line.split(":")[1])
                        user = User(entry)
                        user.privilege = privilege
                        print(privilege)
                        users.append(user)
                    except:
                        continue
    users.sort(key = lambda a: a.id)

def save_user(user):
    if user is None:
        return False
    try:
        data = open(getcwd() + "/" + user_folder + "/" + user.id, "w")
        # check ur privilege
        data.write("privilege:" + str(user.privilege) + "\n")
        data.flush()
        data.close()
        return True
    except:
        return False

def add_user(person):
    user = User(person.id)
    users.append(user)
    users.sort(key = lambda a: a.id)
    save_user(user)
    return user


################################################################################
# Event Handling
################################################################################
# The head module of a server configuration handles these events first.
# Module Events:
# 

async def trigger(module, name, **kwargs):
    if module.has_listener(name) and not await module.call_listener(name, **kwargs) is None:
        print("module responded with halt")
        return True
    print("module responded with None")
    return False


async def trigger_modules(name, server = None, **kwargs):
    if server is None:
        for module in primary_modules:
            await trigger(module, name, client = client, server = server, **kwargs)
    else:
        imports = binary_search(servers, server.id, lambda a: a.id).modules
        for module in modules:
            if module in primary_modules or module in imports:
                await trigger(module, name, client = client, server = server, **kwargs)


@client.event
async def on_resumed():
    await trigger_modules("on_resumed", client = client)


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
    if message.author.bot: # TODO: Remove this after testing...
        return
    server = message.server
    if server:
        print("Message from " + str(server) + " (" + server.id + ")...")
    responded = False
    
    print("Trigger primary modules")
    for module in primary_modules:
        responded = await trigger(module, "on_message", server = server, client = client, message = message)
        
    if responded:
        return
    print("Trigger server modules")
    if message.content and server:
        server = binary_search(servers, server.id, lambda a: a.id)
        if server:
            for module in modules:
                if not module in primary_modules and module in server.modules:
                    responded = await trigger(module, "on_message", client = client, message = message)
    if responded:
        return
    
    
    # global mention
    server = message.server # temp fix
    text = message.content
    #mentioned = text.startswith(mention)
    talk = server is None or text.startswith(mention)
    if text.startswith(mention):
        text = text[len(mention):].strip()
    command = talk and any(text.startswith(a) for a in command_prefixes)
    
    print(text)
    #print("Is " + ("" if mentioned else "not ") + "a mention to Nyx.")
    print("Is " + ("" if talk else "not ") + "talking to Nyx.")
    print("Is " + ("" if command else "not ") + "a command for Nyx.")
    
    if command:
        cmdtext = text[1:].lower() # Removes whatever command symbol the message started with.
        print(cmdtext)
        execute = None
        for module in primary_modules:
            for command in module.commands:
                if any(cmdtext.startswith(a.lower()) for a in command.names):
                    execute = command.function
                    break;
            if execute:
                break
        cmdtext = cmdtext.split(" ", 1)
        if execute is None and len(cmdtext):
            for module in modules:
                if any(cmdtext[0].startswith(a) for a in module.names):
                    for command in module.commands:
                        if any(cmdtext[1].startswith(b) for b in command.names):
                            execute = command.function
                            break
                if execute:
                    message.content = cmdtext[1]
                    break
        if execute:
            print(execute)
            output = execute(client = client, message = message)
            if output:
                await client.send_message(message.channel, output)
    print_line()


################################################################################
# Background Clock
################################################################################
# Run the clock function on each module.
# Get a list of messages to send and forward all of those at once.

@client.event
async def clock():
    print("Background clock created.")
    await client.wait_until_ready()
    await client.change_presence(game = discord.Game(name = "code rewriting..."), status = discord.Status.dnd)
    print("Clock started.")
    print_line()
    while not shutdown:
        await asyncio.sleep(0.5)
        
    print("The system is going down now!")
    await asyncio.sleep(1)
    print("Logging out of Discord...")
    await client.change_presence(game = discord.Game(name = "shutdown..."), status = discord.Status.idle)
    await asyncio.sleep(1)
    print("Here's your gold. Goodbye.")
    print_line()
    await client.logout()


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
    mention = client.user.mention
    


################################################################################
# Startup
################################################################################

def start():
    print_line()
    import splash # Nyx art splash
    print_line()
    load_modules()
    load_servers()
    load_users()
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




