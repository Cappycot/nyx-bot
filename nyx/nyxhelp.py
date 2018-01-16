"""
Here we need to replace the default help command to be able to deal with
disambiguations while feeding same or similar information to HelpFormatters...

Possible solutions for injecting disambiguation information:
 - Injecting the cog name (lowercase probably) into the Context prefix.

Notes:
 - Command signature is in the format [name|alias] <param> [param]
"""

from discord.ext import commands
from discord.ext.commands import HelpFormatter
import re

_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}

_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))


class Help:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    async def help(self, ctx, *commands: str):
        """Gives help in the form of command descriptions and usages."""
        nyx = ctx.bot
        destination = ctx.message.author if nyx.pm_help \
            else ctx.message.channel

        def clear_dumb_mentions(obj):
            return _mentions_transforms.get(obj.group(0), "")

        if len(commands) == 0:
            pages = await nyx.formatter.format_help_for(ctx, nyx)
        else:
            name = _mention_pattern.sub(clear_dumb_mentions, commands[0])
            cog = nyx.lower_cogs.get(name.lower())
            command = None
            disambiguation = nyx.disambiguations.get(name)
            start = 1
            if disambiguation is None:
                if cog is None:
                    await destination.send(nyx.command_not_found.format(name))
                    return
                elif len(commands) > 1:
                    command = nyx.namespaces.get(name.lower()).get(commands[1])
                    ctx.prefix = "".join(
                        [ctx.prefix, type(cog).__name__.lower(), " "])
                    start = 2
            elif len(disambiguation) > 1:
                command_text = nyx.command_has_disambiguation.format(name)
                for command in disambiguation.values():
                    command_text += nyx.command_disambiguation.format("".join(
                        [ctx.prefix, command.cog_name.lower(), " ",
                         command.name.lower()]),
                        command.help or nyx.command_no_description)
                await destination.send(command_text)
                return
            else:
                command = list(disambiguation.values())[0]
            if command is not None:
                for arg in commands[start:]:
                    try:
                        arg = _mention_pattern.sub(clear_dumb_mentions, arg)
                        command = command.all_commands.get(arg)
                        if command is None:
                            await destination.send(
                                nyx.command_not_found.format(arg))
                            return
                    except AttributeError:
                        await destination.send(
                            nyx.command_has_no_subcommands.format(command,
                                                                  arg))
                        return
                pages = await nyx.formatter.format_help_for(ctx, command)
            else:
                pages = await nyx.formatter.format_help_for(ctx, cog)

        if nyx.pm_help is None:
            characters = sum(map(lambda l: len(l), pages))
            if characters > 1000:
                destination = ctx.message.author

        for page in pages:
            await destination.send(page)


class NyxHelpFormatter(HelpFormatter):
    pass


# def setup(nyx):
# nyx.remove_command("help")
# nyx.add_cog(Help(nyx))
