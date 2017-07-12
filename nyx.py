"""
Nyx! A (Mostly Unison League themed) bot...

https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=8

https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

clear; nohup python3 nyx.py >/dev/null &2>1 &

Current Tasks:
 - Rewrite framework to use Discord cogs and stuff...
 - Rewrite task scheduling? (Clocks)
 - Add "dirty" boolean to Guild/UserData for write back optimization.
 - Conform to Python styling guidelines laid out in PEP 8.
Future Tasks:
 - Split Nyx up into Nyx and AutoShardedNyx and have original
   be NyxBase...
 - Move all module code on repo to the new Nyx-Modules repo.
 - Figure out GitHub API for automatic code updates?
"""

import inspect
import sys
from configparser import ConfigParser
from contextlib import closing, redirect_stdout
from io import StringIO
from os import getcwd, listdir
from os.path import isfile

from discord import ClientException
from discord.ext.commands import Bot, Command, CommandError, CommandNotFound, \
    Context, GroupMixin
from discord.ext.commands.view import StringView

nyx_config_file = "info.nyx"


class CommandHasDisambiguation(CommandError):
    """Exception raised when a command is attempted to be invoked
    but the command exists under multiple cogs.

    This does not apply to subcommands.
    """
    pass


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

    def check_collision(self, namespace: dict):
        for name in namespace:
            if name in self.command_map and self.command_map[name] is not None:
                return name
        return None

    def import_module(self, nyx, mod):
        mod = mod.lower()
        if mod in self.modules:
            return False
        namespace = nyx.get_namespace(mod)
        if namespace is None:
            return False
        if self.check_collision(namespace) is not None:
            return False
        self.modules.append(mod)
        for name in namespace:
            self.command_map[name] = namespace[name]
        return True

    def map_commands(self, nyx):
        self.command_map = {}
        passed_modules = []
        for mod in self.modules:
            namespace = nyx.get_namespace(mod)
            if namespace is None:
                continue
            if self.check_collision(namespace) is not None:
                continue
            for name in namespace:
                self.command_map[name] = namespace[name]
            passed_modules.append(mod)
        self.modules = passed_modules

    def deport_module(self, nyx, mod):
        mod = mod.lower()
        if mod not in self.modules:
            return False
        self.modules.remove(mod)
        # For the record, I did consider lazy deletion, but there may come a
        # time in the future when namespaces can be modified, so map_commands
        # is a good thing to have around.
        self.map_commands(nyx)
        return True


class UserData:
    """Class for storing specific data for a Discord user.
    Only the user ID of a Discord User is stored between
    sessions outside of permissions and module-specific data.
    """

    def __init__(self, user_id: int):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = user_id
        self.data = {"privilege": 1}

    @property
    def privilege(self):
        return self.data["privilege"]

    def get_privilege(self):
        return self.data["privilege"]

    def set_privilege(self, level: int):
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

    def __init__(self, **options):
        self.cogs_folder = None
        # Used to group commands by module name for easy collision resolution.
        self.command_disambiguation = options.pop("command_disambiguation",
                                                  "```{} - {}```")
        self.command_has_disambiguation = options.pop(
            "command_has_disambiguation",
            'Command "{}" exists in multiple modules as:')
        self.command_no_description = options.pop("command_no_description",
                                                  "No description.")
        self.core_commands = {}
        self.disambiguations = {}
        self.lower_cogs = {}
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
        super().__init__(command_prefix=check_prefix, **options)

    def add_cog(self, cog):
        lower_name = type(cog).__name__.lower()
        if lower_name in self.lower_cogs:
            raise ClientException(
                "The cog {} is already registered.".format(lower_name))
        self.lower_cogs[lower_name] = cog
        super().add_cog(cog)

    def add_command(self, command):
        # Raise the usual errors from super method.
        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command')

        # If there is already said name/alias occupying the main commands,
        # then remove it and leave it to be handled by disambiguation.
        name = command.name.lower()
        if name not in self.all_commands:
            self.all_commands[name] = command
            for alias in command.aliases:
                alias = alias.lower()
                if alias not in self.all_commands:
                    self.all_commands[alias] = command
                else:
                    del self.all_commands[alias]
        else:
            del self.all_commands[name]

        # Add as disambiguation...
        self.get_disambiguation(name, create=True)[
            id(command)] = command
        for alias in command.aliases:
            self.get_disambiguation(alias.lower(), create=True)[
                id(command)] = command

        # Add to namespace...
        cog_name = command.cog_name
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
                view.skip_ws()
                invoker = view.get_word().lower()
                if invoker:
                    ctx.invoked_with = invoker
                    ctx.command = namespace.get(invoker)
        return ctx

    async def invoke(self, ctx):
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
        disambiguations work."""
        cog = self.cogs.pop(name, None)
        self.lower_cogs.pop(name.lower(), None)
        if cog is None:
            return cog
        members = inspect.getmembers(cog)
        for name, member in members:
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
        specified name."""
        super().remove_command(name)
        # self.all_commands has been dealt with at this point.
        disambiguation = self.get_disambiguation(name)
        if disambiguation is None:
            return None

        # Search for command in the disambiguation.
        command = None
        for cmd in disambiguation.values():
            if cog is None or str(cog) == cmd.cog_name:
                command = cmd

        # Remove command from namespace if it is found.
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

    async def reply(self, ctx, content):
        if ctx.message.guild is None:
            await ctx.send(content)
        else:
            await ctx.send(ctx.message.author.mention + ", " + content)


if __name__ == "__main__":
    nyx = Nyx()

    nyx.load_cogs("cogs")

    nyx_config = ConfigParser()
    nyx_config.read(nyx_config_file)
    # If the file doesn't exist ConfigParser will just read empty.
    if "Settings" not in nyx_config:
        print("Settings not found. Configure your " +
              nyx_config_file + " file.")
    elif "Token" not in nyx_config["Settings"]:
        print("Token setting not found. Configure your " +
              nyx_config_file + " file.")
    else:
        nyx.run(nyx_config["Settings"]["Token"])
