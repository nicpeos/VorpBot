from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord import ui

from vorpbot.config import config

if TYPE_CHECKING:
    from .client import VorpBotClient


SELECTOR_BUTTON = "vorpmap_selector"


@app_commands.guild_only()
class SelectorCommandGroup(app_commands.Group):
    def __init__(self, client: VorpBotClient):
        super().__init__(name="selector", description="Manage selectors")
        self._client: VorpBotClient = client

    @app_commands.command(name="add", description="Add a selector")
    @discord.app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def add_selector(self, interaction: discord.Interaction) -> None:

        channel = self._client.get_channel(interaction.channel_id)
        if channel is None:
            channel = await self._client.fetch_channel(interaction.channel_id)

        view = ui.View()
        view.add_item(
            ui.Button(
                label=config.selector.static_embed.button, custom_id=SELECTOR_BUTTON, style=discord.ButtonStyle.primary
            )
        )

        embed = discord.Embed(description=config.selector.static_embed.description)
        embed.set_footer(text=config.selector.static_embed.footer)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("Done!", ephemeral=True)
