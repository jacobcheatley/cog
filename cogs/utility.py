import inspect
import io
import traceback
import unicodedata
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from .utils import checks


class Utility:
    """Various miscellaneous 'helpful' commands."""

    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    async def show_quote(self, message: discord.Message, quoter: discord.Member):
        embed = discord.Embed()
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url or message.author.default_avatar_url)
        embed.description = message.content
        embed.set_footer(text=f'Quoted by {quoter}', icon_url=quoter.avatar_url or quoter.default_avatar_url)
        embed.colour = 0x738bd7
        embed.timestamp = message.timestamp
        await self.bot.send_message(destination=message.channel, embed=embed)

    async def on_reaction_add(self, reaction: discord.Reaction, member: discord.Member):
        quote_emoji = ['\N{SPEECH BALLOON}', '\N{LEFT SPEECH BUBBLE}']

        if reaction.emoji in quote_emoji:
            await self.show_quote(reaction.message, member)

    @commands.command(hidden=True)
    async def charinfo(self, *, characters: str):
        """Shows information about some characters.

        Max 15 at a time."""

        if len(characters) > 15:
            await self.bot.say(f'Too many characters ({len(characters)}/15).')

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        await self.bot.say('\n'.join(map(to_string, characters)))

    @commands.command(name='eval', hidden=True, pass_context=True)
    @checks.is_owner()
    async def _eval(self, ctx: commands.Context, *, expr: str):
        """Evalutes a Python 3.6.0 expression."""
        try:
            await self.bot.say(eval(expr))
        except Exception as e:
            await self.bot.whisper(f'{type(e).__name__} - {e}')

    @staticmethod
    def cleanup_code(content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(e):
        return '```python\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def repl(self, ctx: commands.Context):
        """Starts a REPL session."""
        message = ctx.message

        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': message,
            'server': message.server,
            'channel': message.channel,
            'author': message.author,
            '_': None
        }

        if message.channel.id in self.sessions:
            return await self.bot.say('Already running a REPL session in this channel.', delete_after=10)

        self.sessions.add(message.channel.id)

        await self.bot.say('Enter code to execute or eval.', delete_after=10)

        while True:
            response = await self.bot.wait_for_message(author=message.author, channel=message.channel, check=lambda m: m.content.startswith('`'))
            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit' or 'exit()'):
                self.sessions.remove(message.channel.id)
                return await self.bot.say('Exiting', delete_after=10)

            executor = exec
            if cleaned.count('\n') == 0:
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await self.bot.say(self.get_syntax_error(e))
                    continue

            variables['message'] = response
            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```python\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```python\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```python\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await self.bot.send_message(message.channel, 'Content too long to print.')
                    else:
                        await self.bot.send_message(message.channel, fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await self.bot.send_message(message.channel, f'Unexpected error: `{e}`')


def setup(bot):
    bot.add_cog(Utility(bot))
