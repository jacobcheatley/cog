import discord
from discord.ext import commands
from PIL import Image
import io
import re


def final(image: Image):
    result = io.BytesIO()
    image.save(result, 'png')
    result.seek(0)
    return result

# Regexes
hex_digits = '([0-9a-fA-F]{2})'
HEX = re.compile('#{0}{0}{0}'.format(hex_digits))
rgb_num = '(\d{1,3})'
RGB = re.compile('{0}\s{0}\s{0}'.format(rgb_num))


class Images:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['color'])
    async def colour(self, *, colour: str):
        """Displays a block of a colour (hex or rgb).

        Supported formats:
        Hex: #000000
        RGB: 255 255 255"""

        result = None

        if HEX.match(colour):
            match = HEX.match(colour)
            result = tuple(int('0x{}'.format(c), 16) for c in match.groups())
        elif RGB.match(colour):
            match = RGB.match(colour)
            result = tuple(int(c) for c in match.groups())

        if result is not None:
            image = Image.new('RGB', (128, 128), result)
            await self.bot.upload(final(image), filename='test.png', content=colour)
        else:
            await self.bot.say('Couldn\'t understand that colour format. U WOT M8.', delete_after=10)


def setup(bot):
    bot.add_cog(Images(bot))
