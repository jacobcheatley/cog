import discord
from discord.ext import commands
from .utils import funcs
from PIL import Image, ImageFont, ImageDraw
import io
import re
import textwrap


def final(image: Image, fmt='png', **kwargs):
    result = io.BytesIO()
    image.save(result, fmt, **kwargs)
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
            await self.bot.upload(final(image), filename='colour.png', content=colour)
        else:
            await self.bot.say('Couldn\'t understand that colour format. U WOT M8.', delete_after=10)

    def reline(self, text, width, max_lines):
        wrapped = textwrap.wrap(text, width=width)
        if len(wrapped) <= max_lines:
            return wrapped

        wrapped = wrapped[:max_lines]
        wrapped[-1] += '...'
        return wrapped

    @commands.command()
    async def retarded(self, *, text: str):
        """Makes a comic with text and that cute retarded dog."""

        image = Image.open('resource/retarded.png')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Times_New_Roman_Bold.ttf', 26)
        lines = self.reline(text, 25, 6)
        draw.text((340, 120-21*len(lines)), '\n'.join(lines), font=font)

        await self.bot.upload(final(image), filename='retarded.png')

    async def get_recent_images(self, channel):
        async for message in self.bot.logs_from(channel, limit=10):
            to_check = [message.attachments, message.embeds]
            for _list in to_check:
                if _list:
                    if 'width' in _list[0] or ('type' in _list[0] and _list[0]['type'] == 'image'):
                        url = _list[0]['url']
                        yield url

    async def do_jpegify(self, url):
        b = await funcs.bytes_download(url)
        if not b:
            await self.bot.say('Failed to parse data from URL.', delete_after=10)
            return False
        try:
            image = Image.open(b)
        except:
            await self.bot.say('Failed to parse data from URL.', delete_after=10)
            return False
        else:
            o_size = image.size
            image = image.resize((image.size[0]//2, image.size[1]//2)).resize(o_size)
            result = final(image, 'jpeg', quality=1)
            return result

    @commands.command(pass_context=True, aliases=['jpegify', 'jpeg'])
    async def needsmorejpeg(self, ctx: commands.Context, url: str = None):
        """Makes an image into a low quality jpeg. URL, attachment or recent images."""

        if url:
            result = await self.do_jpegify(url)
            if result is not False:
                await self.bot.upload(result, filename='doilooklikeiknowwhatthisis.jpg')
        else:
            async for url in self.get_recent_images(ctx.message.channel):
                result = await self.do_jpegify(url)
                if result is not False:
                    await self.bot.upload(result, filename='doilooklikeiknowwhatthisis.jpg')
                return
        await self.bot.say('Couldn\'t find an image.', delete_after=10)


def setup(bot):
    bot.add_cog(Images(bot))
