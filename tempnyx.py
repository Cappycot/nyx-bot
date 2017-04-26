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
# - Create thread locks for certain kinds of objects possibly

# Experimental Startup Parameters:
modules_folder = "modulesnew"
module_prefix = "mod"
servers_folder = "serversnew"
users_folder = "usersnew"

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
        self.has_access = None
        self.name = name
        self.names = []
        self.data = {"privilege": 1}
        if name is not None:
            self.names.append(name)
        if names is not None:
            self.names.extend(names)
            if self.name is None:
                self.name = names[0]
        for key in kwargs:
            self.data[key] = kwargs[key]
    
    @property
    def privilege(self):
        return self.data["privilege"]


class Module:
    """Holder object for a particular module that is imported into Nyx.
    The command mapping system is still a WIP.
    """
    def __init__(self, name, folder, module, **_):
        self.commands = []
        self.command_map = {}
        self.disabled = False
        self.folder = folder
        self.module = module
        self.name = name
        self.names = [name]
        self.primary = False
        self.listeners = {}
    
    
    def add_command(self, function, name=None, **kwargs):
        """Adds a command to the Module listing."""
        self.remove_command(name)
        command = Command(function, name, **kwargs)
        if command.name is None:
            return None
        self.commands.append(command)
        for name in command.names:
            self.command_map[name] = command
        # self.commands.sort(key=lambda a: a.name)
        return command
    
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
    
    
    # Listeners triggered in the Discord client will call these if
    # there exists a listener with a matching event name.
    def add_listener(self, function, name):
        """Designate a function to be called upon a certain event
        name.
        """
        self.listeners[name] = function
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
    
    
    def add_name(self, name):
        if name not in self.names:
            self.names.append(name)


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
        # Done. Now this runs in O(1) time lol.
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
    
    
    @property
    def privilege(self):
        return self.data["privilege"]
    
    
    def get_privilege(self):
        return self.data["privilege"]
    
    
    def set_privilege(self, level):
        self.data["privilege"] = level
    
    
    def has_access(self, command):
        if command.has_access is not None:
            return command.has_access(self)
        if self.privilege < 0:
            return self.privilege <= command.privilege
        elif command.privilege > 0:
            return self.privilege >= command.privilege
        else:
            return command.privilege == 0


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
        # Default command prefixes that can be overwritten...
        self.command_prefixes = ["$", "~", "!", "%", "^", "&",
                                "*", "-", "=", ".", ">", "/"]
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
        self.mention = None
        self.mention2 = None
        self.ready = False
        self.restart = False    # Option to restart after shutdown.
        self.shutdown = False
        # Don't Touch:
        self.safe_to_shutdown = False
    
    
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
        if discord_server is None:
            return None
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
        self.command_map.clear()
        self.module_map.clear()
        for module in self.modules:
            for name in module.names:
                self.module_map[name] = module
            if module.primary:
                for cmdname in module.command_map:
                    self.command_map[cmdname] = module.command_map[cmdname]
    
    
    def load_module(self, name):
        """Loads a custom Nyx module into existence."""
        module = self.get_module(name)
        try:
            if module is None:
                path = getcwd() + "/" + self.modules_folder + "/" + name
                # Add folder of module to import.
                sys.path.append(path)
                module = Module(name, path, __import__(self.mod_prefix + name
                                                        + self.mod_suffix))
                # TODO: Call init on module
                if not module.module.init(client=self, module=module):
                    return False
                self.modules.append(module)
                self.modules.sort(key=lambda a:a.name)
            elif self.debug:
                module.module = reload(module.module)
                # TODO: Call init on module
                module.commands.clear()
                module.command_map.clear()
                if not module.module.init(client=self,
                                            module=module, nyx=self):
                    return False
                module.update_command_map()
            else:
                return False
            self.update_maps()
            return True     # haha poor logical flow
        except:
            # TODO: Some error stuff
            error = sys.exc_info()
            for e in error:
                print(e)
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
            else:   # Force creation of new User object.
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
            error = sys.exc_info()
            for e in error:
                print(e)
            return False
    
    
    def load_users(self, users_folder=None):
        """asdf"""
        # Check if a specific folder is designated.
        if users_folder is not None:
            self.users_folder = users_folder
        if self.users_folder is None:
            return False
        path = getcwd() + "/" + self.users_folder + "/"
        success = True
        try:
            for usrpath in listdir(path):
                if not isfile(path + usrpath):
                    print("not file")
                    continue
                # usrpath is the id string of a user and the filename.
                success = self.load_user(str(usrpath)) and success
        except FileNotFoundError:
            mkdir(path)
        return success


########################################################################
# Client Events
########################################################################

    async def trigger(self, module, name, **kwargs):
        if self.shutdown:
            return False
        await self.client.wait_until_ready()
        if module.has_listener(name) and not await \
            module.call_listener(name, client=self.client,
                                nyx=self, **kwargs) is None:
            return True
        return False


    async def trigger_modules(self, name, server=None, **kwargs):
        if server is None:
            # TODO: Determine if all Modules should listen to DMs...
            for module in self.modules:
                await self.trigger(module, name, server=server, **kwargs)
        else:
            imports = self.get_server_data(server).modules
            for module in self.modules:
                if module.primary or module in imports:
                    await self.trigger(module, name, server=server, **kwargs)
    
    
    def connect_events(self):
        """Sets up listeners for triggering Modules for events.
        These are placed in the same order as:
        http://discordpy.readthedocs.io/en/latest/api.html
        except for the on_message event, which has its own separate
        section.
        """
        client = self.client
        
        
        @client.event
        async def on_ready():
            self.mention = self.client.user.mention
            self.mention2 = self.mention[0:2] + "!" + self.mention[2:]
            await self.trigger_modules("on_ready")
            print("on_ready")
        
        
        @client.event
        async def on_resumed():
            await self.trigger_modules("on_resumed")
        
        
        # Unknown what really is passed to on_error event??
        # For now, modules can't subscribe to it...
        @client.event
        async def on_error(event, *args, **kwargs):
            print("Error encountered! (" + str(event) + ")")
            for a in args:
                print(str(a))
            for key in kwargs:
                print(key + " - " + kwargs[key])
        
        
        # This is where on_socket_raw_receive and on_socket_raw_send
        # would be, but I don't think anyone would care.
        
        
        @client.event
        async def on_message_delete(message):
            member = None if message.server is None else message.author
            await self.trigger_modules("on_message_delete", message=message,
                            server=message.server, channel=message.channel,
                            user=message.author, member=member)
        
        
        @client.event
        async def on_message_edit(message1, message2):
            """At this point, we're throwing a lot of kwargs in and
            hoping something sticks to the wall... help.
            """
            member = None if message2.server is None else message2.author
            await self.trigger_modules("on_message_edit", message=message2,
                            server=message2.server, channel=message2.channel,
                            user=message2.author, member=member,
                            before=message1, after=message2)
        
        
        @client.event
        async def on_reaction_add(reaction, user):
            message = reaction.message
            member = None if message.server is None else user
            await self.trigger_modules("on_reaction_add", message=message,
                            server=message.server, channel=message.channel,
                            user=user, member=member, reaction=reaction,
                            emoji=reaction.emoji)
        
        @client.event
        async def on_reaction_remove(reaction, user):
            message = reaction.message
            member = None if message.server is None else user
            await self.trigger_modules("on_reaction_remove", message=message,
                            server = message.server, channel=message.channel,
                            user=user, member=member, reaction=reaction,
                            emoji=reaction.emoji)
        
        
        @client.event
        async def on_reaction_clear(message, reactions):
            message = reaction.message
            await self.trigger_modules("on_reaction_remove", message=message,
                            server=message.server, channel=message.channel,
                            reactions=reactions)
        
        
        @client.event
        async def on_channel_create(channel):
            await self.trigger_modules("on_channel_create",
                            server=channel.server, channel=channel)
        
        
        @client.event
        async def on_channel_delete(channel):
            await self.trigger_modules("on_channel_delete",
                            server=channel.server, channel=channel)
        
        
        @client.event
        async def on_channel_update(channel1, channel2):
            await self.trigger_modules("on_channel_update",
                            server=channel2.server, channel=channel2,
                            before=channel1, after=channel2)
        
        
        @client.event
        async def on_member_join(member):
            await self.trigger_modules("on_member_join", server=member.server,
                            user=member, member=member)
        
        
        @client.event
        async def on_member_remove(member):
            await self.trigger_modules("on_member_remove",
                            server=member.server, user=member, member=member)
        
        
        @client.event
        async def on_member_update(member1, member2):
            await self.trigger_modules("on_member_update",
                            server=member2.server, user=member2,
                            member=member2, before=member1, after=member2)
        
        
        @client.event
        async def on_server_join(server):
            await self.trigger_modules("on_server_join", server=server)


        @client.event
        async def on_server_remove(server):
            await self.trigger_modules("on_server_remove", server=server)


        @client.event
        async def on_server_update(server1, server2):
            await self.trigger_modules("on_server_update", server=server2,
                            before=server1, after=server2)


        @client.event
        async def on_server_role_create(role):
            await self.trigger_modules("on_server_role_create",
                            server=role.server, role=role)


        @client.event
        async def on_server_role_delete(role):
            await self.trigger_modules("on_server_role_delete",
                            server=role.server, role=role)


        @client.event
        async def on_server_role_update(role1, role2):
            await self.trigger_modules("on_server_role_delete",
                            server=role2.server, role = role2,
                            before=role1, after=role2)


        @client.event
        async def on_server_emojis_update(list1, list2):
            server = None
            if len(list1) > 0:
                server = list1[0].server
            # TODO: Confirm the theory that either list
            # has at least 1 emoji in it.
            else:
                server = list2[0].server
            await self.trigger_modules("on_server_emojis_update",
                            server=server, emojis=list2,
                            before=list1, after=list2)


        @client.event
        async def on_server_available(server):
            await self.trigger_modules("on_server_available", server=server)


        @client.event
        async def on_server_unavailable(server):
            await self.trigger_modules("on_server_unavailable", server=server)


        @client.event
        async def on_voice_state_update(member1, member2):
            await self.trigger_modules("on_voice_state_update",
                            server = member2.server, member=member2,
                            before=member1, after=member2)


        @client.event
        async def on_member_ban(member):
            await self.trigger_modules("on_member_ban", server=member.server,
                            user=member, member=member)


        @client.event
        async def on_member_unban(server, user):
            await self.trigger_modules("on_member_unban",
                            server=server, user=user)


        @client.event
        async def on_typing(channel, user, when):
            server = None if channel.is_private else channel.server
            member = None if server is None else user
            if member is not None:
                user = member
            await self.trigger_modules("on_typing", server=server,
                            channel=channel, user=user,
                            member=member, time=when)


        @client.event
        async def on_group_join(channel, user):
            await self.trigger_modules("on_group_join",
                            channel=channel, user=user)


        @client.event
        async def on_group_remove(channel, user):
            await self.trigger_modules("on_group_remove",
                            channel=channel, user=user)
        
        
########################################################################
# Main Message Event
########################################################################

        @client.event
        async def on_message(message):
            if message.author.id == client.user.id:
                return
            # TODO: Main on_message handling
            # Have all listening modules trigger on_message event.
            server = message.server
            server_data = self.get_server_data(server)
            mention = self.client.user.mention
            await self.trigger_modules("on_message", server=server,
                                                    message=message)
            
            command = False
            talk = server is None
            # Normalize message and search for module or command call.
            # If the bot client is mentioned at the beginning of the
            # message, remove the mention and the bot user from the list
            # of mentions unless the bot is mentioned more than once.
            for user in message.mentions:
                if user == self.client.user:
                    mention = user.mention
                    if message.content.startswith(user.mention):
                        talk = True
                        message.content = message.content[len(mention):] \
                                            .strip()
                    # Check for a second mention before removing user.
                    if user.mention not in message.content:
                        message.mentions.remove(user)
            
            # Check to see if command type message is in place,
            # also normalizing message by removing the prefix.
            if talk:
                for prefix in self.command_prefixes:
                    if message.content.startswith(prefix):
                        command = True
                        message.content = message.content[len(prefix):].strip()
                        break
            if server_data is not None and not command:
                for prefix in server_data.prefixes:
                    if message.content.startswith(prefix):
                        command = True
                        message.content = message.content[len(prefix):].strip()
                        break
            
            # Execute command from non-bot if command type message.
            # By this point, we have the following normalized format:
            # <command or module> <command> [param1] [param2] ...
            # e.g. unison ap stat 32 140
            # from original command @user $unison ap stat 32 140
            # oh, and also check of message.content is not empty...
            if command and message.content and not message.author.bot:
                # Priority on first keyword arg (if cmd prefix is used):
                # First: (primary) module commands (command_map)
                # Second: imported server module commands (if exists)
                # Third: individual module names
                # TODO: Change var name 'args' to understandable name?
                args = message.content.lower().split(" ")
                # Check for core commands or module names:
                command = self.command_map.get(args[0], None)
                module = self.module_map.get(args[0], None)
                
                if command is None and server_data is not None:
                    # Check for imported server commands if no core
                    # command has been found.
                    command = server_data.command_map.get(args[0], None)
                if command is None and module is not None and len(args) > 1:
                    command = module.command_map.get(args[1], None)
                
                # Execute command and send output message if exists.
                if command is not None:
                    output = None
                    user = self.get_user(message.author)
                    if user.has_access(command):
                        output = await command.function(client=self.client,
                                                    message=message,
                                                    nyx=self)
                    elif server is None:
                        output = "You do not have access to that command."
                    if output is not None:
                        output = str(output)
                        if server is not None:
                            name = message.author.nick or message.author.name
                            output = name + ", " + output
                        await client.send_message(message.channel, output)
                
                # Trigger module help event.
                elif module is not None:
                    await self.trigger(module, "help", server=server,
                                                    message=message)
            
            # If user is known to be talking to Nyx, but no bot command
            # was issued, then issue talk event to possible chat mods.
            elif talk:
                await self.trigger_modules("talk", server=server,
                                                    message=message)
            
            
########################################################################
# Main Background Clock
########################################################################

    async def clock(self):
        print("Main background clock created.")
        await self.client.wait_until_ready()
        last_minute = -1
        while not self.shutdown:
            await asyncio.sleep(1)
            dtime = datetime.now()
            if last_minute != dtime.minute:
                last_minute = dtime.minute
                #print("minute tick")
                for module in self.modules:
                    try:
                        await self.trigger(module, "clock",
                                        server=None, time=dtime)
                    except:
                        # TODO: Handle individual module clock error.
                        pass
        
        print("The system is going down now!")
        await asyncio.sleep(1)
        print("Logging out of Discord...")
        await self.client.change_presence(game = \
                                discord.Game(name = "shutdown..."),
                                            status = discord.Status.idle)
        await asyncio.sleep(1)
        print("Here's your gold. Goodbye.")
        await self.client.logout()


########################################################################
# Client Main Loop with Startup
########################################################################
# TODO: Refer to:
# http://discordpy.readthedocs.io/en/latest/migrating.html

    async def main(self):
        await self.client.login(self.token)
        await self.client.connect()

    
    def start(self):
        self.connect_events()
        self.client.loop.create_task(self.clock())
        while True:
            try:
                if not self.shutdown:
                    self.client.loop.run_until_complete(self.main())
                else:
                    self.client.loop.run_until_complete(asyncio.sleep(1))
            except KeyboardInterrupt:
                print("Killed.")
                self.shutdown = True
            except:
                if self.shutdown:
                    break
        self.client.loop.run_until_complete(self.client.logout())
        self.client.loop.close()


########################################################################
# Startup
########################################################################

line_thing = "-" * 80

def print_line():
    print(line_thing)


async def testclock():
    min_lasted = 0
    while True:
        await asyncio.sleep(60)
        min_lasted += 1
        print("Minutes survived: " + str(min_lasted))


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
    import logging
    logging.basicConfig(level=logging.INFO)
    nyx = Nyx()
    nyx.modules_folder = modules_folder
    nyx.module_prefix = module_prefix
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
    nyx.client.loop.create_task(testclock())
    nyx.start()








