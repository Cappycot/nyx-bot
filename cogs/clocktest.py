import asyncio
from datetime import datetime
from discord.ext import commands
import nyxcommands

channel = None
role = None
times = [655, 1355, 1725, 2155]


class Mobius:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def bind(self, ctx, target):
        global channel
        global role
        channel = ctx.channel
        for thing in ctx.guild.roles:
            if thing.name.lower() == target.lower():
                role = thing
                break
        if not role.mentionable:
            await ctx.send("You baka! This role can't be mentioned!")
            channel = None
            role = None
            return
        await ctx.send(
            "Test timer set to ping the {} role.".format(role.name))

    @commands.command()
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def unbind(self, ctx):
        global channel
        global role
        channel = None
        role = None
        await ctx.send("Test timer disabled. Channel and role removed.")

    async def mention(self, ctx):
        global channel
        global role
        if ctx is not None:
            if channel is None or role is None:
                await ctx.send("You baka! Configure the timer first!")
                return
            elif ctx.channel != channel:
                await ctx.send("You baka! This is the wrong channel!")
                return
            await channel.send("The following is a test of the timer:")
        if channel is not None and role is not None:
            await channel.send(
                "Umm... {}, Mobius starts in 5 minutes...".format(
                    role.mention))

    @commands.command()
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_server=True)
    async def ping(self, ctx):
        await self.mention(ctx)

    async def clock(self):
        global times
        await self.nyx.wait_until_ready()
        last_minute = -1
        while True:
            await asyncio.sleep(1)
            time = datetime.now()
            if last_minute != time.minute:
                last_minute = time.minute
                stamp = time.hour * 100 + time.minute
                if any(stamp == a for a in times):
                    await self.mention(None)


def setup(bot):
    pass  # mobius = Mobius(bot)
    # bot.add_cog(mobius)
    # bot.loop.create_task(mobius.clock())
