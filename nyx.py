"""
Nyx! A (Mostly Unison League themed) bot...
https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=8
https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

Current Tasks:
 - Rewrite framework to use Discord cogs and stuff...
 - Rewrite task scheduling? (Clocks)
 - Conform to Python styling guidelines laid out in PEP 8.
 - Split Nyx up into Nyx and AutoShardedNyx and have original
   be NyxBase...
Future Tasks:
 - Move all module code on repo to the new Nyx-Modules repo.
 - Figure out GitHub API for automatic code updates?
 - Create thread locks for certain kinds of objects possibly...
"""

import sys
from configparser import ConfigParser
from contextlib import closing, redirect_stdout
from io import StringIO
from os import getcwd, listdir
from os.path import isfile

from discord.ext.commands import Bot, Command, Context, GroupMixin
from discord.ext.commands.view import StringView


class GuildData:
    """Class for holding preference data for Discord guilds
    in terms of custom modules imported and prefixes to use.
    """

    def __init__(self, guild_id: int):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = guild_id
        self.command_map = {}
        self.data = {}
        self.modules = []
        self.prefixes = []


class UserData:
    """Class for storing specific data for a Discord user.
    Only the user ID of a Discord User is stored between
    sessions outside of permissions and module-specific data.
    """

    def __init__(self):
        self.data = {"privilege": 1}

    @property
    def privilege(self):
        return self.data["privilege"]

    def get_privilege(self):
        return self.data["privilege"]

    def set_privilege(self, level):
        self.data["privilege"] = level


def check_prefix(bot, message):
    """If a guild has no specified custom prefixes, Nyx will use her mention
    appended before each of her default prefixes.
    """
    if message.guild is not None:
        at_prefixes = []
        mention = message.guild.get_member(bot.user.id).mention
        for prefix in bot.prefixes:
            at_prefixes.append(mention + " " + prefix)
        guild_prefixes = bot.get_guild_data(message.guild).prefixes
        return guild_prefixes + at_prefixes
    else:
        return bot.prefixes


class Nyx(Bot):
    """An extension of Discord's Bot class that can handle a collision between
    two commands from differing cogs with the same name if needed.
    """

    def __init__(self, **kwargs):
        self.cogs_folder = None
        # Used to group commands by module name for easy collision resolution.
        self.core_commands = {}
        self.disambiguations = {}
        self.namespaces = {}
        self.owner = None
        # Default command prefixes that can be overwritten...
        self.prefixes = ["$", "~", "!", "%", "^", "&", "*", "-",
                         "=", ",", "<", ".", ">", "/", "?"]
        self.separate = False
        self.guild_data = {}
        self.guilds_folder = None
        self.user_data = {}
        self.users_folder = None
        super().__init__(command_prefix=check_prefix, **kwargs)

    def add_cog(self, cog):
        super().add_cog(cog)

    def add_command(self, command):
        # Raise the usual errors from super method.
        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command')

        if command.name not in self.all_commands:
            self.all_commands[command.name] = command
            for alias in command.aliases:
                if alias not in self.all_commands:
                    self.all_commands[alias] = command
                else:
                    del self.all_commands[alias]
        else:
            del self.all_commands[command.name]

        # Add to disambiguations...
        self.get_disambiguation(command.name, create=True)[
            id(command)] = command
        for alias in command.aliases:
            self.get_disambiguation(alias, create=True)[id(command)] = command

        # Add to namespace...
        cog_name = command.cog_name
        if cog_name is None:
            cog_name = "none"
            # If someone makes a cog named "None" they shouldn't.
        else:
            cog_name = cog_name.lower()
        namespace = self.get_namespace(cog_name, create=True)
        namespace[command.name] = command
        for alias in command.aliases:
            namespace[alias] = command

    def get_command(self, name):
        names = name.split()
        command = None
        disambiguation = self.get_disambiguation(names[0])
        namespace = self.get_namespace(names[0])
        sub_command = 1

        if disambiguation is None and namespace is None:
            return None
        elif disambiguation is not None and len(disambiguation) == 1:
            for val in disambiguation.values():
                command = val

        if command is None:
            if namespace is None or len(names) < 2:
                return None
            command = namespace.get(names[1], None)
            sub_command = 2

        if command is not None and isinstance(command, GroupMixin):
            for name in names[sub_command:]:
                try:
                    command = command.all_commands[name]
                except (AttributeError, KeyError):
                    return None
        return command

    async def get_context(self, message, *args, cls=Context):
        ctx = await super().get_context(message, *args, cls=Context)
        if ctx.command is None and ctx.prefix is not None:
            # Attempt to grab command
            view = StringView(message.content)
            ctx.view = view
            view.skip_string(ctx.prefix)

            invoker = view.get_word()
            ctx.invoked_with = invoker

            disambiguation = self.get_disambiguation(invoker)
            if disambiguation is not None:
                if len(disambiguation) == 1:
                    for val in disambiguation.values():
                        ctx.command = val
                        return ctx
                elif len(disambiguation) > 1:
                    return ctx

            namespace = self.get_namespace(invoker)
            if namespace is not None:
                view.skip_ws()
                invoker = view.get_word()
                if invoker:
                    ctx.invoked_with = invoker
                    ctx.command = namespace.get(invoker, None)
        return ctx

    def remove_cog(self, name):
        return super().remove_cog(name)

    def remove_command(self, name, cog=None):
        """Will exterminate the most recently-added command bearing the
        specified name."""
        super().remove_command(name)
        # self.all_commands has been dealt with at this point.
        disambiguation = self.get_disambiguation(name)
        if disambiguation is None:
            return None
        command = None
        for cmd in disambiguation.values():
            if cog is None or str(cog) == cmd.cog_name:
                command = cmd
        if command is not None:
            namespace = self.get_namespace(str(command.cog_name).lower())
            if namespace is None:
                return command  # Should not occur.
            disambiguation.pop(id(command))
            if len(disambiguation) == 1:
                for cmd in disambiguation.values():
                    self.all_commands[name] = cmd
            namespace.pop(name)
            if name not in command.aliases:
                for alias in command.aliases:
                    disambiguation = self.get_disambiguation(alias)
                    if disambiguation is None:
                        continue  # Should not occur.
                    disambiguation.pop(id(command))
                    if len(disambiguation) == 0:
                        del self.disambiguations[alias]
                    elif len(disambiguation) == 1:
                        for cmd in disambiguation.values():
                            self.all_commands[alias] = cmd
                    namespace.pop(alias)
        return command

    def remove_commands_named(self, name, cog=None):
        count = 0
        while self.remove_command(name, cog=cog) is not None:
            count += 1
        return count

    def walk_commands(self):
        return super().walk_commands()

    async def on_ready(self):
        print("Connection established.")
        print("\033[35mNyx has awoken. " +
              "Only fools fear not of darkness...\033[0m")
        print("Currently serving " + str(len(self.guilds)) + " guilds.")

    async def loadstring(self, code, ctx):
        """Remote execute code from the Discord client or other sources for
        debugging. This returns true if the code to execute runs completely 
        without error. This function returns a string with output.

        Arguments:
        code - the Python 3 code to run within self
        """
        with closing(StringIO()) as log:
            with redirect_stdout(log):
                try:
                    exec(code)
                # Screw your warnings, PyCharm!
                except:
                    error = sys.exc_info()
                    for e in error:
                        print(e)
            return log.getvalue()

    def get_disambiguation(self, name, create=False):
        if name not in self.disambiguations:
            if not create:
                return None
            disambiguation = {}
            self.disambiguations[name] = disambiguation
            return disambiguation
        else:
            return self.disambiguations[name]

    def get_namespace(self, name, create=False):
        if name not in self.namespaces:
            if not create:
                return None
            namespace = {}
            self.namespaces[name] = namespace
            return namespace
        else:
            return self.namespaces[name]

    def get_guild_data(self, discord_guild):
        """Retrieves the GuildData object for a particular Discord guild.
        If such GuildData does not exist, then create a new object to hold
        data.
        """
        if discord_guild is None:
            return None
        # Since both Discord Guild and GuildData have a string id
        # parameter, this will still be okay if GuildData is passed.
        # Quack quack.
        if discord_guild.id not in self.guilds:
            guild = GuildData(discord_guild.id)
            self.guild_data[discord_guild.id] = guild
            return guild
        else:
            return self.guild_data[discord_guild.id]

    def get_user_data(self, discord_user):
        if discord_user is None:
            return None
        # Quack quack.
        if discord_user.id not in self.user_data:
            user = UserData()
            self.user_data[discord_user.id] = user
        else:
            user = self.user_data[discord_user.id]
        return user

    def load_cogs(self, folder=None):
        if folder is not None:
            self.cogs_folder = folder
        if self.cogs_folder is None:
            return False
        path = getcwd() + "/" + self.cogs_folder + "/"
        print(path)
        sys.path.append(path)
        for mod_path in listdir(path):
            if not isfile(path + mod_path):
                continue
            if mod_path.endswith(".py"):
                self.load_extension(mod_path[:-3])
        return True

    def load_guild_data(self, folder=None):
        if folder is not None:
            self.guilds_folder = folder
        if self.guilds_folder is None:
            return False
        config = ConfigParser()
        path = getcwd() + "/" + self.guilds_folder + "/"
        for guild_path in path:
            if not isfile(path + guild_path):
                continue
            try:
                guild_data = GuildData(int(guild_path))
            except ValueError:
                continue
            with open(path + guild_path) as file:
                config.read_file(file)
                if "Settings" in config:
                    settings = config["Settings"]
                    if "Modules" in settings:
                        guild_data.modules.extend(
                            settings["Modules"].split(" "))
                    if "Prefixes" in settings:
                        guild_data.prefixes.extend(
                            settings["Prefixes"].split(" "))
                if "Data" in config:
                    data = config["Data"]
                    for key in data:
                        guild_data.data[key] = data.get(key, None)
        return True

    def load_user_data(self, folder=None):
        pass

    def save_guild_data(self, guild_data, folder=None):
        pass

    def save_all_guild_data(self, folder=None):
        pass

    def save_user_data(self, user_data, folder=None):
        pass

    def save_all_user_data(self, folder=None):
        pass


def bot_is_nyx(ctx):
    """Hopefully no one else names their bot subclass Nyx..."""
    return type(ctx.bot).__name__ == Nyx.__name__


if __name__ == "__main__":
    nyx = Nyx()

    nyx.load_cogs("cogs")


    @nyx.command()
    async def asdf(ctx):
        await ctx.send("fdsa")


    nyx_config = ConfigParser()
    nyx_config.read("info.nyx")

    if "Settings" not in nyx_config:
        print("Settings not found. Configure your file.")
    elif "Token" not in nyx_config["Settings"]:
        print("Token setting not found. Configure your file.")
    else:
        nyx.run(nyx_config["Settings"]["Token"])
