import discord
from discord.ext import commands
from .utils import database, config, paginator
import json
import datetime
import difflib


class TagInfo:
    __slots__ = ('name', 'content', 'owner', 'uses', 'created_at')

    def __init__(self, name, content, owner, **kwargs):
        self.name = name
        self.content = content
        self.owner = owner
        self.uses = kwargs.pop('uses', 0)
        self.created_at = kwargs.pop('created_at', 0.0)

    def __str__(self):
        return self.content

    async def embed(self, ctx, db):
        embed = discord.Embed()
        embed.title = self.name
        embed.add_field(name='Owner', value=f'<@!{self.owner}>')
        embed.add_field(name='Uses', value=self.uses)

        ranked = sorted(db.all().values(), key=lambda t: t.uses, reverse=True)
        try:
            embed.add_field(name='Rank', value=ranked.index(self) + 1)
        except:
            embed.add_field(name='Rank', value='Unknown')

        if self.created_at:
            embed.timestamp = datetime.datetime.fromtimestamp(self.created_at)

        owner = discord.utils.find(lambda m: m.id == self.owner, ctx.bot.get_all_members())
        if owner is None:
            owner = await ctx.bot.get_user_info(self.owner)

        embed.set_author(name=str(owner), icon_url=owner.avatar_url or owner.default_avatar_url)

        return embed


class TagEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TagInfo):
            payload = {
                attr: getattr(obj, attr)
                for attr in TagInfo.__slots__
                }
            payload['__tag__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)


def tag_decoder(obj):
    if '__tag__' in obj:
        return TagInfo(**obj)
    return obj


class Tags:
    """Tag related commands (o rly?)"""

    def __init__(self, bot):
        self.bot = bot
        self.db = database.Database('tags.json', encoder=TagEncoder, object_hook=tag_decoder, loop=bot.loop,
                                    load_later=True)

    @staticmethod
    def clean_tag_content(content):
        return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')

    def get_tag(self, name):
        all_tags = self.db.all()
        try:
            return all_tags[name]
        except KeyError:
            possible_matches = difflib.get_close_matches(name, tuple(all_tags.keys()))
            if not possible_matches:
                raise RuntimeError('Tag not found.')
            nl = '\n'
            raise RuntimeError(f'Tag not found. Did you mean...\n{nl.join(possible_matches)}')

    @commands.group(invoke_without_command=True)
    async def tag(self, *, name: str):
        """Tag text to be retrieved later.

        If a subcommand is not called, this will search for the tag with the given name and display it."""

        lookup = name.lower()
        try:
            tag = self.get_tag(lookup)
        except RuntimeError as e:
            return await self.bot.say(e)

        tag.uses += 1
        await self.bot.say(tag)

        await self.db.put(tag.name, tag)

    @tag.error
    async def tag_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('You need to pass in a tag name.', delete_after=10)

    def verify_lookup(self, lookup):
        if '@everyone' in lookup or '@here' in lookup:
            raise RuntimeError('That tag is using blocked words.')

        if not lookup:
            raise RuntimeError('You need to actually pass in a tag name.')

        if len(lookup) > 100:
            raise RuntimeError('Tag name is a maximum of 100 characters.')

    @tag.command(pass_context=True, aliases=['add', 'make'])
    async def create(self, ctx: commands.Context, name: str, *, content: str):
        """Creates a new tag owned by you."""
        content = self.clean_tag_content(content)
        lookup = name.lower().strip()
        try:
            self.verify_lookup(lookup)
        except RuntimeError as e:
            return await self.bot.say(e, delete_after=10)

        if lookup in self.db:
            return await self.bot.say(f'A tag with the name of "{lookup}" already exists.', delete_after=10)

        await self.db.put(lookup, TagInfo(name, content, ctx.message.author.id,
                                          created_at=datetime.datetime.utcnow().timestamp()))
        await self.bot.say(f'Tag "{lookup}" successfully created.', delete_after=10)

    @create.error
    async def create_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Tag ' + str(error), delete_after=10)

    def top_three_tags(self):
        emoji = 129351
        ranked = sorted(self.db.all().values(), key=lambda t: t.uses, reverse=True)
        for tag in ranked[:3]:
            yield (chr(emoji), tag)
            emoji += 1

    @tag.command(aliases=['overview'])
    async def stats(self):
        """Gives information about the tags in the database."""
        embed = discord.Embed()

        all_tag_infos = self.db.all().values()
        total_tags = len(all_tag_infos)
        embed.add_field(name='Number of Tags', value=total_tags)
        total_uses = sum(t.uses for t in all_tag_infos)
        embed.add_field(name='Total Tag Uses', value=total_uses)
        embed.add_field(name='Featured Tag', value='PLACEHOLDER')

        for emoji, tag in self.top_three_tags():
            embed.add_field(name=f'{emoji} Tag', value=f'{tag.name} ({tag.uses} uses)')

        await self.bot.say(embed=embed)

    def can_modify(self, ctx, tag):
        return ctx.message.author.id in [tag.owner, config.owner_id]

    @tag.command(pass_context=True, aliases=['change'])
    async def edit(self, ctx, name: str, *, content: str):
        """Modifies an existing tag that you own.

        This completely replaces the existing text."""

        content = self.clean_tag_content(content)
        lookup = name.lower()
        try:
            tag = self.get_tag(lookup)
        except RuntimeError as e:
            return await self.bot.say(e)

        if not self.can_modify(ctx, tag):
            return await self.bot.say('Only the tag owner can edit this tag.')

        tag.content = content
        await self.db.put(tag.name, tag)
        await self.bot.say('Tag successfully edited.')

    @tag.command(pass_context=True, aliases=['delete'])
    async def remove(self, ctx, *, name: str):
        """Removes a tag that you own.

        This is un-undoable, so don't be dumb."""

        lookup = name.lower()
        try:
            tag = self.get_tag(lookup)
        except RuntimeError as e:
            return await self.bot.say(e)

        if not self.can_modify(ctx, tag):
            return await self.bot.say('Only the tag owner can delete this tag.')

        await self.db.remove(lookup)

    @tag.command(pass_context=True, aliases=['owner'])
    async def info(self, ctx, *, name: str):
        """Retrieves information about a tag."""

        lookup = name.lower()
        try:
            tag = self.get_tag(lookup)
        except RuntimeError as e:
            return await self.bot.say(e)

        embed = await tag.embed(ctx, self.db)
        await self.bot.say(embed=embed)

    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say('Missing tag name to get info for.')

    async def show_tags_list(self, tags, ctx):
        try:
            p = paginator.Pages(self.bot, message=ctx.message, entries=tags, per_page=15)
            p.embed.colour = 0x738bd7
            await p.paginate()
        except Exception as e:
            await self.bot.say(e)

    @tag.command(name='list', pass_context=True)
    async def _list(self, ctx, *, member: discord.Member = None):
        """Lists all tags that belong to you or someone else."""

        owner = ctx.message.author if member is None else member
        tags = [tag.name for tag in self.db.all().values() if tag.owner == owner.id]
        tags.sort()

        await self.show_tags_list(tags, ctx)

    @tag.command(name='all', pass_context=True)
    async def _all(self, ctx):
        """Lists ALL THE TAGS ranked by usage."""

        tags = [tag.name for tag in sorted(self.db.all().values(), key=lambda t: t.uses, reverse=True)]

        await self.show_tags_list(tags, ctx)

    @tag.command(pass_context=True)
    async def search(self, ctx, *, query: str):
        """Searches for a tag by substring or close match.
        The query must be at least 2 characters."""
        pass


def setup(bot):
    bot.add_cog(Tags(bot))
