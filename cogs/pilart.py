from io import BytesIO

import aiohttp
from PIL import Image
from discord.ext import commands

from nyxutils import get_user, respond


# 5 random :cherry_blossom: appeared! Pick them up by typing >pick

class PILArt:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(aliases=["destroy"], pass_context=True)
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    async def obliterate(self, ctx, victim):
        """For when you really hate someone..."""
        await self.nyx.send_typing(ctx.message.channel)
        victim = get_user(ctx, victim)
        if victim is None:
            await respond(ctx, "We couldn't get a target, sir!")
        elif victim == self.nyx.user:
            await respond(ctx, "I'm your gunner... moron.")
        elif victim == ctx.message.author:
            await respond(ctx, "What? Do you have crippling depression?")
        else:
            # TODO: Decide whether to use else here instead of 3 returns...
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
            async with aiohttp.ClientSession(loop=self.nyx.loop) as session:
                async with session.get(url1) as req1:
                    if req1.status == 200:
                        imfile = BytesIO(await req1.read())
                        shooter = Image.open(imfile).convert("RGBA")
                        async with session.get(url2) as req2:
                            if req2.status == 200:
                                imfile = BytesIO(await req2.read())
                                victim = Image.open(imfile)
                                # TODO: Figure out image directories
                                backdrop = Image.open("Obliterate.png")

                                # Paste shooter on top of tank as resized image
                                shooter = shooter.resize((avatarside, avatarside), Image.LANCZOS)
                                backdrop.paste(shooter, (spos[0], spos[1], spos[0] + avatarside,
                                                         spos[1] + avatarside), mask=shooter)

                                # Resize, tint, rotate, and paste victim
                                victim = victim.resize((avatarside, avatarside), Image.LANCZOS).convert("RGBA")

                                data = victim.getdata()
                                new_data = []
                                for i in range(0, len(data)):
                                    item = data[i]
                                    # Tint red and brighten a bit
                                    red = min(item[0] + 42, 255)
                                    green = min(item[1] + 9, 255)
                                    blue = max(item[2] - 9, 0)
                                    new_data.append((red, green, blue, item[3]))
                                victim.putdata(new_data)

                                victim = victim.rotate(-40, expand=True)
                                vw = victim.size[0]
                                vh = victim.size[1]
                                backdrop.paste(victim, (vpos[0], vpos[1], vpos[0] + vw, vpos[1] + vh), mask=victim)

                                # Save in-memory filestream and send to Discord
                                imfile = BytesIO()
                                backdrop.save(imfile, format="png")

                                # Move pointer to beginning so Discord can read pic.
                                imfile.seek(0)
                                await self.nyx.send_file(ctx.message.channel, imfile, filename="bwaarp.png")
                                imfile.close()
                                await respond(ctx, "Another one bites the dust! ``*CLAP*``")
                            else:
                                await respond(ctx, "Image loading failed! :<")
                    else:
                        await respond(ctx, "Image loading failed! :<")


def setup(bot):
    bot.add_cog(PILArt(bot))
