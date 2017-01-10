import discord
from discord.ext import commands
from .utils import database, checks, config
import psutil
import datetime

status_emoji = {
    'online': ':green_heart:',
    'offline': ':black_heart:',
    'idle': ':yellow_heart:',
    'dnd': ':heart:'
}


class Info:
    """Gives information on various things."""

    def __init__(self, bot):
        self.bot = bot
        self.user_db = database.Database('user.json', loop=bot.loop)
        self.command_db = database.Database('command.json', loop=bot.loop)

    async def on_command(self, command, ctx):
        q_name = ctx.command.qualified_name
        count = self.command_db.get(q_name, 0) + 1
        await self.command_db.put(q_name, count)

    def get_member_info(self, member_id):
        return self.user_db.get(member_id, {})

    async def save_member_info(self, member_id, info):
        await self.user_db.put(member_id, info)

    async def show_whois(self, member: discord.Member):
        embed = discord.Embed()
        # Discord Info
        embed.set_author(name=f'{member.display_name}#{member.discriminator}', icon_url=member.avatar_url or member.default_avatar_url,
                         url=member.avatar_url or member.default_avatar_url)
        embed.colour = member.colour
        embed.add_field(name='Username', value=member.name)
        embed.add_field(name='Nickname', value=member.nick)
        embed.add_field(name='ID', value=member.id)
        embed.add_field(name='Join Date', value=member.joined_at.strftime('%d %B %Y'))
        status = str(member.status)
        embed.add_field(name='Status', value=f'{status_emoji[status]} **{status.upper()}**')
        # Custom Info
        member_info = self.get_member_info(member.id)
        embed.add_field(name='Real Name', value=member_info.get('name', 'Not set.'))
        embed.add_field(name='Description', value=member_info.get('desc', 'Not set.'), inline=False)
        for name, value in member_info.get('other', {}).items():
            embed.add_field(name=name, value=value)

        await self.bot.say(embed=embed)

    @commands.command()
    async def whois(self, *, member: discord.Member):
        """Gives information about the member."""
        await self.show_whois(member)

    @whois.error
    async def whois_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('You need to supply a member.', delete_after=10)

    @commands.command(pass_context=True, hidden=True)
    async def whoami(self, ctx: commands.Context):
        """Gives information about yourself."""
        await self.show_whois(ctx.message.author)

    async def _setbasic(self, member: discord.Member, field: str, value: str):
        member_info = self.get_member_info(member.id)
        member_info[field] = value
        await self.save_member_info(member.id, member_info)

    @commands.command(pass_context=True)
    async def setname(self, ctx: commands.Context, *, name: str):
        """Sets your name for whois information.
        See also: setdesc, setfield, removefield"""
        member = ctx.message.author
        await self._setbasic(member, 'name', name)
        await self.bot.say('Updated your name.', delete_after=10)

    @commands.command(pass_context=True, hidden=True, aliases=['setdescription'])
    async def setdesc(self, ctx: commands.Context, *, desc: str):
        """Sets your description for whois information."""
        member = ctx.message.author
        await self._setbasic(member, 'desc', desc)
        await self.bot.say('Updated your description.', delete_after=10)

    @commands.command(pass_context=True, hidden=True, aliases=['addfield'])
    async def setfield(self, ctx: commands.Context, field: str, *, value: str):
        """Sets a custom field for whois information.
        You can have a maximum of 3 custom fields at a time.
        You have to remove one (with removefield) if you want to add another."""
        member = ctx.message.author
        member_info = self.get_member_info(member.id)
        if 'other' not in member_info:
            member_info['other'] = {}

        if field not in member_info['other'] and len(member_info['other']) >= 3:
            await self.bot.say('You already have 3 custom fields. Consider removing one.', delete_after=10)
        else:
            member_info['other'][field] = value
            await self.save_member_info(member.id, member_info)
            await self.bot.say(f'Updated your custom field "{field}".', delete_after=10)

    @commands.command(pass_context=True, hidden=True, aliases=['deletefield'])
    async def removefield(self, ctx: commands.Context, *, field: str):
        """Removes a custom field in your whois information.
        The name should match exactly."""
        member = ctx.message.author
        member_info = self.get_member_info(member.id)
        try:
            del member_info['other'][field]
            await self.save_member_info(member.id, member_info)
            await self.bot.say(f'Removed your custom field "{field}".', delete_after=10)
        except KeyError:
            await self.bot.say(f'Field "{field}" not found.', delete_after=10)
        except:
            pass

    @commands.command(no_pm=True, aliases=['setnameother'])
    @checks.permissions(manage_nicknames=True, manage_messages=True)
    async def setothername(self, member: discord.Member, *, name: str):
        """Sets the name of another user's whois information.
        This requires manage nicknames and manage messages permissions.
        See also: setotherdesc, setotherfield, removeotherfield"""
        await self._setbasic(member, 'name', name)
        await self.bot.say(f'Name for member {member} updated.')

    @commands.command(no_pm=True, hidden=True, aliases=['setotherdescription', 'setdescother', 'setdescriptionother'])
    @checks.permissions(manage_nicknames=True, manage_messages=True)
    async def setotherdesc(self, member: discord.Member, *, desc: str):
        """Sets the description of another user's whois information.
        This requires manage nicknames and manage messages permissions."""
        await self._setbasic(member, 'desc', desc)
        await self.bot.say(f'Description for member {member} updated.')

    @commands.command(no_pm=True, hidden=True, aliases=['setfieldother'])
    @checks.permissions(manage_nicknames=True, manage_messages=True)
    async def setotherfield(self, member: discord.Member, field: str, *, value: str):
        """Sets the value of a custom field for another user's whois information.
        This requires manage nicknames and manage messages permissions.

        A user can have a maximum of 3 custom fields at a time.
        You have to remove one if you want to add another."""
        member_info = self.get_member_info(member.id)
        if 'other' not in member_info:
            member_info['other'] = {}

        if field not in member_info['other'] and len(member_info['other']) >= 3:
            await self.bot.say('That user already have 3 custom fields. Consider deleting one.', delete_after=10)
        else:
            member_info['other'][field] = value
            await self.save_member_info(member.id, member_info)
            await self.bot.say(f'Updated {member}\'s custom field "{field}".', delete_after=10)

    @commands.command(no_pm=True, hidden=True, aliases=['deleteotherfield', 'removefieldother', 'deletefieldother'])
    @checks.permissions(manage_nicknames=True, manage_messages=True)
    async def removeotherfield(self, member: discord.Member, *, field: str):
        """Deletes a custom field for another user's whois information.
        This requires manage nicknames and manage messages permissions."""
        member_info = self.get_member_info(member.id)
        try:
            del member_info['other'][field]
            await self.save_member_info(member.id, member_info)
            await self.bot.say(f'Removed {member}\'s custom field "{field}".', delete_after=10)
        except KeyError:
            await self.bot.say(f'Field "{field}" not found for {member}.', delete_after=10)
        except:
            pass

    def get_bot_uptime(self, *, brief=False):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                return f'{days} days, {hours} hours, {minutes} minutes and {seconds} seconds'
            else:
                return f'{hours} hours, {minutes} minutes and {seconds} seconds'
        else:
            if days:
                return f'{days}d {hours}h {minutes}m {seconds}s'
            else:
                return f'{hours}h {minutes}m {seconds}s'

    @commands.command(hidden=True)
    async def uptime(self):
        """Tells you how long Cog has been clanking away."""
        await self.bot.say(f'Uptime: **{self.get_bot_uptime()}**')

    @commands.command(aliases=['whoareyou', 'stats'])
    async def about(self):
        """Displays a whole bunch of information about Cog."""
        embed = discord.Embed()
        # Top
        embed.title = 'Cog Bot'
        embed.description = f'Made by <@!{config.owner_id}>.'
        embed.set_author(name=str(self.bot.user), icon_url=self.bot.user.avatar_url or self.bot.user.default_avatar_url)
        embed.colour = 0x738bd7

        # Fields
        memory_usage = psutil.Process().memory_full_info().uss / 1024**2

        embed.add_field(name='Uptime', value=self.get_bot_uptime(brief=True))
        embed.add_field(name='Commands Run', value=sum(self.command_db.all().values()))
        embed.add_field(name='Memory Usage', value=f'{memory_usage:.2f} MiB')
        embed.add_field(name='Source', value='https://github.com/jacobcheatley/cog')

        # Bottom
        embed.timestamp = self.bot.uptime

        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
