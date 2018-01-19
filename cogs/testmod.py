from discord.ext import commands

from nyx.nyxutils import respond


class TestOne:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    async def asdf(self, ctx):
        await ctx.send("no")

    @commands.command()
    async def test(self, ctx):
        """Prints "asdf\""""
        await ctx.send("asdf")

    @commands.command()
    async def fraktur(self, ctx, *words: str):
        result = "Your fried text:"
        for word in words:
            result += " "
            for char in word:
                val = ord(char)
                # print(val)
                if 65 <= val <= 90:
                    result += chr(val + 120107)
                elif 97 <= val <= 122:
                    result += chr(val + 120101)
                else:
                    result += char
        await respond(ctx, result)

    @commands.group()
    async def cool(self, ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

    @cool.command(name='bot')
    async def _bot(self, ctx):
        """Is the bot cool?"""
        await ctx.send('Yes, the bot is cool.')


class TestTwo:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    async def test(self, ctx):
        await ctx.send("fdsa")


def setup(bot):
    bot.add_cog(TestOne(bot))
    bot.add_cog(TestTwo(bot))
