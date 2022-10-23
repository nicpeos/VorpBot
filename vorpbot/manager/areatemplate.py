from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from vorpbot.db.model import Area, Template
    from discord import TextChannel
    from vorpbot.discord.client import VorpBotClient
    from .steps import StepMessageProxy


class AreaTemplate:
    channel: TextChannel
    webhook_url: str

    def __init__(self, client: VorpBotClient, area: Area, template: Template):
        self._client: VorpBotClient = client
        self.area: Area = area
        self.template: Template = template

    @property
    def channel_name(self) -> str:
        return f"{self.area.abbreviation}-{self.template.name}"

    @property
    def poracle_name(self) -> str:
        return f"vorpbot-{self.area.abbreviation}-{self.template.name}"

    async def create_channel(self, category: discord.CategoryChannel) -> None:
        self.channel = await category.create_text_channel(name=self.channel_name)

    async def register_webhook(self) -> None:
        webhook = await self.channel.create_webhook(name="Poracle managed by VorpBot")
        self.webhook_url = webhook.url
        await self._client.poracle.send_command(
            client=self._client, name=self.poracle_name, command=f"channel add {webhook.url}"
        )

    async def set_areas(self) -> None:
        await self._client.poracle.set_areas(human_id=self.webhook_url, names=self.area.poracle_names)

    async def set_trackings(self) -> None:
        await self._client.poracle.send_command(
            client=self._client, name=self.poracle_name, command=self.template.command
        )


async def set_up_area_trackings(
    area_templates: list[AreaTemplate],
    client: VorpBotClient,
    steps: StepMessageProxy,
    register: Enum,
    areas: Enum,
    trackings: Enum,
) -> None:
    for area_template in area_templates:
        await area_template.register_webhook()
    await steps.done(register)

    for area_template in area_templates:
        await area_template.set_areas()
    await steps.done(areas)

    for area_template in area_templates:
        await area_template.set_trackings()
    await steps.done(trackings)
