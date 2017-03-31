########################################################################
# Nyx! A (Mostly Unison League themed) bot...
"""https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0"""
########################################################################
# Current Tasks:
# - Rewriting framework to have client as an object (see tempnyx.py)
#   rather than a set of global variables.
# - Conform to Python styling guidelines laid out in PEP 8.
#   (Meaning lines are <= 80 chars and comments <= 72 chars length.)
# Future Tasks:
# - Move all module code on repo to the new Nyx-Modules repo.
# - Github API for automatic code updates?


########################################################################
# Python Libraries
########################################################################

import asyncio
from datetime import datetime
import discord
from importlib import reload
from os import getcwd, listdir, mkdir
from os.path import isfile
from utilsnyx import binary_search
# TODO:
import sys


########################################################################
# Main Object Types
########################################################################

class Command:
    def __init__(self, function, names, **args):
        self.desc = None
        self.function = function
        self.name = names[0]
        self.names = names
        self.privilege = 1
        self.usage = None


class Module:
    def __init__(self, name, module, primary=False):
        self.commands = []
        # self.dir = None # removed in place of the folder variable
        self.disabled = False
        self.folder = getcwd() + "/" + mod_folder + "/" + name
        self.module = module
        self.name = name
        self.primary = primary
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
    
    # Listeners triggered in the Discord client will call these if
    # there exists a listener with a matching event name.
    def set_listener(self, function, name):
        self.listeners[name] = function
    
    def has_listener(self, name):
        return name in self.listeners
    
    async def call_listener(self, name, **kwargs):
        return await self.listeners[name](**kwargs)


class Server:
    """Class for holding preference data for Discord servers
    in terms of custom modules imported and prefixes to use.
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


########################################################################
# Main Client
########################################################################

class Nyx:
    """The main class for holding a client and its modules.
    More information later. This is a placeholder for multiline doc.
    """
    
    def __init__(self):
        self.client = discord.Client()
        self.command_map = {}
        self.modules = []
        # Hashmap of module names to module objects
        self.module_map = {}
        self.servers = []
        self.token = None
        self.users = []
        # Runtime Status
        self.debug = False
        self.ready = False
        self.shutdown = False
    
    
    def init(self, info_file=None):
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
        Returns true if the code to execute
        runs completely without error.
        This function also reroutes print statements if
        kwargs contains a list named "output".
        
        Arguments:
        code - the Python 3 code to run within self
        """
        print_holder = print # Holds built-in function print.
        successful = True
        # Reroute output accordingly.
        if "output" in kwargs and type(kwargs["output"]) is list:
            print = kwargs["output"].append
        # Attempt to run the code. See if exceptions are thrown???
        try:
            exec(code) 
        except:
            error = sys.exc_info()
            # Will tack error to whatever print is routed to.
            for e in error:
                print(e)
            successful = False
        # Not sure if this statement is necessary, but included anyway.
        print = print_holder
        return successful
    
    
    def get_module(self, name):
        """Retrieves a module by searching for their main name.
        Uses binary_search because Python's if in list is linear.
        
        Arguments:
        name - the name of the module to retrieve
        """
        to_return = binary_search(self.modules, name, lambda a: a.name)
        if to_return is not None:
            return to_return
        return None


    def load_module(name, path):
        """Loads a custom Nyx module into existence.
        If the path is not specified (None),
        then the default modules folder is used.
        
        Arguments:
        name - the primary name of the module to load or reload
        path - the file location of the module .py file 
        """
        pass
    
    
    def get_server(id):
        server = binary_search(servers, id, lambda a: a.id)
        if server is None:
            server = Server(id)
            servers.append(server)
            servers.sort(key = lambda a: a.id)
        return server


########################################################################
# Startup
########################################################################

line_thing = "-" * 80

def print_line():
    print(line_thing)


# Default startup sequence if this .py file is run.
if __name__ == "__main__":
    try: # Bypass ANSI escape sequences on output file.
        import colorama
        colorama.init()
    except:
        pass
    print_line()
    import splashnyx # Nyx art splash
    print_line()








