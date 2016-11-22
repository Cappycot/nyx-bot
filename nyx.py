################################################################################
# Nyx! A (Mostly Unison League themed) bot...
# 
# https://discordapp.com/oauth2/authorize?client_id=201425813965373440&scope=bot&permissions=0
################################################################################


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
from os.path import isfile
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
        if any(any(module.name == b for b in a.names) for a in pmod.commands):
            print("[WARN] Collision between module " + module.name + " and primary module " + pmod.name + "...")
            return True
    return False
        
    
def is_server_admin(user, server):
    return server.default_channel.permissions_for(user).administrator


def loadstring(code):
    """
    Remote operate code from the Discord client...
    """
    exec(code)


def print_line():
    print("--------------------------------------------------------------------------------")


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
        self.dir = None
        self.disabled = False
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
    def call_listener(self, name, **args):
        self.listeners[name](**args)
    
    def set_primary(self, primary):
        global primary_modules
        exist = binary_search(primary_modules, self.name, lambda a: a.names[0])
        if primary and exist is None:
            global modules
            primary_modules.append(self)
            primary_modules.sort(key = lambda a: a.names[0])
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
        return
    def deport_mod(self, module):
        if module in self.modules:
            self.modules.remove(module)
            return True
        return False
    def deport(self, module):
        return self.deport_mod(module)
    
    def get_server():
        global client
        


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
    module = binary_search(modules, name, lambda a: a.name)
    if module is None:
        for pmodule in primary_modules:
            if any(name == a.names[0] for a in pmodule.commands):
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
# Event Handling
################################################################################
# The head module of a server configuration handles these events first.
# Module Events:
#  - help (message)
#  - on_member_join (member)
#  - on_member_remove (member)
#  - on_message_edit (message)
#  - on_message_delete (message)

def trigger(module, name, **kwargs):
    if module.has_listener(name):
        module.call_listener(name, **kwargs)


# Primary module event.
@client.event
async def on_member_join(member):
    server = member.server
    return


# Primary module event.
@client.event
async def on_member_remove(member):
    server = member.server
    return


# Primary module event.
@client.event
async def on_message_edit(message):
    server = message.server
    return


# Primary module event.
@client.event
async def on_message_delete(message):
    server = message.server
    return


# Check primary module event then command list.
@client.event
async def on_message(message):
    server = message.server
    print(server)
    for module in primary_modules:
        trigger(module, "on_message", server = server, client = client, message = message)
    if message.content and server:
        server = binary_search(servers, server.id, lambda a: a.id)
        if server:
            for module in modules:
                if not module in primary_modules:
                    trigger(module, "on_message", client = client, message = message)
                if not message:
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
        cmdtext = text[1:].lower()
        execute = None
        for module in primary_modules:
            for command in module.commands:
                for name in command.names:
                    if cmdtext.startswith(name.lower()):
                        execute = command.function
                        break
                if execute:
                    break
            if execute:
                break
        cmdtext = cmdtext.split(" ", 1)
        if execute is None and len(cmdtext):
            for module in modules:
                if any(cmdtext[0].startswith(a) for a in module.names):
                    print("module command?")
        if execute:
            execute(client = client, message = message)
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




