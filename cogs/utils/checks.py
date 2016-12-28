from discord.ext import commands
from . import config


def is_owner_check(message):
    return message.author.id == config.owner_id


def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


def check_permissions(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def permissions(**perms):
    def predicate(ctx):
        return check_permissions(ctx, perms)

    return commands.check(predicate)

