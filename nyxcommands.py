from discord.ext.commands import check, has_permissions

from nyx import bot_is_nyx


def has_privilege(privilege=1):
    def predicate(ctx):
        if not bot_is_nyx(ctx):
            return True
        elif ctx.bot.is_owner(ctx.message.author):
            return True
        user_privilege = ctx.bot.get_user_data(
            ctx.message.author).get_privilege()
        if privilege >= 0:
            return user_privilege >= privilege
        else:
            return user_privilege <= privilege

    return check(predicate)


def has_privilege_or_permissions(privilege=1, **perms):
    def predicate(ctx):
        return has_privilege(privilege=privilege)(ctx) or has_permissions(
            **perms)

    return check(predicate)
