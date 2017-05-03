"""
Nyx! A (Mostly Unison League themed) bot...
https://discordapp.com/oauth2/authorize?client_id=
201425813965373440&scope=bot&permissions=0
https://drive.google.com/open?id=0B94jrO7TTwmORFlpeTJ1Z09UVEU

Current Tasks:
 - Rewrite framework to use Discord cogs and stuff...
 - Rewrite task scheduling? (Clocks)
 - Conform to Python styling guidelines laid out in PEP 8.
   (Meaning lines are < 80 chars and comments <= 72 chars length.)
Future Tasks:
 - Move all module code on repo to the new Nyx-Modules repo.
 - Figure out GitHub API for automatic code updates?
 - Create thread locks for certain kinds of objects possibly...
"""

import sys
from contextlib import closing, redirect_stdout
from io import StringIO

from discord.ext import commands


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


def check_prefix(nyx, message):
    if message.server is not None:
        return nyx.get_server_data(message.server).prefixes
    return nyx.prefixes


class Nyx(commands.Bot):
    """The main class for holding a client and its modules.
    More information later. This is a placeholder for multi-line doc.
    """

    def __init__(self):
        super().__init__(command_prefix=check_prefix)
        # Default command prefixes that can be overwritten...
        self.prefixes = ["$", "~", "!", "%", "^", "&",
                         "*", "-", "=", ".", ">", "/"]

    def loadstring(self, code):
        """Remote execute code from the Discord client or other sources
        for debugging. This returns true if the code to execute runs
        completely without error. This function also reroutes print
        statements if kwargs contains a list named "output".

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
            self.servers[discord_server.id] = server
            return server
        else:
            return self.servers[discord_server.id]
