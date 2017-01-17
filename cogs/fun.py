import discord
from discord.ext import commands
from .utils import paginator
import random
import re
import math

roll_pattern = re.compile(r'^([+-]?\d+)?d(\d+)([+-]?\d+)?(adv|dis)?$')
repeat_pattern = re.compile(r'^(?:repeat|r|rep)(\d+)$')
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
        ["【", "】"], ["﴾", "﴿"], ["|"], ["-(", ")╯╲___卍卍卍卍"], ["/\\\\/\\\\(", ")/\\\\/\\\\"], ["︵‿︵(", ")︵‿︵"],
        ["[̲̅$̲̅(̲̅", ")̲̅$̲̅]"], ["(╯ ", ") ╯︵ ┻━┻"], ["(╭🤙", ")╭🤙"]]


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

    @commands.command(aliases=['r'])
    async def roll(self, *, dice: str = 'd20'):
        """Rolls dice with advanced formatting. For D&D.

        Format: (Nd)X(±C). Things in () are optional.
        Include adv or dis after the dice format for advantage/disadvantage.
        To do math with multiple sets of dice, use commas.
        You can repeat the roll multiple times by adding rn to the end after a comma.
        e.g.
        !roll 1d20+2 -> self explanatory
        !roll 1d20 dis -> rolls 1d20 with disadvantage
        !roll 1d20+2, + 1d4 -> rolls 1d20+2, then adds another 1d4
        !roll 1d10 adv, - 1d8 -> rolls 1d10 with advantage, then removes 1d8
        !roll 1d10 adv, - 1d8,r3 -> same as above but the roll will be performed 3 times"""

        to_roll = []
        dice_groups = dice.replace(' ', '').split(',')
        repeat = 1
        for i, dice_group in enumerate(dice_groups):
            match = roll_pattern.match(dice_group)
            # Group 1 = Number of Dice (+ or -) (optional)
            # Group 2 = Value of Dice
            # Group 3 = Modifier (+ or -) (optional)
            # Group 4 = Adv/Dis (optional)
            if match:
                num = 1 if match.group(1) is None else int(match.group(1))
                value = int(match.group(2))
                mod = 0 if match.group(3) is None else int(match.group(3))
                adv = match.group(4)
                to_roll.append((num, value, mod, adv))
            elif i == len(dice_groups) - 1:
                match = repeat_pattern.match(dice_group)
                if not match:
                    return await self.bot.say(f'Invalid dice/repeat format "{dice_group}"')
                repeat = int(match.group(1))
                if repeat < 1:
                    return await self.bot.say('Repeat value cannot be 0')
            else:
                return await self.bot.say(f'Invalid dice format "{dice_group}"', delete_after=10)

        embed = discord.Embed()
        embed.set_author(name='D&D Dice Roller', icon_url='http://i.imgur.com/FT8VXRQ.png')
        embed.colour = 0xe51e25

        for _ in range(repeat):
            totals = []

            for index, roll_me in enumerate(to_roll):
                string_parts = []
                subtotals = []

                # Roll once or twice
                for reroll in range(2 if roll_me[3] is not None else 1):
                    rolls = [random.randint(1, roll_me[1]) for _ in range(abs(roll_me[0]))]
                    total_rolls = int(math.copysign(1, roll_me[0])) * sum(rolls)
                    subtotal = total_rolls + roll_me[2]
                    subtotals.append(subtotal)
                    string_parts.append(self.roll_format(rolls, roll_me[2], subtotal, roll_me[1]))

                # Choose and format for advantage/disadvantage
                if roll_me[3] is not None:
                    if roll_me[3] == 'adv':
                        chosen_index = subtotals.index(max(subtotals))
                    else:
                        chosen_index = subtotals.index(min(subtotals))
                    lost_index = 0 if chosen_index == 1 else 1

                    totals.append(subtotals[chosen_index])
                    string_parts[lost_index] = f'~~{string_parts[lost_index]}~~'
                else:
                    totals.append(subtotals[0])

                # Final formatting and adding to embed
                prefix = 'Rolling' if index == 0 else 'Plus' if roll_me[0] > 0 else 'Minus'
                embed.add_field(name=f'{prefix} {self.dice_format(*roll_me)}', value='\n'.join(string_parts))

            if len(totals) > 1:
                embed.add_field(name='Final',
                                value=''.join('{0:+}'.format(x) for x in totals) + f' = **{sum(totals)}**',
                                inline=False)

        await self.bot.say(embed=embed)

    @staticmethod
    def dice_format(num, value, mod, adv):
        adv_string = '' if adv is None else ' with advantage' if adv == 'adv' else ' with disadvantage'
        return f'{abs(num)}d{value}{mod:+}{adv_string}'

    @staticmethod
    def roll_format(rolls, mod, total, max):
        rolls_string = ', '.join(str(roll) for roll in rolls) if mod or len(rolls) > 1 else ''
        mod = f' {"+" if mod > 0 else "-"} {abs(mod)}' if mod != 0 else ''
        final = f' = **{abs(total)}**'
        if len(rolls) == 1 and max == 20:
            crit = ' ***CRITICAL SUCCESS***' if rolls[0] == 20 else ' ***CRITICAL FAILURE***' if rolls[0] == 1 else ''
        else:
            crit = ''

        return f'{rolls_string}{mod}{final}{crit}'

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

    @commands.group(aliases=['t'], invoke_without_command=True)
    async def text(self, modifiers: str, *, text: str):
        """A variety of ways to modify text to make it D A N K.

        Possible modifiers:
          aesthetic/a   = A E S T H E T I C
          leet/1337/l   = 1337 5P34K
          emoji/e       = lul xd emoji
          clap/c/:clap: = STOP :clap: APPROPRIATING :clap: BLACK :clap: CULTURE
          upsidedown/u  = uʍop ǝpısdn
          binary/b/0/1  = 01100010 01101001 01101110 01100001 01110010 01111001
        To combine multiple modifiers just comma separate them with no spaces."""
        mapping = [
            ({'aesthetic', 'a'}, self.aesthetic),
            ({'leet', '1337', 'l'}, self.leet),
            ({'emoji', 'e'}, self.emoji),
            ({'clap', 'c', '\U0001f44f'}, self.clap),
            ({'upsidedown', 'u'}, self.upsidedown),
            ({'binary', 'b', '0', '1'}, self.binary)
        ]

        mod_list = modifiers.lower().split(',')
        for mod in mod_list:
            found = False
            for key, func in mapping:
                if mod in key:
                    text = func(text)
                    found = True
                    break
            if not found:
                return await self.bot.say(f'Couldn\'t find the modifier "{mod}"', delete_after=10)
            if len(text) > 2000:
                break

        if len(text) > 2000:
            await self.bot.say(text[:1997] + '...')
        else:
            await self.bot.say(text)

    @staticmethod
    def aesthetic(text: str):
        return ' '.join((c for c in text.upper()))

    @staticmethod
    def leet(text: str):
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

        return ''.join((get_replacement(c) for c in text.upper()))

    @staticmethod
    def emoji(text: str):
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

        return ''.join((get_replacement(c) for c in text.lower()))

    @staticmethod
    def clap(text: str):
        return text.replace(' ', '\U0001f44f') + random.randint(1, 5) * '\U0001f44f'

    @staticmethod
    def upsidedown(text: str):
        replacements = {
            'a': '\u0250',
            'b': 'q',
            'c': '\u0254',
            'd': 'p',
            'e': '\u01DD',
            'f': '\u025F',
            'g': 'b',
            'h': '\u0265',
            'i': '\u0131',
            'j': '\u0638',
            'k': '\u029E',
            'l': '\u05DF',
            'm': '\u026F',
            'n': 'u',
            'o': 'o',
            'p': 'd',
            'q': 'b',
            'r': '\u0279',
            's': 's',
            't': '\u0287',
            'u': 'n',
            'v': '\u028C',
            'w': '\u028D',
            'x': 'x',
            'y': '\u028E',
            'z': 'z',
            '[': ']',
            ']': '[',
            '(': ')',
            ')': '(',
            '{': '}',
            '}': '{',
            '<': '>',
            '>': '<',
            '?': '\u00BF',
            '\u00BF': '?',
            '\'': ',',
            ',': '\'',
            '!': '\u00A1',
            '.': '\u02D9',
            '_': '\u203E',
            ';': '\u061B',
            '9': '6',
            '6': '9',
        }

        def get_replacement(c: str):
            if c in replacements:
                return replacements[c]
            return c

        return ''.join(get_replacement(c.lower()) for c in reversed(text))

    @staticmethod
    def binary(text: str):
        return ' '.join('{0:08b}'.format(ord(c)) for c in text)


def setup(bot):
    bot.add_cog(Fun(bot))
