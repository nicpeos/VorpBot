from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands, ui

from vorpbot.db.model import Template
from vorpbot.manager.template_manager import add_template

if TYPE_CHECKING:
    from .client import VorpBotClient


class TemplateAddModal(ui.Modal, title="Add a template"):
    name = ui.TextInput(label="The name of the template", placeholder="100", required=True)
    command = ui.TextInput(
        label="The Poracle command. Without prefix", placeholder="track everything iv100", required=True
    )

    def __init__(self, client: VorpBotClient):
        super().__init__()
        self._client: VorpBotClient = client

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        channel = self._client.get_channel(interaction.channel_id)
        if channel is None:
            channel = await self._client.fetch_channel(interaction.channel_id)

        message = await channel.send(embed=discord.Embed(title="Adding template"))
        await add_template(
            client=self._client, message=message, template=Template(name=self.name.value, command=self.command.value)
        )


@app_commands.guild_only()
class TemplateCommandGroup(app_commands.Group):
    def __init__(self, client: VorpBotClient):
        super().__init__(name="template", description="Manage templates")
        self._client: VorpBotClient = client

    @app_commands.command(name="add", description="Add a template")
    @discord.app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def add_template(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(TemplateAddModal(self._client))
