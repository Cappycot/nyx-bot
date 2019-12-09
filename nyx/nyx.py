"""
Nyx! A (Mostly Unison League themed) bot...

https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0

https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

clear; python3 nyx.py &

Future Tasks:
 - Rewrite task scheduling? (Clocks)
 - Add "dirty" boolean to Guild/UserData for write back optimization.
 - Conform to Python styling guidelines laid out in PEP 8.
 - Split Nyx up into Nyx and AutoShardedNyx and have original
   be NyxBase...
"""

import sys
from contextlib import closing, redirect_stdout
from inspect import getmembers
from io import StringIO
from os import getcwd, listdir
from os.path import exists, isfile

from discord import ClientException
from discord.ext.commands import Bot, Cog, Command, CommandError, \
    CommandNotFound, Context, GroupMixin
from discord.ext.commands.bot import _is_submodule  # lol
from discord.ext.commands.view import StringView

from nyx.nyxdata import GuildData, UserData
from nyx.nyxguild import NyxGuild
# from nyx.nyxhelp import NyxHelp, NyxHelpCommand  # TODO: Work on specialized HelpCommand
from nyx.nyxuser import NyxUser


class CommandHasDisambiguation(CommandError):
    """Exception raised when a command is attempted to be invoked
    but the command exists under multiple cogs.

    This does not apply to subcommands.
    """
    pass


def check_prefix(bot, message):
    """If a guild has no specified custom prefixes, Nyx will use her mention
    appended before each of her default prefixes.
    """
    mention = bot.user.mention
    prefixes = []
    if message.guild is not None:
        mention = message.guild.get_member(bot.user.id).mention
        prefixes.extend(bot.get_guild_data(message.guild).prefixes)
    else:
        prefixes.extend(bot.prefixes)
    for prefix in bot.prefixes:
        prefixes.append(mention + " " + prefix)
    return prefixes


class Nyx(Bot):
    """An extension of the discord.py Bot class that can handle a collision
    between two commands from differing cogs with the same name if needed.
    """

    def __init__(self, command_prefix=check_prefix, default_cog="nyx",
                 **options):
        self.cogs_folder = None
        # Used to group commands by module name for easy collision resolution.
        self.command_disambiguation = options.pop("command_disambiguation",
                                                  "```{} - {}```")
        self.command_has_disambiguation = options.pop(
            "command_has_disambiguation",
            'Command "{}" exists in multiple modules as:')
        self.command_other_disambiguation = options.pop(
            "command_other_disambiguation",
            'Command "{}" also exists in other modules as:')
        self.command_no_description = options.pop("command_no_description",
                                                  "No description.")

        # self.core_commands = {}  # I don't think we'll be using this.
        self.default_cog = default_cog

        # The disambiguation table is used to look up commands of the same
        # name, distinguished by the object id.
        self.disambiguations = {}  # {command name:{object id:command}}

        # Additional restriction to make cog commands not case-sensitive.
        self.lower_cogs = {}  # {cog name:cog} with lowercase cog names

        # The namespaces table is used to look up commands by the cog name.
        self.namespaces = {}  # {cog name:{command name:command}}

        self.debug = False
        # Default command prefixes that can be overwritten...
        # Using '<' as a prefix is highly not recommended as '<' is the first
        # character in a Discord mention.
        self.prefixes = ["$", "~", "!", "%", "^", "&", "*", "-", "=", ",", ".",
                         ">", "/", "?"]
        self.separate = False
        self.guild_cog = None
        self.guild_data = {}
        self.guilds_folder = None
        self.user_cog = None
        self.user_data = {}
        self.users_folder = None
        # Set the cog that is being referenced when removing a command
        # or the entire cog itself.
        self._ejecting_cog = None
        super(Nyx, self).__init__(command_prefix, **options)

    def get_disambiguation(self, name, create=False):
        """Get the dict of cogs that have a command with such a name. This is
        case-insensitive.
        """
        name = name.lower()
        if name not in self.disambiguations:
            if not create:
                return None
            disambiguation = {}
            self.disambiguations[name] = disambiguation
            return disambiguation
        else:
            return self.disambiguations[name]

    def get_namespace(self, name, create=False):
        """Get the dict of commands from a cog of a certain name. This is case-
        insensitive.
        """
        name = name.lower()
        if name not in self.namespaces:
            if not create:
                return None
            namespace = {}
            self.namespaces[name] = namespace
            return namespace
        else:
            return self.namespaces[name]

    def add_cog(self, cog):
        if not isinstance(cog, Cog):
            raise TypeError('cogs must derive from Cog')
        # Cogs now have a more official way to get their name.
        lower_name = cog.__cog_name__.lower()
        # lower_name = type(cog).__name__.lower()
        # print(lower_name)
        if lower_name in self.lower_cogs:
            raise ClientException(
                "The cog {} is already registered.".format(lower_name))
        self.lower_cogs[lower_name] = cog
        super().add_cog(cog)

    def remove_cog(self, name):
        self._ejecting_cog = self.get_cog(name)
        super().remove_cog(name)
        self.lower_cogs.pop(name.lower(), None)
        self._ejecting_cog = None

    # TODO: Modify if needed.
    def load_cogs(self, folder=None):
        """Load extensions from a certain folder. This will add the folder to
        the sys path so we can just load extensions by the python file name.
        """
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

    def add_command(self, command):
        # Raise the usual errors from super method.
        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command')

        # Attempt to add command name to all commands dictionary.
        name = command.name.lower()
        if name in self.all_commands and not self.all_commands[name].hidden:
            del self.all_commands[name]
        else:
            self.all_commands[name] = command

        # Attempt to add command aliases to all commands dictionary.
        for alias in command.aliases:
            alias = alias.lower()
            if alias in self.all_commands:
                # and not self.all_commands[alias].hidden:
                del self.all_commands[alias]
            else:
                self.all_commands[alias] = command

        # Add as disambiguation entry.
        self.get_disambiguation(name, create=True)[id(command)] = command
        for alias in command.aliases:
            self.get_disambiguation(alias, create=True)[id(command)] = command

        # Add into cog namespace.
        cog_name = command.cog_name
        if cog_name is None:
            cog_name = self.default_cog
        namespace = self.get_namespace(cog_name, create=True)
        namespace[name] = command
        for alias in command.aliases:
            namespace[alias.lower()] = command

    def remove_command(self, name):
        command = super().remove_command(name)
        # We either need the command or the name and the cog.
        if command is None and self._ejecting_cog is None:
            # raise ClientException(
            # "No cog to remove the {} command from.".format(name))
            return None

        # Remove aliases from all_commands if original DNE
        # Get the command from the cog in question.
        if command is None:
            for c in self._ejecting_cog.get_commands():
                if c.name == name:
                    command = c
                    break
            if command is None:
                return None
            if name not in command.aliases:
                for alias in command.aliases:
                    self.all_commands.pop(alias, None)

        # Remove command and aliases from namespace
        namespace = self.get_namespace(command.cog_name)
        namespace.pop(name, None)

        # Remove command and aliases from disambiguations
        self.get_disambiguation(name).pop(id(command), None)

        if name not in command.aliases:
            for alias in command.aliases:
                namespace.pop(alias, None)
                self.get_disambiguation(alias).pop(id(command), None)

        return command

    def remove_cog_command(self, name, cog):
        self._ejecting_cog = self.get_cog(cog)
        self.remove_command(name)
        self._ejecting_cog = None

    # def reload_extension

    async def get_context(self, message, *args, cls=Context):
        return await super().get_context(message, *args, cls=Context)

    async def invoke(self, ctx):
        await super().invoke(ctx)

    # TODO: Refactor
    def get_guild_data(self, discord_guild):
        """Retrieves the GuildData object for a particular Discord Guild. If
        such GuildData does not exist, then create a new object to hold
        data. This is guaranteed to never return None unless None is passed
        as an argument.
        """
        if discord_guild is None:
            return None
        # Since both Discord Guild and GuildData have a integer id
        # parameter, this will still be okay if GuildData is passed.
        # Quack quack.
        if discord_guild.id not in self.guild_data:
            guild = GuildData(discord_guild.id)
            self.guild_data[discord_guild.id] = guild
            return guild
        else:
            return self.guild_data[discord_guild.id]

    def get_user_data(self, discord_user):
        """Retrieves the UserData object for a particular Discord User. If such
        UserData does not exist, then create a new object to hold data. This is
        guaranteed to never return None unless None is passed as an argument.
        """
        if discord_user is None:
            return None
        # Quack quack.
        if discord_user.id not in self.user_data:
            user = UserData(discord_user.id)
            self.user_data[discord_user.id] = user
        else:
            user = self.user_data[discord_user.id]
        return user
