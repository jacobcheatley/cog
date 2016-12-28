import discord
from discord.ext import commands


class Info:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Info(bot))
