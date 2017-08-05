import discord
from discord.ext import commands

from os.path import join

folder = "testsounds"


class TestSoundboard:
    def __init__(self, _):
        pass

    async def play_file(self, ctx, sound):
        """Plays a file from the local filesystem"""

        if ctx.voice_client is None:
            if ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("Not connected to a voice channel.")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        def done(e):
            if e:
                print("Player error: %s" % e)
            if not ctx.voice_client.is_playing():
                ctx.bot.loop.create_task(ctx.voice_client.disconnect())

        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(join(folder, sound)))
        ctx.voice_client.play(source, after=done)

        # await ctx.send('Now playing: {}'.format(query))

    @commands.command(aliases=["ooof", "oooof"])
    async def oof(self, ctx):
        await self.play_file(ctx, "oof.mp3")

    @commands.command(aliases=["ooooof", "ooooooof", "oooooooof"])
    async def oooooof(self, ctx):
        await self.play_file(ctx, "oooooof.mp3")

    @commands.command(aliases=["ooooooooof", "ooooooooooof", "oooooooooooof"])
    async def oooooooooof(self, ctx):
        await self.play_file(ctx, "oooooooooof.mp3")

    @commands.command()
    async def fix(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(TestSoundboard(bot))
