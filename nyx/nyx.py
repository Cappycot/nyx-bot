"""
Nyx! A (Mostly Unison League themed) bot...

https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0

https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

clear; python3 nyx.py &

Current Tasks:
 - Adapt Nyx to be something we can install with pip
 - Rewrite task scheduling? (Clocks)
 - Add "dirty" boolean to Guild/UserData for write back optimization.
 - Conform to Python styling guidelines laid out in PEP 8.
Future Tasks:
 - Split Nyx up into Nyx and AutoShardedNyx and have original
   be NyxBase...
"""

import sys
from contextlib import closing, redirect_stdout
from inspect import getmembers
from io import StringIO
from os import getcwd, listdir
from os.path import isfile

from discord import ClientException
from discord.ext.commands import Bot, Command, CommandError, CommandNotFound, \
    Context, GroupMixin
from discord.ext.commands.bot import _is_submodule  # lol
from discord.ext.commands.view import StringView

from nyx.nyxcommands import is_module_exclusive
from nyx.nyxdata import GuildData, UserData
from nyx.nyxguild import NyxGuild
from nyx.nyxhelp import NyxHelp, NyxHelpFormatter


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

    def __init__(self, **options):
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
        self.core_commands = {}
        self.disambiguations = {}  # {command name:{object id:command}}
        self.lower_cogs = {}
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
        self.user_data = {}
        self.users_folder = None
        super(Nyx, self).__init__(command_prefix=check_prefix,
                                  formatter=NyxHelpFormatter(), **options)
        self.remove_command("help")
        self.guild_cog = NyxGuild(self)
        self.add_cog(self.guild_cog)
        self.add_cog(NyxHelp(self))
        # self.add_cog(User(self))

    def add_cog(self, cog):
        """At the moment we're overriding this to have a dict of all the cogs
        based on their lowercase names. I am not sure what we'll be doing with
        this dict, but it'll be kept here for now.
        """
        lower_name = type(cog).__name__.lower()
        if lower_name in self.lower_cogs:
            raise ClientException(
                "The cog {} is already registered.".format(lower_name))
        self.lower_cogs[lower_name] = cog
        super().add_cog(cog)

    def reload_extension(self, name):
        """Simply unload and load the extension again. If a cog is specified
        rather than an extension, search for the extension that is its parent.
        If both a cog and extension share the same name, the extension will
        take priority.
        """
        if self.extensions.get(name) is None:
            cog = self.lower_cogs.get(name.lower(), None)
            if cog is None:
                return False
            else:
                name = None
                for lib in self.extensions:
                    if _is_submodule(self.extensions[lib].__name__,
                                     cog.__module__):
                        name = lib
                if name is None:
                    return False
        self.unload_extension(name)
        self.load_extension(name)
        return True

    def add_command(self, command):
        # Raise the usual errors from super method.
        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command')

        # If there is already said name/alias occupying the main commands,
        # then remove it and leave it to be handled by disambiguation.
        name = command.name.lower()
        # print(type(command))
        # print(not is_module_exclusive(command))
        if not is_module_exclusive(command):
            occupied = name in self.all_commands  # fit char line limit
            if occupied and not self.all_commands[name].hidden:
                del self.all_commands[name]
            else:
                self.all_commands[name] = command
                for alias in command.aliases:
                    alias = alias.lower()
                    occupied = alias in self.all_commands
                    if occupied and not self.all_commands[alias].hidden:
                        del self.all_commands[alias]
                    else:
                        self.all_commands[alias] = command
            # Add as disambiguation...
            self.get_disambiguation(name, create=True)[
                id(command)] = command
            for alias in command.aliases:
                self.get_disambiguation(alias, create=True)[
                    id(command)] = command

        # Add to namespace...
        cog_name = command.cog_name
        print("Added {} from cog {}".format(name, cog_name))
        if cog_name is None:
            cog_name = "none"
            # If someone makes a cog named "None" they shouldn't.
        else:
            cog_name = cog_name.lower()
        namespace = self.get_namespace(cog_name, create=True)
        namespace[name] = command
        for alias in command.aliases:
            namespace[alias.lower()] = command

    def get_command(self, name):
        """Takes one or two words to get a command."""
        names = name.split()
        command = None
        disambiguation = self.get_disambiguation(names[0])
        namespace = self.get_namespace(names[0])
        sub_command = 1

        # Check if neither a command name nor cog name exists for the name.
        if disambiguation is None and namespace is None:
            return None
        elif disambiguation is not None and len(disambiguation) == 1:
            # If only one command bearing the name, then it's safe to select.
            command = list(disambiguation.values())[0]

        if command is None:
            if namespace is None or len(names) < 2:
                return None
            command = namespace.get(names[1])
            sub_command = 2

        if command is not None and isinstance(command, GroupMixin):
            for name in names[sub_command:]:
                try:
                    command = command.all_commands[name]
                except (AttributeError, KeyError):
                    return None
        return command

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
            # We'll need to affix the namespace name to the prefix if we get
            # a working command to invoke.
            namespace_name = invoker

            if disambiguation is not None and namespace is None:
                if len(disambiguation) == 1:
                    for val in disambiguation.values():
                        ctx.command = val
                        return ctx
                elif len(disambiguation) > 1:
                    if ctx.guild is not None:
                        ctx.command = self.get_guild_data(
                            ctx.guild).command_map.get(ctx.invoked_with)
                    return ctx

            if namespace is not None:
                # print(namespace)
                view.skip_ws()
                invoker = view.get_word().lower()
                if invoker:
                    ctx.command = namespace.get(invoker)
                    ctx.invoked_with = invoker
                    ctx.prefix += namespace_name + " "
        return ctx

    async def on_message(self, message):
        """Filter out commands from bots since the library doesn't do it for
        us anymore.
        """
        if message.author.bot:
            return
        await self.process_commands(message)

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

    def remove_cog(self, name):
        """The reason I can't just call super here is because removing
        commands ideally wants a cog name to go with it because of how
        disambiguations work.
        """
        cog = self.cogs.pop(name, None)
        self.lower_cogs.pop(name.lower(), None)
        if cog is None:
            return cog
        members = getmembers(cog)
        for _, member in members:
            # remove commands the cog has
            if isinstance(member, Command):
                if member.parent is None:
                    # Our new remove_command function needs the cog name since
                    # disambiguations are possible.
                    self.remove_command(member.name, name)
                continue

            # remove event listeners the cog has
            if name.startswith('on_'):
                self.remove_listener(member)
        try:
            check = getattr(cog,
                            '_{0.__class__.__name__}__global_check'.format(
                                cog))
        except AttributeError:
            pass
        else:
            self.remove_check(check)
        try:
            check = getattr(cog,
                            '_{0.__class__.__name__}' +
                            '__global_check_once'.format(cog))
        except AttributeError:
            pass
        else:
            self.remove_check(check)
        unloader_name = '_{0.__class__.__name__}__unload'.format(cog)
        try:
            unloader = getattr(cog, unloader_name)
        except AttributeError:
            pass
        else:
            unloader()
        del cog

    def remove_command(self, name, cog=None):
        """Will exterminate the most recently-added command bearing the
        specified name.
        """
        super().remove_command(name)
        # print("Remove {} from cog {}".format(name, str(cog)))
        # self.all_commands has been dealt with at this point.
        command = None
        disambiguation = self.get_disambiguation(name)

        # if disambiguation is None:
        # return None

        # Search for command in the disambiguation.
        # command = None
        # for cmd in disambiguation.values():
        # if cog is None or str(cog) == cmd.cog_name:
        # command = cmd

        if disambiguation is not None:
            for cmd in disambiguation.values():
                if str(cog).lower() == str(cmd.cog_name).lower() or len(
                        disambiguation) == 1:
                    command = cmd

        namespace = self.get_namespace(str(cog))
        if command is None and namespace is not None:
            command = namespace.get(name)
        elif command is not None:
            # cog = str(command.cog_name).lower()
            namespace = self.get_namespace(str(command.cog_name))

        # We cannot find a command based on name and we weren't given a cog
        # name in which the command might be located so we have no leads.
        if command is None or namespace is None:
            return command

        # Remove command from disambiguation if there's an entry for it.
        disambiguation_found = disambiguation is not None
        if disambiguation_found:
            disambiguation.pop(id(command))
            for cmd in disambiguation.values():
                if not is_module_exclusive(cmd):
                    if name in self.all_commands:
                        del self.all_commands[name]
                        break
                    self.all_commands[name] = cmd

        namespace.pop(name)
        if name not in command.aliases:
            for alias in command.aliases:
                namespace.pop(alias)
                if disambiguation_found:
                    disambiguation = self.get_disambiguation(alias)
                    if disambiguation is None:
                        continue  # Should not occur.
                    disambiguation.pop(id(command))
                    # Maybe we should take this repeated code and put it into
                    # a function of its own...
                    for cmd in disambiguation.values():
                        if not is_module_exclusive(cmd):
                            if name in self.all_commands:
                                del self.all_commands[name]
                                break
                            self.all_commands[name] = cmd
        # print("{} removed".format(command))

        # Preserve old code for now...
        if True:
            return command

        # Remove command from namespace if it is found.
        if command is not None:
            namespace = self.get_namespace(str(command.cog_name))
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
        print("{} removed".format(command))
        return command

    def remove_commands_named(self, name):
        count = 0
        while self.remove_command(name) is not None:
            count += 1
        return count

    def walk_commands(self):
        """Uses disambiguations instead of all_commands."""
        for disambiguation in tuple(self.disambiguations.values()):
            for command in tuple(disambiguation.values()):
                yield command
                if isinstance(command, GroupMixin):
                    yield from command.walk_commands()

    async def on_ready(self):
        """Just print some things here to show a connection or reconnection."""
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
        if ctx is None:
            return "No context to run the code in!"
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

    def load_cogs(self, folder=None):
        """Load extensions from a certain folder."""
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

    def run(self, *args, **kwargs):
        """By now we've initialized all modules so we can go ahead and map
        commands for guilds that have imported modules.
        """
        self.guild_cog.load_all_guild_data()
        super().run(*args, **kwargs)

    async def reply(self, ctx, content):
        if ctx.message.guild is None:
            await ctx.send(content)
        else:
            await ctx.send(ctx.message.author.mention + ", " + content)
