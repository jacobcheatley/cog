import discord
from discord.ext import commands
from .utils import database, checks


class Admin:
    """Bot management and member moderation."""

    def __init__(self, bot):
        self.bot = bot
        self.db = database.Database('admin.json', loop=bot.loop)

    def is_ignored(self, server: discord.Server, member: discord.Member):
        bypass = member.server_permissions.manage_server
        ignored = self.db.get('ignores', {}).get(server.id, [])

        if not bypass and member.id in ignored:
            return True
        return False

    def __check(self, ctx: commands.Context):
        message = ctx.message
        if checks.is_owner_check(message):
            return True

        if message.server and self.is_ignored(message.server, message.author):
            return False

        return True

    @commands.command(no_pm=True, pass_context=True)
    @checks.permissions(manage_server=True)
    async def ignore(self, ctx: commands.Context, *, member: discord.Member):
        """Ignores any commands sent by the member."""

        server_id = ctx.message.server.id
        ignores = self.db.get('ignores', {})
        server_ignores = ignores.get(server_id, [])

        if member.id in server_ignores:
            await self.bot.say(f'{member} already ignored.')
            return

        server_ignores.append(member.id)
        ignores[server_id] = server_ignores
        await self.db.put('ignores', ignores)
        await self.bot.say(f'{member} has been ignored.')

    @commands.command(no_pm=True, pass_context=True)
    @checks.permissions(manage_server=True)
    async def unignore(self, ctx, *, member: discord.Member):
        """Unignores a member."""

        server_id = ctx.message.server.id
        ignores = self.db.get('ignores', {})
        server_ignores = ignores.get(server_id, [])

        try:
            server_ignores.remove(member.id)
        except ValueError:
            await self.bot.say(f'{member} is not ignored.')

    @commands.group(no_pm=True, pass_context=True)
    @checks.permissions(manage_messages=True)
    async def remove(self, ctx: commands.Context):
        """Removes messages (in the last 50 messages by default) that meet a criteria."""

        if ctx.invoked_subcommand is None:
            await self.bot.say(f'Invalid criteria \'{ctx.subcommand_passed}\'')

    async def do_removal(self, message, limit, predicate):
        deleted = await self.bot.purge_from(message.channel, limit=limit, before=message, check=predicate)
        message = f'{len(deleted)} {"message was" if len(deleted) == 1 else "messages were"} removed.'

        await self.bot.say(message, delete_after=10)

    @remove.command(pass_context=True)
    async def embeds(self, ctx, search=50):
        """Removes messages with embedded content."""
        await self.do_removal(ctx.message, search, lambda e: len(e.embeds))

    @remove.command(pass_context=True)
    async def files(self, ctx, search=50):
        """Removes messages with attached files or embedded content."""
        await self.do_removal(ctx.message, search, lambda e: len(e.attachments) or len(e.embeds))

    @remove.command(name='all', pass_context=True)
    async def _remove_all(self, ctx, search=50):
        """Removes all messages. Be very careful with this."""
        await self.do_removal(ctx.message, search, lambda e: True)

    @remove.command(pass_context=True)
    async def user(self, ctx, member: discord.Member, search=50):
        """Removes all messages by the member."""
        await self.do_removal(ctx.message, search, lambda e: e.author == member)

    @remove.command(pass_context=True)
    async def contains(self, ctx, *, substr:str):
        """Removes all messages containing a substring of at least 3 characters."""
        if len(substr) < 3:
            await self.bot.say('The substring must be at least 3 characters long.')
            return
        await self.do_removal(ctx.message, 50, lambda e: substr in e.content)


def setup(bot):
    bot.add_cog(Admin(bot))
