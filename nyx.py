# Nyx! A (Mostly Unison League themed) bot...
# 
# https://discordapp.com/oauth2/authorize?client_id=201425813965373440&scope=bot&permissions=0
# My ID: <@201425862757842944>

# Python Libraries
import asyncio
# from datetime import datetime
import discord
# from importlib import __import__, reload
from utilsnyx import binary_search
import sys # exit, path.append
try: # Bypass ANSI escape sequences on output file.
    import colorama
    colorama.init()
except:
    print("Color init failed. Output may not display properly on Windows or output files...")


################################################################################
# Main/Global Variables
################################################################################

data_file = "info.nyx"
debug = True
admins = []
block = [] # Admin and operator lists override blacklist
operators = []
modules = []
servers = []
client = discord.Client()
default_prefix = "@ ~"
version = "0.0.1"


################################################################################
# Server Package Setup
################################################################################

class Command:
    def __init__(self, function, *names):
        self.function = function
        self.names = names
        
class Module:
    def __init__(self, name, filepath, mod):
        self.filepath = filepath
        self.mod = mod
        self.name = name
        self.commands = []
        self.listeners = {}
    def set_listener(self, name, function):
        self.listeners[name] = function
    def has_listener(self, name):
        return name in self.listeners
    def call_listener(self, name, *args):
        self.listeners[name](*args)

class Server:
    def __init__(self):
        self.prefixes = []
        self.modules = []
        return

class User:
    def __init__(self):
        return


################################################################################
# Utility Functions
################################################################################

def is_admin(id):
    return any(admin == id for admin in admins)
    
def is_operator(id):
    return is_admin or any(admin == id for admin in operators)

def is_server_admin(user, server):
    if is_operator(user.id):
        return True
    elif server is None:
        return False
    return server.default_channel.permissions_for(user).administrator

def print_line():
    print("--------------------------------------------------------------------------------")

def get_module(pyname):
    return binary_search(modules, pyname, lambda a: a.name)
    
def load_module(dirname, pyname):
    filepath = os.getcwd() + "/" + dirname
    sys.path.append(filepath)
    mod = __import__(pyname)
    
    return
    
    
################################################################################
# Background Clock
################################################################################
# Run the clock function on each module.
# Get a list of messages to send and forward all of those at once.

@client.event
async def clock():
    return


################################################################################
# Startup Login
################################################################################

@client.event
@asyncio.coroutine
def on_ready():
    print("Connection established.")
    print("\033[35mNyx has awoken. \"Only fools fear not of darkness...\"\033[0m")
    print("Currently serving " + str(len(client.servers)) + " servers.")
    print_line()
    
    
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

def trigger(name, server, *args):
    return

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


################################################################################
# Message (Event) Handling, triggers all modules by check
################################################################################
# Root Server Commands:
#  - @Nyx ~help
#  - @Nyx ~block @user
#  - @Nyx ~unblock @user
#  - @Nyx ~debug
#  - @Nyx ~echo message...
#  - @Nyx ~exec
#  - @Nyx ~import module, module2...
#                 list
#  - @Nyx ~deport module, module2...
#  - @Nyx ~deportall
#  - @Nyx ~leave
#  - @Nyx ~op @user
#  - @Nyx ~deop @user
#  - @Nyx ~shutdown
    
@client.event
async def on_message(message):
    return


################################################################################
# Startup?
################################################################################

print_line()
import splash # Nyx art splash
print_line()
client.loop.create_task(clock())
# client.run(token)









