"""
Nyx! A (Mostly Unison League themed) bot...
https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=8
https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

Current Tasks:
 - Rewrite framework to use Discord cogs and stuff...
 - Rewrite task scheduling? (Clocks)
 - Conform to Python styling guidelines laid out in PEP 8.
Future Tasks:
 - Move all module code on repo to the new Nyx-Modules repo.
 - Figure out GitHub API for automatic code updates?
 - Create thread locks for certain kinds of objects possibly...
"""

import sys
from contextlib import closing, redirect_stdout
from io import StringIO
from ntpath import basename

from discord import ClientException
from discord.ext import commands
from discord.ext.commands.bot import _get_variable  # lol
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError, CommandNotFound
from discord.ext.commands.view import StringView
from discord.utils import find


class ServerData:
    """Class for holding preference data for Discord servers
    in terms of custom modules imported and prefixes to use.
    """

    def __init__(self, server_id):
        # id variable just in case a function references
        # the id parameter from this type of object.
        self.id = server_id
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


def check_prefix(nyx, message):
    if message.server is not None:
        server_prefixes = nyx.get_server_data(message.server).prefixes
        if len(server_prefixes) > 0:
            return server_prefixes
        else:
            mention = message.server.get_member(nyx.user.id).mention
            at_prefixes = []
            for prefix in nyx.prefixes:
                at_prefixes.append(mention + " " + prefix)
            return at_prefixes
    return nyx.prefixes


class Nyx(commands.Bot):
    """An extension of Discord's Bot class that can handle a collision
    between two commands from differing cogs with the same name if
    needed.
    """

    def __init__(self):
        self.collision = False
        # Used to group commands by module name for easy collision resolution.
        self.namespaces = {}
        self.cogs_folder = None
        # Default command prefixes that can be overwritten...
        self.prefixes = ["$", "~", "!", "%", "^", "&", "*", "-",
                         "=", ",", "<", ".", ">", "/", "?"]
        self.separate = False
        self.server_data = {}
        self.servers_folder = None
        self.users = {}
        self.users_folder = None
        # Runtime Status
        self.debug = False
        self.ready = False
        self.restart = False
        self.shutdown = False
        super().__init__(command_prefix=check_prefix)

    def loadstring(self, code):
        """Remote execute code from the Discord client or other sources
        for debugging. This returns true if the code to execute runs
        completely without error. This function returns a string with
        output.

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

    def get_namespace(self, name):
        if name not in self.namespaces:
            namespace = {}
            self.namespaces[name] = namespace
            return namespace
        else:
            return self.namespaces[name]

    def get_server_data(self, discord_server):
        """Retrieves the ServerData object for a particular Discord
        server. If such ServerData does not exist, then create a new
        object to hold data.
        """
        if discord_server is None:
            return None
        # Since both Discord Server and ServerData have a string id
        # parameter, this will still be okay if ServerData is passed.
        if discord_server.id not in self.servers:
            server = ServerData(discord_server.id)
            self.server_data[discord_server.id] = server
            return server
        else:
            return self.server_data[discord_server.id]

    def get_user_data(self, discord_user):
        user = None
        if discord_user.id not in self.users:
            user = UserData()
            self.users[discord_user.id] = user
        else:
            user = self.users[discord_user.id]
        return user

    def add_command(self, command):
        if not self.collision:
            try:
                super().add_command(command)
            except ClientException:
                self.collision = True
        cog_name = _get_variable("_cog_name")
        if cog_name is None:
            cog_name = "none"
        else:
            cog_name = cog_name.lower()
        namespace = self.get_namespace(cog_name)
        namespace[command.name] = command
        for alias in command.aliases:
            namespace[alias] = command

    def add_cog(self, cog):
        """Nyx's override to adding a cog."""
        _cog_name = type(cog).__name__
        super().add_cog(cog)

    async def process_commands(self, message):
        """Nyx's override to the default process_commands method."""

        _internal_channel = message.channel
        _internal_author = message.author

        view = StringView(message.content)
        if self._skip_check(message.author, self.user):
            return

        prefix = await self._get_prefix(message)
        invoked_prefix = prefix

        if not isinstance(prefix, (tuple, list)):
            if not view.skip_string(prefix):
                return
        else:  # discord.utils.find
            invoked_prefix = find(view.skip_string, prefix)
            if invoked_prefix is None:
                return

        command = None
        invoker = view.get_word()
        if message.server is not None:
            command = self.get_server_data(message.server).command_map.get(invoker, None)
        namespace = self.namespaces.get(invoker.lower(), None)
        print(invoker)
        print(namespace)
        tmp = {
            'bot': self,
            'invoked_with': invoker,
            'message': message,
            'view': view,
            'prefix': invoked_prefix
        }
        ctx = Context(**tmp)
        del tmp

        if command is None:
            if not self.collision and not self.separate:
                command = self.commands.get(invoker, None)
            if command is None and namespace is not None:
                view.skip_ws()
                invoker2 = view.get_word()
                if invoker2:
                    ctx.invoked_with = invoker2
                    command = namespace.get(invoker2, None)
                    if command is not None:
                        # remove module name and splice message.content
                        # this is to prevent confusion to cogs that expect
                        # the format <prefix> <command> <content>
                        omit = message.content.index(invoker)
                        message.content = message.content[:omit] + message.content[omit + len(invoker):].strip()

        if command is not None:
            self.dispatch("command", command, ctx)
            try:
                await command.invoke(ctx)
            except CommandError as e:
                ctx.command.dispatch_error(e, ctx)
            else:
                self.dispatch('command_completion', command, ctx)
        elif invoker:
            exc = CommandNotFound('Command "{}" is not found'.format(invoker))
            self.dispatch('command_error', exc, ctx)


if __name__ == "__main__":
    nyx = Nyx()

    nyx.load_extension("rng")

    for mod in nyx.namespaces:
        print("Mod " + mod)
        for c in nyx.namespaces[mod]:
            print(c)
    print("...")
    for key in nyx.commands:
        print(key)
        print(basename(nyx.commands[key].module.__file__))
    print("...")

    nyx.run("MjY0NTQyNTg5NzU4MzQxMTIw.C0iGAA.o_wNq4yiztxiddRZUHxissXGdpw")
