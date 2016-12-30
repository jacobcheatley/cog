import discord
from discord.ext import commands
import random
import re


roll_pattern = re.compile(r'^(\d*)d(\d+)(?:(\+|-)(\d+))?')
question_split_pattern = re.compile(r'(?:,\W+or|or|,)\W+')


class Fun:
    """Commands that serve no real purpose."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, dice: str):
        """Rolls dice in the format NdX±C"""
        try:
            num_dice, size, sign, mod = roll_pattern.findall(dice)[0]
            dice_roll = sum((random.randint(1 if int(size) else 0, int(size)) for _ in range(int(num_dice or 1))))
            constant = (int(mod) if sign == '+' else -int(mod)) if mod else 0
            await self.bot.say('Rolled a {}'.format(dice_roll + constant))
        except Exception as e:
            print(e)
            await self.bot.say('Invalid dice format (NdX+C)')

    @commands.command()
    async def flip(self):
        """Flips a coin."""
        await self.bot.say(random.choice(['Heads', 'Tails']))

    @commands.command(aliases=['q'])
    async def question(self, *, question: str):
        """Answers a question - "Question? comma, separated or options" """
        parts = question.split('?')
        if len(parts) != 2:
            return await self.bot.say('Question was not in proper format.')
        options = question_split_pattern.split(parts[1])
        print(options)
        await self.bot.say(random.choice(options).strip())


def setup(bot):
    bot.add_cog(Fun(bot))
