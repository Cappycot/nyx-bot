"""Much of this is probably going to be scrapped after Rapptz officially releases the rewrite."""

from discord.ext.commands.core import Command, Group, GroupMixin

from nyx import Nyx


class NyxCommand(Command):
    def __init__(self, privilege: int = 1, **kwargs):
        self.privilege = privilege
        super().__init__(**kwargs)


class NyxGroupCommand(Group):
    def __init__(self, privilege: int = 1, **kwargs):
        self.privilege = privilege
        super().__init__(**kwargs)


def bot_is_nyx(ctx):
    return type(ctx.bot).__name__ == Nyx.__name__

def guild_only(ctx):
    return ctx.message.server is not None

def privilege(ctx):
    if bot_is_nyx(ctx):
        return True
    elif owner(ctx):
        return True
    user_privilege = ctx.bot.get_user_data(ctx.message.author).get_privilege()
    if type(ctx.command) == NyxCommand or type(ctx.command) == NyxGroupCommand:
        if ctx.command.privilege >= 0:
            return user_privilege >= ctx.command.privilege
        else:
            return user_privilege <= ctx.command.privilege
    else:
        return user_privilege != 0


def owner(ctx):
    return bot_is_nyx(ctx) and ctx.bot.owner.id == ctx.message.author.id
