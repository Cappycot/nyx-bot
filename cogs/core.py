import asyncio

from discord.ext import commands

import nyxprivilege
from nyxprivilege import NyxCommand
from nyxutils import get_predicate, get_server_member, respond


class Core:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(name="privilege", aliases=["rank"], pass_context=True)
    @commands.check(nyxprivilege.bot_is_nyx)
    async def check_privilege(self, ctx):
        """Displays your privilege rank."""
        if nyxprivilege.owner(ctx):
            privilege = "Owner"
        else:
            privilege = str(self.nyx.get_user_data(ctx.message.author).get_privilege())
        if ctx.message.server is None:
            await self.nyx.say("Privilege: " + privilege)
        else:
            await self.nyx.reply("your privilege level is " + privilege + ".")

    @commands.command(pass_context=True)
    @commands.check(nyxprivilege.bot_is_nyx)
    @commands.check(nyxprivilege.owner)
    async def exec(self, ctx):
        """Remote executes code."""
        code = get_predicate(ctx)
        if code.startswith("```Python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        output = await self.nyx.loadstring(code, ctx)
        if not output:
            output = "empty"
        output = "```" + output + "```"
        await respond(ctx, output)

    @commands.command(cls=NyxCommand, pass_context=True, privilege=-1)
    @commands.check(nyxprivilege.privilege)
    async def echo(self, ctx):
        """I copy what you say."""
        if ctx.message.channel.permissions_for(ctx.message.server.get_member(self.nyx.user.id)).manage_messages:
            await self.nyx.delete_message(ctx.message)
        await self.nyx.say(get_predicate(ctx))

    @commands.command(cls=NyxCommand, privilege=-1)
    @commands.check(nyxprivilege.privilege)
    async def shutdown(self):
        """Dun kill me pls..."""
        await self.nyx.say("Light cannot be without dark!!!")
        await asyncio.sleep(1)
        await self.nyx.logout()

    @commands.command(pass_context=True)
    @commands.check(nyxprivilege.guild_only)
    async def whois(self, ctx, query):
        test = ctx.message.clean_content.split(" ")
        test = test[len(test) - 1]
        if test.startswith("@"):
            test = test[1:]
        await self.nyx.say(str(get_server_member(ctx.message.server, test)))


def setup(bot):
    bot.add_cog(Core(bot))
