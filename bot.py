from discord.ext import commands
from cogs.utils import config, checks
import datetime
import json

initial_extensions = [
    'cogs.admin',
    'cogs.info'
]

bot = commands.Bot(**config.bot_kwargs)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - ID: {bot.user.id}')
    bot.uptime = datetime.datetime.utcnow()


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


if __name__ == '__main__':
    with open('credentials.json') as f:
        credentials = json.load(f)

    token = credentials['token']

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'FAIL LOADING {extension}\n{type(e).__name__}: {e}')

    bot.run(token)
