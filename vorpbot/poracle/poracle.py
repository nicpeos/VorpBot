from __future__ import annotations

from enum import Enum
from typing import Literal, Any, TYPE_CHECKING
from urllib.parse import urljoin, quote_plus

import discord
import httpx
from cachetools import TTLCache

from vorpbot.config import config
from .geofence import Geofence, from_geojson

if TYPE_CHECKING:
    from vorpbot.discord.client import VorpBotClient


class CacheKey(Enum):
    PREFIX = 0


class PoracleApi:
    def __init__(self):
        self._cache: TTLCache[CacheKey, Any] = TTLCache(maxsize=10, ttl=5 * 60)

    @staticmethod
    async def _request(
        body: dict | list | None = None, url_parameters: str = "", method: Literal["GET", "POST"] = "GET"
    ) -> dict[str, Any] | list[dict[str, Any]]:
        poracle_url = urljoin(config.poracle.url, "api/")
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=urljoin(poracle_url, url_parameters),
                json=body,
                headers={"X-Poracle-Secret": config.poracle.secret},
            )
        return response.json()

    async def get_geofences(self) -> list[Geofence]:
        response = await self._request(url_parameters="geofence/all/geojson")
        return from_geojson(response.get("geoJSON", {}))

    async def get_geofence_groups(self) -> set[str | None]:
        geofences = await self.get_geofences()
        return set(g.group for g in geofences)

    async def get_prefix(self) -> str | None:
        if prefix := self._cache.get(CacheKey.PREFIX):
            return prefix

        r = await self._request(url_parameters="config/poracleWeb")
        prefix = r.get("prefix")
        self._cache[CacheKey.PREFIX] = prefix
        return prefix

    async def set_areas(self, human_id: str, names: list[str]) -> None:
        quoted = quote_plus(human_id)
        await self._request(body=names, url_parameters=f"/api/humans/{quoted}/setAreas", method="POST")

    async def send_command(self, client: VorpBotClient, name: str, command: str) -> discord.PartialEmoji | None:
        prefix = await self.get_prefix()

        if prefix is None:
            return  # TODO

        channel = client.get_channel(config.discord.trash_channel_id)
        if channel is None:
            channel = await client.fetch_channel(config.discord.trash_channel_id)

        message = await channel.send(f"{prefix}{command.strip()} name:{name}")

        # TODO return the responded emoji
