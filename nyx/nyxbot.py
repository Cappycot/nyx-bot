"""
Nyx! A (Mostly Unison League themed) bot...

https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0

https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

Future Tasks:
 - Rewrite task scheduling? (Clocks)
 - Add "dirty" boolean to Guild/UserData for write back optimization.
 - Conform to Python styling guidelines laid out in PEP 8.
 - Split Nyx up into Nyx and AutoShardedNyx and have original
   be NyxBase...
"""

import sys
from os import getcwd, listdir
from os.path import isfile

from discord import ClientException
from discord.ext.commands import Bot, Cog, Command, CommandError, \
    CommandNotFound, Context, GroupMixin
from discord.ext.commands.view import StringView

from nyx.nyxbase import NyxBase
from nyx.nyxhelp import DefaultNyxHelpCommand


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


class NyxBot(NyxBase, Bot):
    """An extension of the discord.py Bot class that can handle a collision
    between two commands from differing cogs with the same name if needed.
    """

    def __init__(self, command_prefix=check_prefix, default_cog_name="nyx",
                 help_command=DefaultNyxHelpCommand(),
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

        # Additional restriction to make cog commands not case-sensitive.
        self.lower_cogs = {}  # {cog name:cog} with lowercase cog names

        self.debug = False
        # Default command prefixes that can be overwritten...
        # Using '<' as a prefix is highly not recommended as '<' is the first
        # character in a Discord mention.
        self.prefixes = ["$", "~", "!", "%", "^", "&", "*", "-", "=", ",", ".",
                         ">", "/", "?"]
        # self.separate = False

        # Set the cog that is being referenced when removing a command
        # or the entire cog itself.
        self._ejecting_cog = None
        NyxBase.__init__(self, default_cog_name)
        Bot.__init__(self, command_prefix, help_command=help_command,
                     **options)

    @property
    def commands(self):
        ret = []
        for command_name in self.disambiguations.values():
            ret.extend(command_name.values())
        return set(ret)

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

        self.add_command_entry(command)

    def remove_command(self, command_name):
        command = super().remove_command(command_name)
        # We either need the command or the name and the cog.
        if command is None and self._ejecting_cog is None:
            # raise ClientException(
            # "No cog to remove the {} command from.".format(name))
            return None

        # Remove aliases from all_commands if original DNE
        # Get the command from the cog in question.
        if command is None:
            for c in self._ejecting_cog.get_commands():
                if c.name == command_name:
                    command = c
                    break
            if command is None:
                return None
            self.remove_disambiguation_command(command_name, command)
            self.remove_namespace_command(command_name, command.cog_name)
            if command_name not in command.aliases:
                for alias in command.aliases:
                    self.all_commands.pop(alias, None)
                    self.remove_disambiguation_command(alias, command)
                    self.remove_namespace_command(alias, command.cog_name)

        return command

    def remove_cog_command(self, name, cog):
        self._ejecting_cog = self.get_cog(cog)
        self.remove_command(name)
        self._ejecting_cog = None

    def walk_commands(self):
        """Uses disambiguations instead of all_commands."""
        for disambiguation in tuple(self.disambiguations.values()):
            for command in tuple(disambiguation.values()):
                yield command
                if isinstance(command, GroupMixin):
                    yield from command.walk_commands()

    async def get_context(self, message, *args, cls=Context):
        """Override latter part of context in case we actually run into
        a disambiguation.
        """
        ctx = await super().get_context(message, *args, cls=Context)
        # Make sure the current command is not part of a disambiguation with
        # multiple commands.
        if ctx.command is not None:
            disambiguation = self.get_disambiguation(ctx.invoked_with)
            if disambiguation is not None and len(disambiguation) > 1:
                ctx.command = None

        # If no command was found or a disambiguation occurred...
        if ctx.command is None and ctx.prefix is not None:
            # Attempt to grab command
            view = StringView(message.content)
            ctx.view = view
            view.skip_string(ctx.prefix)

            invoker = view.get_word().lower()
            ctx.invoked_with = invoker

            disambiguation = self.get_disambiguation(invoker)
            namespace = self.get_namespace(invoker)

            if namespace is not None:
                view.skip_ws()
                # We'll need to affix the namespace name to the prefix if we
                # get a working command to invoke.
                namespace_name = invoker
                invoker = view.get_word().lower()
                if invoker:
                    ctx.command = namespace.get(invoker)
                    ctx.invoked_with = invoker
                    ctx.prefix += namespace_name + " "
            elif disambiguation is not None:
                if len(disambiguation) == 1:
                    ctx.command = list(disambiguation.values())[0]
                elif len(disambiguation) > 1 and ctx.guild is not None:
                    ctx.command = self.get_guild_data(
                        ctx.guild).command_map.get(invoker)

        return ctx

    async def invoke(self, ctx):
        """Hook into this function for sending command errors for
        disambiguations.
        """
        if ctx.command is not None:
            await super().invoke(ctx)
        elif ctx.invoked_with:
            if self.get_disambiguation(ctx.invoked_with) is None:
                exc = CommandNotFound(
                    'Command "{}" is not found'.format(ctx.invoked_with))
            else:
                exc = CommandHasDisambiguation(
                    'Command "{}" exists in multiple cogs'.format(
                        ctx.invoked_with))
            self.dispatch("command_error", ctx, exc)
