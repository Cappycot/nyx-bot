"""
Test concept for pinging Minecraft servers asynchronously in the most
inefficient manner humanly possible...
"""

from asyncio import sleep
from datetime import datetime
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import BucketType
from mcstatus import MinecraftServer
from threading import Thread


class ServerPingThread(Thread):
    """We need crappy multithreading here because Dinnerbone doesn't write
    his stuff using async and everything gets blocked...

    This represents a short-lived thread for getting information once.
    """

    def __init__(self, address: str, port: int = 25565,
                 name: str = "Minecraft Server", site: str = None):
        Thread.__init__(self)
        self.name = name
        self.online = False
        self.server = MinecraftServer(address, port)
        self.site = site
        self.status = None
        self.timestamp = None

    def run(self):
        try:
            self.status = self.server.status()
            self.online = True
        except:
            self.online = False
        self.timestamp = datetime.now()

    def get_embed(self, timeout):
        embed = Embed(title=self.name, description=":".join(
            [self.server.host, str(self.server.port)]), url=self.site)
        embed.add_field(name="Status",
                        value="Online" if self.online else "Offline")
        embed.colour = Color.red()
        if self.online and self.status is not None:
            embed.add_field(name="Message", value=self.status.description)
            players = self.status.players
            embed.add_field(name="Players",
                            value="{}/{}".format(players.online, players.max))
            embed.colour = Color.green()
            embed.set_footer(
                text="Got reply in {} ms.".format(self.status.latency))
        else:
            timeout = "1 second" if timeout == 1 else "{} seconds".format(
                timeout)
            embed.set_footer(
                text="Unable to get reply within {}.".format(timeout))
        return embed


site = ""
servers = {25565: "Server"}


class Polycraft:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def servers(self, ctx, timeout: int = 3):
        """Gets the current status of the Polycraft servers."""
        if timeout < 1:
            timeout = 1
        async with ctx.message.channel.typing():
            threads = []
            for thread in threads:
                thread.start()
            await sleep(timeout)
            for thread in threads:
                await ctx.send(embed=thread.get_embed(timeout))


def setup(bot):
    bot.add_cog(Polycraft(bot))
