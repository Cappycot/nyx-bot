from asyncio import sleep, TimeoutError
from random import randint

from discord import Color, Embed, File
from discord.ext import commands


class FakeFlower():
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    @commands.guild_only()
    async def fakeflower(self, ctx):
        """heh"""
        disabled = False
        if disabled:
            author = ctx.message.author
            avatar = author.default_avatar_url if \
                not author.avatar else author.avatar_url
            embed = Embed(
                description=(author.display_name + " tried to use " +
                             "fakeflower...\nWhat a fool! :joy:"))
            embed.set_author(name=author.display_name, icon_url=avatar)
            embed.colour = Color.green()
            await ctx.send(embed=embed)
            return

        # old code
        manageable = ctx.message.channel.permissions_for(
            ctx.message.guild.get_member(self.nyx.user.id)).manage_messages
        if manageable:
            await ctx.message.delete()
        else:
            await sleep(randint(60, 120))
        await sleep(randint(120, 300))

        def latch(m):
            return m.channel == ctx.message.channel

        await self.nyx.wait_for("message", check=latch)
        flower_file = open("img" + str(randint(1, 3)) + ".jpg", "rb")
        bait = await ctx.send(
            "5 random :cherry_blossom: appeared! " +
            "Pick them up by typing ``>pick``",
            file=File(flower_file))

        def fooled(m):
            return m.content == ">pick" and m.channel == ctx.message.channel

        try:
            fool = await self.nyx.wait_for("message", check=fooled,
                                           timeout=60)
            await bait.delete()
            if fool is None:
                return
            elif manageable:
                await fool.delete()
            author = fool.author
            avatar = author.default_avatar_url if not author.avatar \
                else author.avatar_url
            embed = Embed(
                description=(author.display_name +
                             " picked 0 :cherry_blossom:" +
                             "\nWhat a fool! :joy:"))
            embed.set_author(name=author.display_name, icon_url=avatar)
            embed.colour = Color.green()
            await ctx.send(embed=embed)
        except TimeoutError:
            await bait.delete()


def setup(bot):
    bot.add_cog(FakeFlower(bot))
