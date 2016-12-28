import discord
from discord.ext import commands


class Search:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Search(bot))
