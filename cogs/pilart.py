from asyncio import sleep, TimeoutError
from io import BytesIO
from random import randint

import aiohttp
import discord
from PIL import Image
from discord import Embed, File
from discord.ext import commands
from discord.ext.commands import BucketType

from nyxutils import get_predicate, get_user, respond


# 5 random :cherry_blossom: appeared! Pick them up by typing >pick

class PILArt:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
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
            embed.colour = discord.Color.green()
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
            embed.colour = discord.Color.green()
            await ctx.send(embed=embed)
        except TimeoutError:
            await bait.delete()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def fear(self, ctx):
        """For when you fear someone or yourself..."""
        tofear = get_user(ctx, get_predicate(ctx)) or ctx.message.author
        url = tofear.avatar_url
        if not url:
            url = tofear.default_avatar_url

        # Make http request for profile picture and get background
        async with ctx.message.channel.typing(), aiohttp.ClientSession(
                loop=self.nyx.loop) as session, session.get(url) as req:
            # async with session.get(url) as req:
            if req.status == 200:
                imfile = BytesIO(await req.read())
                tofear = Image.open(imfile).convert("RGBA")
                backdrop = Image.open("NoFearOneFear.png")

                # Presets for image creation
                avatarside = 240
                fpos = (522, 132)

                # Paste avatar pic on top of backdrop as resized image
                tofear = tofear.resize((avatarside, avatarside),
                                       Image.LANCZOS)
                backdrop.paste(tofear, (
                    fpos[0], fpos[1], fpos[0] + avatarside,
                    fpos[1] + avatarside), mask=tofear)

                # Save in-memory filestream and send to Discord
                imfile = BytesIO()
                backdrop.save(imfile, format="png")
                # Move pointer to beginning so Discord can read pic.
                imfile.seek(0)
                msg = "We are all very afraid..."
                if ctx.guild is not None:
                    msg = ctx.message.author.mention + ", w" + msg[1:]
                await ctx.send(msg,
                               file=File(imfile,
                                         filename="nofearonefear.png"))
                imfile.close()
            else:
                await respond(ctx, "Image loading failed! :<")

    @commands.command(aliases=["destroy"])
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def obliterate(self, ctx, victim):
        """For when you really hate someone..."""
        victim = get_user(ctx, victim)
        if victim is None:
            await respond(ctx, "We couldn't get a target, sir!")
        elif victim == self.nyx.user:
            await respond(ctx, "I'm your gunner... moron.")
        elif victim == ctx.message.author:
            await respond(ctx, "What? Do you have crippling depression?")
        else:
            shooter = ctx.message.author
            # Get urls for profile pics
            url2 = victim.avatar_url
            if not url2:
                url2 = victim.default_avatar_url
            url1 = shooter.avatar_url
            if not url1:
                url1 = shooter.default_avatar_url
            # Presets for image creation
            avatarside = 80
            spos = (130, 42)
            vpos = (260, 360)

            # Make http request for profile pictures and get background tank
            async with ctx.message.channel.typing(), aiohttp.ClientSession(
                    loop=self.nyx.loop) as session, session.get(
                    url1) as req1, session.get(url2) as req2:
                # async with session.get(url1) as req1:
                if req1.status == 200 and req2.status == 200:
                    imfile = BytesIO(await req1.read())
                    shooter = Image.open(imfile).convert("RGBA")
                    imfile = BytesIO(await req2.read())
                    victim = Image.open(imfile)
                    # TODO: Figure out image directories
                    backdrop = Image.open("Obliterate.png")

                    # Paste shooter on top of tank as resized image
                    shooter = shooter.resize(
                        (avatarside, avatarside), Image.LANCZOS)
                    backdrop.paste(shooter, (
                        spos[0], spos[1], spos[0] + avatarside,
                        spos[1] + avatarside), mask=shooter)

                    # Resize, tint, rotate, and paste victim
                    victim = victim.resize(
                        (avatarside, avatarside),
                        Image.LANCZOS).convert("RGBA")

                    data = victim.getdata()
                    new_data = []
                    for i in range(0, len(data)):
                        item = data[i]
                        # Tint red and brighten a bit
                        red = min(item[0] + 42, 255)
                        green = min(item[1] + 9, 255)
                        blue = max(item[2] - 9, 0)
                        new_data.append(
                            (red, green, blue, item[3]))
                    victim.putdata(new_data)

                    victim = victim.rotate(-40, expand=True)
                    vw = victim.size[0]
                    vh = victim.size[1]
                    backdrop.paste(victim, (
                        vpos[0], vpos[1], vpos[0] + vw,
                        vpos[1] + vh),
                                   mask=victim)

                    # Save in-memory filestream and send to Discord
                    imfile = BytesIO()
                    backdrop.save(imfile, format="png")

                    # Move pointer to beginning.
                    imfile.seek(0)
                    msg = "Another one bites the dust! ``*CLAP*``"
                    if ctx.guild is not None:
                        msg = ctx.message.author.mention + \
                              ", a" + msg[1:]
                    await ctx.send(
                        msg, file=File(imfile,
                                       filename="bwaarp.png"))
                    imfile.close()
                else:
                    await respond(ctx, "Image loading failed! :<")


def setup(bot):
    bot.add_cog(PILArt(bot))
