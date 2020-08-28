"""
Here we need to replace the default help command to be able to deal with
disambiguations while feeding same or similar information to HelpFormatters...

Possible solutions for accounting for disambiguation information:
 - Injecting the cog name (lowercase probably) into the Context prefix.

Notes:
 - Command signature is in the format [name|alias] <param> [param]
"""

from itertools import groupby

from discord.ext.commands import Group, DefaultHelpCommand, MinimalHelpCommand
from discord.ext.commands.errors import CommandError
from discord.ext.commands.view import StringView
from discord.utils import maybe_coroutine


class DefaultNyxHelpCommand(DefaultHelpCommand):

    def __init__(self, no_category="None", **options):
        super().__init__(no_category=no_category, **options)
        self._ref_command = None

    async def filter_commands(self, commands, *, sort=False, key=None,
                              show_hidden=False):
        show_hidden |= self.show_hidden
        if sort and key is None:
            # key = lambda c: c.name
            def key(c):
                return c.name

        iterator = commands if self.show_hidden or show_hidden else filter(
            lambda c: not c.hidden, commands)

        if not self.verify_checks:
            # if we do not need to verify the checks then we can just
            # run it straight through normally without using await.
            return sorted(iterator, key=key) if sort else list(iterator)

        # if we're here then we need to check every command if it can run
        async def predicate(command):
            try:
                return await command.can_run(self.context)
            except CommandError:
                return False

        ret = []
        for cmd in iterator:
            valid = await predicate(cmd)
            if valid:
                ret.append(cmd)

        if sort:
            ret.sort(key=key)
        return ret

    def get_bot_mapping(self):
        mapping = super().get_bot_mapping()
        namespace_none = self.context.bot.get_namespace(None)
        if namespace_none is not None:
            mapping[None] = [a for a in namespace_none.values()]
        return mapping

    async def send_disambiguation_help(self, disambiguation, invoker,
                                       example=True):
        self.paginator.add_line(
            "The command \"{0}\" exists in multiple cogs.".format(invoker),
            empty=False)
        self.paginator.add_line(
            "Type the module name followed by \"{0}\" to invoke it.".format(
                invoker), empty=not example)

        def get_category(command, *,
                         no_category='\u200b{0.no_category}:'.format(self)):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else no_category

        filtered = await self.filter_commands(disambiguation.values(),
                                              sort=True, key=get_category)
        # If all commands with the same name are hidden, show all.
        if len(filtered) == 0:
            filtered = await self.filter_commands(disambiguation.values(),
                                                  show_hidden=True,
                                                  sort=True, key=get_category)
        max_size = self.get_max_size(filtered)
        to_iterate = groupby(filtered, key=get_category)

        # Now we can add the commands to the page.
        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if \
                self.sort_commands else list(commands)
            if example:
                self.paginator.add_line(
                    "e.g. {}{} {}".format(self.context.prefix,
                                          category[:-1].lower(),
                                          commands[0]), empty=True)
                example = False
            self.add_indented_commands(commands, heading=category,
                                       max_size=max_size)

        await self.send_pages()

    async def command_not_found(self, string):
        # self.context  # has all info
        # check for disambiguation
        # print(self._ref_command)
        view = StringView(self._ref_command)

        invoker = view.get_word().lower()

        bot = self.context.bot
        command = None
        disambiguation = bot.get_disambiguation(invoker)
        namespace = bot.get_namespace(invoker)
        namespaced = False

        if namespace is not None:
            view.skip_ws()
            # We'll need to affix the namespace name to the prefix if we
            # get a working command to invoke.
            namespace_name = invoker
            invoker = view.get_word().lower()
            if invoker:
                command = namespace.get(invoker)
                namespaced = True
                self.context.prefix += namespace_name + " "
        elif disambiguation is not None:
            if len(disambiguation) == 1:
                command = list(disambiguation.values())[0]
            elif len(disambiguation) > 1 and self.context.guild is not None:
                command = bot.get_guild_data(
                    self.context.guild).command_map.get(invoker)

        if command is None:
            if disambiguation is not None and len(disambiguation) > 1:
                return await self.send_disambiguation_help(disambiguation,
                                                           invoker)
            elif namespace is not None:
                return await self.send_cog_help(bot.lower_cogs[namespace_name])
        else:
            keys = self._ref_command.split(" ")[2 if namespaced else 1:]
            # print(keys)
            # for key in keys[1:]:
            for key in keys:
                try:
                    found = command.all_commands.get(key)
                except AttributeError:
                    string = await maybe_coroutine(self.subcommand_not_found,
                                                   command,
                                                   self.remove_mentions(key))
                    return await self.send_error_message(string)
                else:
                    if found is None:
                        string = await maybe_coroutine(
                            self.subcommand_not_found, command,
                            self.remove_mentions(key))
                        return await self.send_error_message(string)
                    command = found
            if isinstance(command, Group):
                await self.send_group_help(command)
            else:
                await self.send_command_help(command)
            return None

        return super().command_not_found(string)

    async def send_error_message(self, error):
        if error is not None:
            await super().send_error_message(error)

    async def prepare_help_command(self, ctx, command):
        self._ref_command = command
        await super().prepare_help_command(ctx, command)


class MinimalNyxHelpCommand(MinimalHelpCommand):
    pass
