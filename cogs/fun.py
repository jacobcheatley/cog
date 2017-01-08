import discord
from discord.ext import commands
from .utils import paginator
import random
import re

roll_pattern = re.compile(r'^(\d*)d(\d+)(?:(\+|-)(\d+))?')
question_split_pattern = re.compile(r'(?:,\W+or|or|,)\W+')

mouths = [[" ͜ʖ"], ["v"], ["ᴥ"], ["ᗝ"], ["Ѡ"], ["ᗜ"], ["Ꮂ"], ["ᨓ"], ["ᨎ"], ["ヮ"], ["╭͜ʖ╮"], [" ͟ل͜"], [" ͟ʖ"], [" ʖ̯"],
          ["ω"], [" ³"], [" ε "], ["﹏"], ["□"], ["ل͜"], ["‿"], ["╭╮"], ["‿‿"], ["▾"], ["‸"], ["Д"], ["∀"], ["!"],
          ["人"], ["."], ["ロ"], ["_"], ["෴"], ["ꔢ"], ["ѽ"], ["ഌ"], ["⏠"], ["⏏"], ["⍊"], ["⍘"], ["ツ"], ["益"], ["╭∩╮"],
          ["Ĺ̯"], ["◡"], [" ͜つ"], ["◞ "], ["ヘ"]]
eyes = [[" ͡°"], ["⌐■", "■"], [" ͠°", " °"], ["⇀", "↼"], ["´• ", " •`"], ["´", "`"], ["`", "´"], ["ó", "ò"], ["ò", "ó"],
        ["⸌", "⸍"], ["\u003e", "\u003c"], ["Ƹ̵̡", "Ʒ"], ["ᗒ", "ᗕ"], ["⟃", "⟄"], ["⪧", "⪦"], ["⪦", "⪧"], ["⪩", "⪨"],
        ["⪨", "⪩"], ["⪰", "⪯"], ["⫑", "⫒"], ["⨴", "⨵"], ["⩿", "⪀"], ["⩾", "⩽"], ["⩺", "⩹"], ["⩹", "⩺"], ["◥▶", "◀◤"],
        ["◍", "◎"], ["/͠-", " ͝-\\"], ["⌣", "⌣”"], [" ͡⎚", " ͡⎚"], ["≋"], ["૦ઁ"], ["  ͯ"], ["  ͌"], ["ꗞ"], ["ꔸ"],
        ["꘠"], ["ꖘ"], ["܍"], ["ළ"], ["◉"], ["☉"], ["・"], ["▰"], ["ᵔ"], [" ﾟ"], ["□"], ["☼"], ["*"], ["`"], ["⚆"],
        ["⊜"], ["\u003e"], ["❍"], ["￣"], ["─"], ["✿"], ["•"], ["T"], ["^"], ["ⱺ"], ["@"], ["ȍ"], ["  "], ["  "],
        ["x"], ["-"], ["$"], ["Ȍ"], ["ʘ"], ["Ꝋ"], [""], [""], ["⸟"], ["๏"], ["ⴲ"], ["■"], [" ﾟ"], ["◕"], ["◔"],
        ["✧"], ["■"], ["♥"], ["¬"], [" º "], ["⨶"], ["⨱"], ["⏓"], ["⏒"], ["⍜"], ["⍤"], ["ᚖ"], ["ᴗ"], ["ಠ"],
        ["σ"], ["☯"], ["の"], ["￢ "]]
ears = [["(", ")"], ["q", "p"], ["ʢ", "ʡ"], ["⸮", "?"], ["ʕ", "ʔ"], ["ᖗ", "ᖘ"], ["ᕦ", "ᕥ"], ["ᕦ(", ")ᕥ"], ["ᕙ(", ")ᕗ"],
        ["ᘳ", "ᘰ"], ["ᕮ", "ᕭ"], ["ᕳ", "ᕲ"], ["[", "]"], ["¯\\_", "_/¯"], ["୧", "୨"], ["୨", "୧"],
        ["⤜(", ")⤏"], ["☞", "☞"], ["(╭☞", ")╭☞"], ["ᑫ", "ᑷ"], ["ᑴ", "ᑷ"], ["ヽ(", ")ﾉ"], ["\\(", ")/"], ["乁(", ")ㄏ"],
        ["└[", "]┘"], ["(づ", ")づ"], ["(ง", ")ง"], ["⎝", "⎠"], ["ლ(", "ლ)"], ["ᕕ(", ")ᕗ"], ["(∩", ")⊃━☆ﾟ.*"],
        ["【", "】"], ["﴾", "﴿"], ["|"]]


def build_lenny(mouth, eye, ear):
    mouth %= len(mouths)
    eye %= len(eyes)
    ear %= len(ears)
    m_part = mouths[mouth]
    i_part = eyes[eye]
    e_part = ears[ear]
    return f'{e_part[0]}{i_part[0]}{m_part[0]}{i_part[1 % len(i_part)]}{e_part[1 % len(e_part)]}'


def format_lenny_part(part, mouth=False):
    if mouth:
        return part[0]
    else:
        return part[0] + ' ' + part[1 % len(part)]


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

    @commands.command(aliases=['q', '?'])
    async def question(self, *, question: str):
        """Answers a question - "Question? comma, separated or options" """
        parts = question.split('?')
        if len(parts) != 2:
            return await self.bot.say('Question was not in proper format.')
        options = question_split_pattern.split(parts[1])
        print(options)
        await self.bot.say(random.choice(options).strip())

    @commands.group(invoke_without_command=True)
    async def lenny(self, mouth: int = 1, eye: int = 1, ear: int = 1):
        """Makes a lenny face with custom mouth eyes and ears."""
        await self.bot.say(build_lenny(mouth - 1, eye - 1, ear - 1))

    @lenny.command(name='random')
    async def lenny_random(self):
        """Makes a lenny out of random components."""
        mouth = random.randrange(len(mouths))
        eye = random.randrange(len(eyes))
        ear = random.randrange(len(ears))
        await self.bot.say(build_lenny(mouth, eye, ear))

    @lenny.command(name='mouths', pass_context=True)
    async def lenny_mouths(self, ctx: commands.Context):
        """Displays all the possible mouths."""
        p = paginator.Pages(self.bot, message=ctx.message, entries=[format_lenny_part(part, mouth=True) for part in mouths])
        p.embed.colour = 0x738bd7
        await p.paginate()

    @lenny.command(name='eyes', pass_context=True)
    async def lenny_eyes(self, ctx: commands.Context):
        """Displays all the possible eyes."""
        p = paginator.Pages(self.bot, message=ctx.message, entries=[format_lenny_part(part) for part in eyes])
        p.embed.colour = 0x738bd7
        await p.paginate()

    @lenny.command(name='ears', pass_context=True)
    async def lenny_ears(self, ctx: commands.Context):
        """Displays all the possible ears."""
        p = paginator.Pages(self.bot, message=ctx.message, entries=[format_lenny_part(part) for part in ears])
        p.embed.colour = 0x738bd7
        await p.paginate()

    @commands.group(aliases=['t'])
    async def text(self):
        """A variety of subcommands for modifying text in D A N K ways."""
        pass

    @text.command(aliases=['a'])
    async def aesthetic(self, *, text: str):
        """A E S T H E T I C"""
        result = ' '.join((c for c in text.upper()))
        await self.bot.say(result)

    @text.command(aliases=['1337', 'l'])
    async def leet(self, *, text: str):
        """1337 5P34K"""
        replacements = {
            'A': '4',
            'B': ['|3', 'B'],
            'C': ['<', 'C'],
            'D': ['|)', 'D'],
            'E': '3',
            'I': '1',
            'L': '|',
            'M': [r'/\\/\\', 'M'],
            'N': [r'|\\|', 'N'],
            'O': '0',
            'S': ['5', '$'],
            'T': '7',
            'V': [r'\\/', 'V'],
            'W': [r'\\/\\/', 'W'],
            'X': ['><', 'X', 'xx'],
            'Z': '2'
        }

        def get_replacement(c: str):
            if c in replacements:
                if isinstance(replacements[c], str):
                    return replacements[c]
                return random.choice(replacements[c])
            return random.choice([c, c.lower()])

        result = ''.join((get_replacement(c) for c in text.upper()))
        await self.bot.say(result)

    @text.command(aliases=['e'])
    async def emoji(self, *, text: str):
        """lul xd emoji"""
        replacements = {
            '1': ':one:',
            '2': ':two:',
            '3': ':three:',
            '4': ':four:',
            '5': ':five:',
            '6': ':six:',
            '7': ':seven:',
            '8': ':eight:',
            '9': ':nine:',
            '0': ':zero:',
            '!': ':exclamation:',
            '?': ':question:',
            '<': ':arrow_backward:',
            '>': ':arrow_forward:',
            '^': ':arrow_up_small:',
            '+': ':heavy_plus_sign:',
            '-': ':heavy_minus_sign:',
            '/': ':heavy_division_sign:',
            '*': ':heavy_multiplication_x:'
        }

        def get_replacement(c: str):
            if c in 'abcdefghijklmnopqrstuvwxyz':
                return f':regional_indicator_{c}:'
            elif c in replacements:
                return replacements[c]
            return c

        result = ''.join((get_replacement(c) for c in text.lower()))
        await self.bot.say(result)

    @text.command(aliases=['c', '\U0001f44f'])
    async def clap(self, *, text: str):
        """STOP :clap: APPROPRIATING :clap: BLACK :clap: CULTURE"""
        await self.bot.say(text.replace(' ', '\U0001f44f'))


def setup(bot):
    bot.add_cog(Fun(bot))
