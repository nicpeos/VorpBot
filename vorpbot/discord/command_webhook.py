from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from .client import VorpBotClient


@app_commands.guild_only()
class WebhookCommandGroup(app_commands.Group):
    def __init__(self, client: VorpBotClient):
        super().__init__(name="webhook", description="Manage webhooks")
        self._client: VorpBotClient = client

    @app_commands.command(name="add", description="Add a webhook")
    @discord.app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def add_selector(self, interaction: discord.Interaction, channel_id: str) -> None:
        channel = await interaction.guild.fetch_channel(int(channel_id))
        wh = await channel.create_webhook(name="Poracle managed by VorpBot")
        await interaction.response.send_message("`" + wh.url + "`")
