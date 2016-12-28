import discord
from discord.ext import commands


class Forwarding:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Forwarding(bot))
