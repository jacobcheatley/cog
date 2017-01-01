import discord
from discord.ext import commands
import re


r_regex = re.compile(r'(?:^|\s)/(u|r)/(\S+)')


class Replies:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        if message.content.startswith(self.bot.command_prefix) or message.author.id == self.bot.user.id:
            return

        subs = None

        r_matches = r_regex.findall(message.content)
        if r_matches:
            print(r_matches)
            subs = ['https://www.reddit.com/{}/{}'.format(*sub) for sub in r_matches]

        if subs:
            await self.bot.send_message(message.channel, '\n'.join(subs))


def setup(bot):
    bot.add_cog(Replies(bot))
