########################################################################
# Nyx! A (Mostly Unison League themed) bot...
"""https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0"""
# https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU
########################################################################
# Current Tasks:
# - Rewriting framework to have client as an object.
#   rather than a set of global variables.
# - Conform to Python styling guidelines laid out in PEP 8.
#   (Meaning lines are < 80 chars and comments <= 72 chars length.)
# Future Tasks:
# - Move all module code on repo to the new Nyx-Modules repo.
# - Figure out Github API for automatic code updates?

# Experimental Startup Parameters:
modules_folder = "modules"
servers_folder = "servers"
users_folder = "users"

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
# TODO: Decide specific sys imports to use?
import sys
# TODO: kete; Setsunasa ni wa namae o tsukeyou ka "Snow halation"


########################################################################
# Main Object Types
########################################################################

class Command:
    """Holder object for a single function that originates from a
    particular module that is imported into Nyx. Command alias
    system is still a WIP.
    """
    def __init__(self, function, name, names=None, **kwargs):
        self.function = function
        self.name = name
        self.names = []
        self.data = {}
        if name is not None:
            self.names.append(name)
        if names is not None:
            self.names.extend(names)
            if name is None:
                name = names[0]
        for key in kwargs:
            data[key] = kwargs[key]


class Module:
    """Holder object for a particular module that is imported into Nyx.
    The command mapping system is still a WIP.
    """
    def __init__(self, name, folder, module=None, primary=False, **kwargs):
        self.commands = []
        self.command_map = {}
        self.disabled = False
        self.folder = folder
        self.module = module
        self.name = name
        self.primary = primary
        self.listeners = {}
    
    
    def update_command_map(self):
        """Probably-costly operation to reset the command_map and
        map each Command name to the Command itself to allow for
        O(1) time to search for a Command.
        """
        self.command_map.clear()
        for command in self.commands:
            for name in command.names:
                self.command_map[name] = command
    
    
    def remove_command(self, name):
        """Completely removes a Command from the Module listing.
        Will automatically perform a remapping of names to Commands.
        """
        remove = self.command_map.get(name, None)
        if remove is None:
            return False
        self.commands.remove(remove)
        self.update_command_map()
        return True
    
    
    def add_command(self, function, name, **kwargs):
        """Adds a command to the Module listing."""
        self.remove_command(name)
        command = Command(function, name)
        if command.name is None:
            return None
        self.commands.append(command)
        self.command_map[name] = command
        # self.commands.sort(key=lambda a: a.name)
        return command
    
    
    # Listeners triggered in the Discord client will call these if
    # there exists a listener with a matching event name.
    def set_listener(self, function, name):
        """Designate a function to be called upon a certain event
        name.
        """
        self.listeners[name] = function
    
    
    def has_listener(self, name):
        """Checks to see if event listener is designated for a name."""
        return name in self.listeners
    
    
    async def call_listener(self, name, **kwargs):
        """asdf"""
        return await self.listeners[name](**kwargs)


class ServerData:
    """Class for holding preference data for Discord servers
    in terms of custom modules imported and prefixes to use.
    """
    def __init__(self, id):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = id
        self.command_map = {}
        self.data = {}
        self.modules = []
        self.prefixes = []
    
    
    def update_command_map(self):
        """Probably-costly operation to reset the command_map and
        map each Command name to the Command itself to allow for
        O(1) time to search for a Command.
        """
        self.command_map.clear()
        for module in self.modules:
            for cmdname in module.command_map:
                self.command_map[cmdname] = module.command_map[cmdname]
    
    
    def import_mod(self, module):
        """Adds a module to the list of imported modules if it is not
        currently on the list of imported modules.
        """
        # TODO: Maybe change this to binary_search function to avoid
        # O(n^2) worst case not found time.
        if module is None or module in self.modules:
            return False
        modules.append(module)
        for cmdname in module.command_map:
            self.command_map[cmdname] = module.command_map[cmdname]
        return True
    
    
    def deport_mod(self, module):
        """Removes a module from the list of imported modules if it is
        currently on the list of imported modules.
        """
        # TODO: Maybe change this to binary_search...
        if module not in self.modules:
            return False
        self.modules.remove(module)
        self.update_command_map()
        return True
    
    
    def deport(self, module):
        """Alias for deport_mod."""
        return self.deport_mod(module)


class User:
    """Class for storing specific data for a Discord user.
    Only the user ID of a Discord User is stored between
    sessions outside of permissions and module-specific data.
    """
    def __init__(self, discord_user, id=None):
        self.data = {"privilege": 1}
        self.id = discord_user.id
        self.user = discord_user
        
    
    def get_privilege(self):
        return self.data["privilege"]
    
    
    def set_privilege(self, level):
        self.data["privilege"] = level


########################################################################
# Utility
########################################################################

def trim(string):
    """Removes all carriage returns, newlines, and spaces from the
    target string. Not sure how much this operation costs.
    """
    while string[-1:] == "\r" or string[-1:] == "\n":
        string = string[:-1].strip()
    return string


########################################################################
# Main Client
########################################################################

class Nyx:
    """The main class for holding a client and its modules.
    More information later. This is a placeholder for multiline doc.
    """
    def __init__(self):
        # TODO: Group variables in some fashion.
        self.client = discord.Client()
        self.command_map = {}
        self.modules = []
        self.modules_folder = None
        self.module_map = {}
        # Prefix and/or suffix should be used to distinguish names
        # from preexisting Python libraries.
        self.mod_prefix = "mod"
        self.mod_suffix = ""
        # TODO: May want to change "servers" to "server_data" as servers
        # typically refers to discord.Client.servers...
        self.servers = {}
        self.servers_folder = None
        self.token = None
        self.users = {}
        self.users_folder = None
        # Runtime Status
        self.debug = False
        self.ready = False
        self.restart = False
        self.shutdown = False
    
    
    def loadstring(self, code, **kwargs):
        """Remote execute code from the Discord client or other sources
        for debugging. This returns true if the code to execute runs
        completely without error. This function also reroutes print
        statements if kwargs contains a list named "output".
        
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
        """Retrieve a Module object by name."""
        if name in self.module_map:
            return self.module_map[name]
        return None
    
    
    def get_server_data(self, discord_server):
        """Retrieves the ServerData object for a particular Discord
        server. If such ServerData does not exist, then create a new
        object to hold data.
        """
        server = None
        # Since both Discord Server and ServerData have a string id
        # parameter, this will still be okay if ServerData is passed.
        if discord_server.id not in self.servers:
            server = ServerData(discord_server.id)
            self.servers[discord_server.id] = server
        else:
            server = self.servers[discord_server.id]
        return server
    
    
    def save_server_data(self, discord_server):
        """Saves a single instance of ServerData to a file in the
        specified servers folder.
        """
        server = self.get_server_data(discord_server)
        server_file = getcwd() + "/" + self.servers_folder + "/" + server.id
        try:
            data = open(server_file, "w")
            if len(server.modules > 0):
                data.write("modules:")
                data.write(server.modules[0].name)
                for i in range(1, len(server.modules)):
                    data.write("/" + server.modules[i].name)
                data.write("\n")
            if len(server.prefixes) > 0:
                data.write("prefixes:" + server.prefixes[0])
                for i in range(1, len(server.prefixes)):
                    data.write(" " + server.prefixes[i])
                data.write("\n")
            for key in server.data:
                if key is not "modules" and key is not "prefixes":
                    data.write(key + ":" + str(server.data[key]) + "\n")
            data.flush()
            data.close()
            return True
        except:
            return False
    
    
    def save_servers_data(self):
        """Attempt to save the data for all servers. Will return
        false if any (yes any lol) server fails to save properly.
        Not recommended to call this method from more than one
        module!!
        """
        return all(self.save_server_data(self, self.servers[sid])
                    for sid in self.servers)
    
    
    def get_user(self, discord_user):
        """Retrieves the User object for a particular Discord user.
        If such a User does not exist, then create a new object to
        hold data.
        """
        user = None
        if discord_user.id not in self.users:
            user = User(discord_user)
            self.users[discord_user.id] = user
        else:
            user = self.users[discord_user.id]
            # May need to update Discord User object depending on how
            # discord.py handles the uniqueness of User objects?
            # Or if we never really instantiated the object?
            if user.user.display_name is None:
                user.user = discord_user
        return user
    
    
    def save_user(self, discord_user):
        """Saves a single instance of User to a file in the
        specified users folder.
        """
        user = self.get_user(discord_user)
        user_file = getcwd() + "/" + self.users_folder + "/" + user.id
        try:
            data = open(user_file, "w")
            data.write("data:\n")
            for key in user.data:
                data.write(key + ":" + str(user.data[key]) + "\n")
            data.flush()
            data.close()
            return True
        except:
            return False
    
    
    def save_users(self):
        """Attempt to save the data for all users. Will return
        false if any (yes any lol) user fails to save properly.
        Not recommended to call this method from more than one
        module!!
        """
        success = True
        for uid in self.users:
            success = self.save_user(self, self.users[uid]) and success
        return success
    
    
    def update_maps(self):
        pass
    
    
    def load_module(self, name):
        """Loads a custom Nyx module into existence."""
        module = self.get_module(name)
        try:
            if module is None:
                path = getcwd() + "/" + self.modules_folder + "/" + name
                # Add folder of module to import.
                sys.path.append(path)
                module = Module(name, path)
                module.module = __import__(self.mod_prefix
                                            + name + self.mod_suffix)
                # TODO: Call init on module
                module.module.init(client=self, module=module)
                self.modules.append(module)
                self.modules.sort(key=lambda a:a.name)
            elif self.debug:
                module.module = reload(module.module)
                # TODO: Call init on module
                module.module.init(client=self, module=module)
            else:
                return False
            self.update_maps()
            return True # haha poor logical flow
        except:
            # TODO: Some error stuff
            return False
    
    
    def load_modules(self, modules_folder=None):
        """asdf"""
        if modules_folder is not None:
            self.modules_folder = modules_folder
        if self.modules_folder is None:
            return False
        path = getcwd() + "/" + self.modules_folder + "/"
        success = True
        for modpath in listdir(path):
            if isfile(modpath):
                continue
            mod_name = str(modpath)
            success = self.load_module(mod_name) and success
        return success
        
    
    def load_server_data(self, id):
        """asdf"""
        path = getcwd() + "/" + self.servers_folder + "/" + id
        try:
            data = open(path, "r")
            server_data = None
            if id in self.servers:
                server_data = self.servers[id]
            else:
                server_data = ServerData(id)
                self.servers[id] = server_data
            # TODO: Update ServerData data dictionary
            success = True
            for line in data:
                line = trim(line)
                args = line.split(":", 1)
                if "modules" in args[0]:
                    # TODO: code to add Modules into ServerData
                    args = args[1].split("/")
                    for modname in args:
                        module = self.get_module(modname)
                        if module is not None:
                            success = server_data.import_mod(module) \
                                        and success
                elif "prefixes" in args[0]:
                    # TODO: code to add prefixes into ServerData
                    server_data.prefixes = args[1].split(" ")
                else:
                    server_data.data[args[0]] = args[1]
            return success
        except:
            return False
    
    
    def load_servers_data(self, servers_folder=None):
        """asdf"""
        if self.servers_folder is None:
            self.servers_folder = servers_folder
        if self.servers_folder is None:
            return False
        path = getcwd() + "/" + self.servers_folder + "/"
        success = True
        for svrpath in listdir(path):
            if not isfile(svrpath):
                continue
            sid = str(svrpath)
            success = self.load_server_data(sid) and success
        return success
    
    
    def load_user(self, id):
        """asdf"""
        path = getcwd() + "/" + self.users_folder + "/" + id
        try:
            data = open(path, "r")
            # TODO: Find User data object.
            user = None
            if id in self.users:
                user = self.users[id]
            else: # Force creation of new User object.
                placeholder = discord.User()
                placeholder.id = id
                user = self.get_user(placeholder)
            # TODO: Update User data dictionary.
            for line in data:
                line = trim(line)
                if not line:
                    continue
                args = line.split(":", 1)
                if args[0] == "privilege":
                    args[1] = int(args[1])
                user.data[args[0]] = args[1]
            return True
        except:
            return False
    
    
    def load_users(self, users_folder=None):
        """asdf"""
        # Check if a specific folder is designated.
        if self.users_folder is None:
            self.users_folder = users_folder
        if self.users_folder is None:
            return False
        path = getcwd() + "/" + self.users_folder + "/"
        success = True
        try:
            for usrpath in listdir(path):
                if not isfile(usrpath):
                    continue
                uid = str(usrpath)
                success = self.load_user(uid) and success
        except FileNotFoundError:
            mkdir(path)
        return success


########################################################################
# Client Events
########################################################################

    async def trigger(self, module, name, **kwargs):
        await self.client.wait_until_ready()
        if module.has_listener(name) and not await \
            module.call_listener(name, client = self, **kwargs) is None:
            return True
        return False


    async def trigger_modules(self, name, server=None, **kwargs):
        if server is None:
            for module in self.modules:
                await self.trigger(module, name, server = server, **kwargs)
        else:
            imports = self.get_server_data(server).modules
            for module in self.modules:
                if module.primary or module in imports:
                    await self.trigger(module, name, server = server, **kwargs)
    
    
    def connect_events(self):
        """Sets up listeners for triggering Modules for events."""
        client = self.client
        
        
        @client.event
        async def on_ready():
            await self.trigger_modules("on_ready")
            print("on_ready")
        
        
########################################################################
# Main Message Event
########################################################################

        @client.event
        async def on_message(message):
            if message.author.id == client.user.id:
                return
            # TODO: Main on_message handling
            print(message.content)


########################################################################
# Client Startup
########################################################################

    def start(self):
        self.connect_events()
        self.client.run(self.token)
        print("ended")


########################################################################
# Startup
########################################################################

line_thing = "-" * 80

def print_line():
    print(line_thing)


# Default startup sequence if this .py file is run.
if __name__ == "__main__":
    # global modules_folder
    # global servers_folder
    # global users_folder
    try: # Bypass ANSI escape sequences on output file.
        import colorama
        colorama.init()
    except:
        pass
    print_line()
    import splashnyx # Nyx art splash
    print_line()
    nyx = Nyx()
    nyx.modules_folder = modules_folder
    nyx.servers_folder = servers_folder
    nyx.users_folder = users_folder
    # TODO: Temp code clear
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
    nyx.load_modules()
    nyx.load_servers_data()
    nyx.load_users()
    nyx.token = token
    nyx.start()








