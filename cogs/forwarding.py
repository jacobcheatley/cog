import discord
from discord.ext import commands

from .utils import config, checks


class Forwarding:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner = self.get_owner()

    def get_owner(self):
        return discord.utils.find(lambda m: m.id == config.owner_id, self.bot.get_all_members())

    async def send_to_owner(self, **kwargs):
        if self.owner is None:
            self.owner = self.get_owner()

        await self.bot.send_message(self.owner, **kwargs)

    async def on_message(self, message: discord.Message):
        if self.owner is None:
            self.owner = self.get_owner()

        if not message.channel.is_private or message.channel.user.id == self.owner.id:
            return

        embed = discord.Embed()
        if message.author == self.bot.user:
            embed.title = f'Sent PM to {message.channel.user.mention}.'
        else:
            embed.set_author(name=message.author, icon_url=message.author.avatar_url or message.author.default_avatar_url)
            embed.title = f'Received PM from {message.author.mention}'
        embed.description = message.content
        embed.timestamp = message.timestamp

        await self.send_to_owner(embed=embed)

    async def on_message_delete(self, message: discord.Message):
        embed = discord.Embed()
        embed.set_author(name=message.author, icon_url=message.author.avatar_url or message.author.default_avatar_url)
        embed.title = f'{message.author.mention}\'s message deleted in {message.server}#{message.channel}'
        embed.description = message.content
        embed.timestamp = message.timestamp

        await self.send_to_owner(embed=embed)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        embed = discord.Embed()
        embed.set_author(name=before.author, icon_url=before.author.avatar_url or before.author.default_avatar_url)
        embed.title = f'{before.author.mention}\'s message edited in {before.server}#{before.channel}'
        embed.add_field(name='Before', value=before.content, inline=False)
        embed.add_field(name='After', value=after.content, inline=False)
        embed.timestamp = before.timestamp

        await self.send_to_owner(embed=embed)

    @commands.command()
    @checks.is_owner()
    async def pm(self, user: discord.User, *, content: str):
        """PMs a person."""
        await self.bot.send_message(user, content)


def setup(bot):
    bot.add_cog(Forwarding(bot))
