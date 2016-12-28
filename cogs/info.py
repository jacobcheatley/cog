import discord
from discord.ext import commands
import re

from discord.ext.commands import CommandError

_mentions_transforms = discord.ext.commands.bot._mentions_transforms
_mention_pattern = discord.ext.commands.bot._mention_pattern


class Info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def help(self, ctx, *_commands: str):
        """Shows the help message. You've probably used it."""

        def repl(obj):
            return _mentions_transforms.get(obj.group(0), '')

        if len(_commands) == 0:
            embed = self._default_help(ctx)

        elif len(_commands) == 1:
            name = _mention_pattern.sub(repl, _commands[0])
            command = None

            if name in self.bot.cogs:
                command = self.bot.cogs[name]
            else:
                command = self.bot.commands.get(name)
                if command is None:
                    await self.bot.say(f'Command {name} not found.')
                    return

            embed = self._command_help(ctx, command)

        else:
            name = _mention_pattern.sub(repl, _commands[0])
            command = self.bot.commands.get(name)
            if command is None:
                await self.bot.say(f'Command {name} not found.')
                return

            for key in _commands[1:]:
                try:
                    key = _mention_pattern.sub(repl, key)
                    command = command.commands.get(key)
                    if command is None:
                        await self.bot.say(f'Command {name} not found.')
                        return
                except AttributeError:
                    await self.bot.say(f'Command {command} has no subcommands.')

            embed = None

        await self.bot.say(embed=embed)

    def _default_help(self, ctx):
        # Sets up embed
        result = discord.Embed()
        result.set_author(name=f'{self.bot.user.name} Help', icon_url=self.bot.user.avatar_url, url='')
        result.description = self.bot.description

        # Figures out which commands to display
        def predicate(command):
            if command.hidden:
                return False

            try:
                return command.can_run(ctx) and self.bot.can_run(ctx)
            except CommandError:
                return False

        commands_dict = {}

        for command_name, command in self.bot.commands.items():
            if predicate(command):
                cog = command.cog_name
                if cog not in commands_dict:
                    commands_dict[cog] = []
                commands_dict[cog].append((command_name, command.short_doc))

        for cog, commands_list in commands_dict.items():
            commands_list = ['{0[0]}: *{0[1]}*'.format(c) for c in commands_list]
            result.add_field(name=cog, value='\n'.join(commands_list), inline=False)

        print(commands_dict)

        return result

    def _command_help(self, ctx, command):
        result = discord.Embed()
        return result


def setup(bot):
    bot.add_cog(Info(bot))
