from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands, ui

from vorpbot.db.model import Area
from vorpbot.manager.area_manager import add_area
from .overflow_select import OverflowView

if TYPE_CHECKING:
    from .client import VorpBotClient


class AreaChooseView(OverflowView):
    def __init__(self, client: VorpBotClient, name: str, abbr: str, options: list[discord.SelectOption]):
        super().__init__(options, max_options=4, timeout=None)
        self.embed: discord.Embed = discord.Embed(title=f"Please choose Poracle Geofences for area `{name}` (`{abbr}`)")

        self._client: VorpBotClient = client
        self._name: str = name
        self._abbr: str = abbr

    @ui.button(label="Finish", style=discord.ButtonStyle.primary, row=4)
    async def finish(self, interaction: discord.Interaction, _) -> None:
        area = Area(name=self._name, abbreviation=self._abbr)
        area.poracle_names = list(self.selected_values)

        view = self.clear_items()
        await interaction.response.edit_message(embed=discord.Embed(title="Done!"), view=view)
        message = await interaction.original_response()

        await add_area(client=self._client, message=message, area=area)

    async def select_callback(self, interaction: discord.Interaction) -> None:
        for select in self.selects:
            for option in select.options:
                option.default = option.value in self.selected_values

        self.embed.description = "\n".join(f"- {v}" for v in self.selected_values)
        await interaction.response.edit_message(embed=self.embed, view=self)


class AreaNameModal(ui.Modal, title="Add an area"):
    name = ui.TextInput(label="The area name", required=True)
    abbreviation = ui.TextInput(label="An abbreviation to use in channel names", max_length=5, required=True)

    def __init__(self, client: VorpBotClient):
        super().__init__()
        self._client: VorpBotClient = client

    async def on_submit(self, interaction: discord.Interaction) -> None:
        areas = await self._client.poracle.get_geofences()
        options = [discord.SelectOption(label=a.name, description=a.group) for a in areas]
        view = AreaChooseView(client=self._client, name=self.name.value, abbr=self.abbreviation.value, options=options)
        await interaction.response.send_message(embed=view.embed, view=view)


@app_commands.guild_only()
class AreaCommandGroup(app_commands.Group):
    def __init__(self, client: VorpBotClient):
        super().__init__(name="area", description="Manage areas")
        self._client: VorpBotClient = client

    @app_commands.command(name="add", description="Add an area")
    @discord.app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def add_area(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(AreaNameModal(self._client))
