"""
Here we need to replace the default help command to be able to deal with
disambiguations while feeding same or similar information to HelpFormatters...

Possible solutions for accounting for disambiguation information:
 - Injecting the cog name (lowercase probably) into the Context prefix.

Notes:
 - Command signature is in the format [name|alias] <param> [param]
"""

import re

from discord.ext import commands
from discord.ext.commands import HelpFormatter
from discord.ext.commands.errors import CommandError

from nyx.nyxcommands import ModuleExclusiveCommand

_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}

_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))


class Help:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command()
    async def help(self, ctx, *words: str):
        """Gives help in the form of command descriptions and usages."""
        nyx = ctx.bot
        destination = ctx.message.author if nyx.pm_help \
            else ctx.message.channel

        def clear_dumb_mentions(obj):
            return _mentions_transforms.get(obj.group(0), "")

        if len(words) == 0:
            pages = await nyx.formatter.format_help_for(ctx, nyx)
        else:
            name = _mention_pattern.sub(clear_dumb_mentions, words[0])
            cog = nyx.lower_cogs.get(name.lower())
            print(name)
            command = None
            # Search guild namespace for commands.
            if ctx.guild is not None:
                guild = nyx.get_guild_data(ctx.guild)
                if name.lower() in guild.command_map:
                    command = guild.command_map[name.lower()]
            disambiguation = nyx.disambiguations.get(name)
            start = 1
            if disambiguation is None and command is None:
                if cog is None:
                    await destination.send(nyx.command_not_found.format(name))
                    return
                elif len(words) > 1:
                    command = nyx.namespaces.get(name.lower()).get(words[1])
                    ctx.prefix = "".join(
                        [ctx.prefix, type(cog).__name__.lower(), " "])
                    start = 2
            elif disambiguation is not None and len(disambiguation) > 1:
                command_text = nyx.command_has_disambiguation.format(name)
                for d_command in disambiguation.values():
                    command_text += nyx.command_disambiguation.format("".join(
                        [ctx.prefix, d_command.cog_name.lower(), " ",
                         d_command.name.lower()]),
                        d_command.help or nyx.command_no_description)
                await destination.send(command_text)
                if command is None:
                    return
            elif command is None:
                command = list(disambiguation.values())[0]
            if command is not None:
                for arg in words[start:]:
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
    """Tweaked default HelpFormatter for how Nyx's command system works."""

    def _add_subcommands_to_page(self, max_width, commands):
        """A lot of this work is under the hood because of the tweaks Nyx's
        new command system does.
        """
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue
            # need_module = isinstance(command, ModuleExclusiveCommand)
            if isinstance(command, ModuleExclusiveCommand):
                name = "{} {}".format(command.cog_name.lower(), name)
            if len(command.short_doc) > 0:
                entry = '  {0:<{width}} - {1}'.format(name, command.short_doc,
                                                      width=max_width)
            else:
                entry = "  {0:<{width}}".format(name, width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)

    async def filter_command_list(self):
        """Returns a filtered list of commands based on the two attributes
        provided, :attr:`show_check_failure` and :attr:`show_hidden`.
        Also filters based on if :meth:`~.HelpFormatter.is_cog` is valid.
        This function is modded to use Nyx's namespace system.

        Returns
        --------
        iterable
            An iterable with the filter being applied. The resulting value is
            a (key, value) :class:`tuple` of the command name and the command itself.
        """

        def sane_no_suspension_point_predicate(tup):
            cmd = tup[1]
            if self.is_cog():
                # filter commands that don't exist to this cog.
                if cmd.instance is not self.command:
                    return False

            if cmd.hidden and not self.show_hidden:
                return False

            return True

        async def predicate(tup):
            if sane_no_suspension_point_predicate(tup) is False:
                return False

            cmd = tup[1]
            try:
                return await cmd.can_run(self.context)
            except CommandError:
                return False

        # iterator = self.command.all_commands.items() if not self.is_cog()
        # else self.context.bot.all_commands.items()
        # if self.show_check_failure:
        # return filter(sane_no_suspension_point_predicate, iterator)

        # Gotta run every check and verify it
        ret = []
        # for elem in iterator:
        # valid = await predicate(elem)
        # if valid:
        # ret.append(elem)

        nyx = self.context.bot if self.is_cog() else self.command

        if self.is_cog():
            namespace = nyx.get_namespace(type(self.command).__name__.lower())
            for elem in namespace.items():
                valid = await predicate(elem)
                if valid:
                    ret.append(elem)
        else:
            for namespace in nyx.namespaces.values():
                for elem in namespace.items():
                    valid = await predicate(elem)
                    if valid:
                        ret.append(elem)

        return ret
