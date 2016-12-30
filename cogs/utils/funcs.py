import aiohttp
import io
import asyncio


class Funcs:
    def __init__(self, bot):
        self.bot = bot

    async def bytes_download(self, url: str):
        session = aiohttp.ClientSession(loop=self.bot.loop)
        try:
            with aiohttp.Timeout(5):
                async with session.get(url) as resp:
                    data = await resp.read()
                    b = io.BytesIO(data)
                    b.seek(0)
                    return b
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            print(e)
            return False
