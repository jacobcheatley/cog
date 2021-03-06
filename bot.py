import datetime
import json

import discord
from discord.ext import commands

from cogs.utils import config, checks, funcs

bot = commands.Bot(**config.bot_kwargs)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - ID: {bot.user.id}')
    bot.uptime = datetime.datetime.utcnow()
    bot.funcs = funcs.Funcs(bot)


@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bots

    await bot.process_commands(message)


@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """Loads a module."""
    try:
        bot.load_extension(module)
    except Exception as e:
        await bot.say(f'Failed. {type(e).__name__} - {e}', delete_after=10)
    else:
        await bot.say('\N{OK HAND SIGN}')


@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """Unload a module."""
    try:
        bot.unload_extension(module)
    except Exception as e:
        await bot.say(f'Failed. {type(e).__name__} - {e}', delete_after=10)
    else:
        await bot.say('\N{OK HAND SIGN}')


@bot.command(name='reload', hidden=True)
@checks.is_owner()
async def _reload(*, module: str):
    """Reloads a module."""
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except Exception as e:
        await bot.say(f'Failed. {type(e).__name__} - {e}', delete_after=10)
    else:
        await bot.say('\N{OK HAND SIGN}')


@bot.command(hidden=True)
@checks.is_owner()
async def setcogname(name: str):
    """Changes Cog's username."""
    try:
        await bot.edit_profile(username=name)
    except:
        await bot.say('Failed to update username.')


@bot.command(hidden=True)
@checks.is_owner()
async def setcogavatar(url: str):
    """Changes Cog's avatar."""
    b = await bot.funcs.bytes_download(url)
    if b:
        byte = b.getvalue()
        try:
            await bot.edit_profile(avatar=byte)
        except:
            await bot.say('Failed to update avatar.', delete_after=10)
    else:
        await bot.say('Failed to update avatar.', delete_after=10)


@bot.command(hidden=True)
@checks.is_owner()
async def join():
    """Gets an invite link to join another server."""
    perms = discord.Permissions.none()
    perms.read_messages = True
    perms.send_messages = True
    perms.manage_roles = True
    perms.ban_members = True
    perms.kick_members = True
    perms.manage_messages = True
    perms.embed_links = True
    perms.read_message_history = True
    perms.attach_files = True
    perms.add_reactions = True
    perms.external_emojis = True
    perms.mention_everyone = True
    await bot.say(discord.utils.oauth_url(bot.client_id, perms))


if __name__ == '__main__':
    with open('credentials.json') as f:
        credentials = json.load(f)

    token = credentials['token']
    bot.client_id = credentials['client_id']

    for extension in config.initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'FAIL LOADING {extension}\n{type(e).__name__}: {e}')

    bot.run(token)
