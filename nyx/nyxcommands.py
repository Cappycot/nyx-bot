import sys
from contextlib import closing, redirect_stdout
from io import StringIO

from discord.ext.commands import check


async def check_privilege(ctx, privilege: int):
    if await ctx.bot.is_owner(ctx.message.author):
        return True
    user_privilege = ctx.bot.get_user_data(ctx.message.author).get_privilege()
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


async def loadstring(code, ctx):
    """Remote execute code from the Discord client or other sources for
    debugging. This function returns a string with output.

    Arguments:
    code - the Python 3 code to run within self
    """
    if ctx is None:
        return "No context to run the code in!"
    with closing(StringIO()) as log:
        with redirect_stdout(log):
            try:
                exec(code)
            except:
                error = sys.exc_info()
                for e in error:
                    print(e)
        return log.getvalue()


def is_debug():
    async def predicate(ctx):
        return ctx.bot.debug

    return check(predicate)
