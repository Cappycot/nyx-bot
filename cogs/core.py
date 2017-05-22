import asyncio

from discord.ext import commands
from discord.ext.commands.view import StringView


class Core:
    def __init__(self, nyx):
        self.nyx = nyx

    def owner(ctx):
        return ctx.bot.owner.id == ctx.message.author.id

    @commands.command(pass_context=True)
    @commands.check(owner)
    async def exec(self, ctx):
        view = StringView(ctx.message.content)
        view.skip_string(ctx.prefix + ctx.invoked_with)
        code = view.read_rest().strip()
        if code.startswith("```Python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        output = await self.nyx.loadstring(code)
        output = "```" + output + "```"
        if ctx.message.server is None:
            await self.nyx.say(output)
        else:
            await self.nyx.reply(output)

    async def shutdown(self):
        await self.nyx.say("Light cannot be without dark!!!")
        await asyncio.sleep(1)
        await self.nyx.logout()


def setup(bot):
    bot.add_cog(Core(bot))
