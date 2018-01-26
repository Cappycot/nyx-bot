from discord.ext.commands import check
from discord.ext.commands import Command


class ModuleExclusiveCommand(Command):
    def __init__(self, name, callback, **kwargs):
        super(ModuleExclusiveCommand, self).__init__(name, callback, **kwargs)


async def check_privilege(ctx, privilege: int):
    if await ctx.bot.is_owner(ctx.message.author):
        return True
    user_privilege = ctx.bot.get_user_data(
        ctx.message.author).get_privilege()
    if privilege >= 0:
        return user_privilege >= privilege or user_privilege < 0
    else:
        return user_privilege <= privilege


def has_privilege(privilege=1):
    async def predicate(ctx):
        return await check_privilege(ctx, privilege)

    return check(predicate)


def has_privilege_or_permissions(privilege=1, **perms):
    async def predicate(ctx):
        if await check_privilege(ctx, privilege):
            return True
        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)
        return all(getattr(permissions, perm, None) == value for perm, value in
                   perms.items())

    return check(predicate)


def is_debug():
    async def predicate(ctx):
        return ctx.bot.debug

    return check(predicate)
