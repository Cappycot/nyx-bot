import asyncio

from discord.ext import commands

from nyx import bot_is_nyx
import nyxcommands
from nyxutils import get_predicate, get_server_member, respond


class Core:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(name="privilege", aliases=["rank"], pass_context=True)
    @commands.check(bot_is_nyx)
    async def check_privilege(self, ctx):
        """Displays your privilege rank."""
        if self.nyx.is_owner(ctx.message.author):
            privilege = "Owner"
        else:
            privilege = str(
                self.nyx.get_user_data(ctx.message.author).get_privilege())
        if ctx.message.guild is None:
            await ctx.send("Privilege: " + privilege)
        else:
            await ctx.send("".join(
                [ctx.message.author.mention, ", your privilege level is ",
                 privilege, "."]))

    @commands.command()
    @commands.check(bot_is_nyx)
    @commands.is_owner()
    async def exec(self, ctx, *code: str):
        """Remote executes code."""
        code = " ".join(code)
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

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def echo(self, ctx, *words: str):
        """I copy what you say."""
        if ctx.guild is not None and ctx.message.channel.permissions_for(
                ctx.message.guild.get_member(
                        self.nyx.user.id)).manage_messages:
            await ctx.message.delete()
        await ctx.send(" ".join(words))

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def shutdown(self, ctx):
        """Dun kill me pls..."""
        await ctx.send("Light cannot be without dark!!!")
        await asyncio.sleep(1)
        await self.nyx.logout()

    @commands.command()
    @commands.guild_only()
    async def whois(self, ctx):
        test = ctx.message.clean_content.split(" ")
        test = test[len(test) - 1]
        if test.startswith("@"):
            test = test[1:]
        await ctx.send(str(get_server_member(ctx.message.guild, test)))


def setup(bot):
    bot.add_cog(Core(bot))
