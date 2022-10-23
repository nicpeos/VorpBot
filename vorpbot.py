import asyncio

import discord
from vorpbot.discord.client import client

from vorpbot.config import config

discord.utils.setup_logging()


async def main():
    async with client:
        await client.start(config.discord.token)


asyncio.run(main())
