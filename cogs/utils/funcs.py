import aiohttp
import io
import asyncio

session = aiohttp.ClientSession()

async def bytes_download(url: str):
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
