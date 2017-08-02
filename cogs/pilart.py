from io import BytesIO

import aiohttp
from PIL import Image
from discord import File
from discord.ext import commands
from discord.ext.commands import BucketType

from nyxutils import get_member, respond
from os.path import join

templates_folder = "pillow"


def get_asset(file_name):
    return join(templates_folder, file_name)


class PILArt:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def fear(self, ctx, user: str = None):
        """For when you fear someone or yourself..."""
        tofear = ctx.message.author
        if user is not None:
            tofear = await get_member(ctx, user)
            if tofear is None:
                await respond(ctx, "I dun know who you are talking about...")
                ctx.command.reset_cooldown(ctx)
                return
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
                backdrop = Image.open(get_asset("NoFearOneFear.png"))

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
                                         filename="Fear.png"))
                imfile.close()
            else:
                await respond(ctx, "Image loading failed! :<")

    @commands.command(aliases=["destroy"])
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    @commands.guild_only()
    async def obliterate(self, ctx, victim: str):
        """For when you really hate someone..."""
        victim = await get_member(ctx, victim)
        if victim is None:
            await respond(ctx, "We couldn't get a target, sir!")
            ctx.command.reset_cooldown(ctx)
        elif victim == self.nyx.user:
            await respond(ctx, "I'm your gunner... moron.")
            ctx.command.reset_cooldown(ctx)
        elif victim == ctx.message.author:
            await respond(ctx, "What? Do you have crippling depression?")
            ctx.command.reset_cooldown(ctx)
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
                    backdrop = Image.open(get_asset("Obliterate.png"))

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
                                       filename="Bwaarp.png"))
                    imfile.close()
                else:
                    await respond(ctx, "Image loading failed! :<")


def setup(bot):
    bot.add_cog(PILArt(bot))
