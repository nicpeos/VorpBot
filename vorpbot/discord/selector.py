from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from vorpbot.config import config
from vorpbot.db.model import Area
from vorpbot.db.repository import get_areas
from .overflow_select import OverflowView

if TYPE_CHECKING:
    from .client import VorpBotClient


class SelectorView(OverflowView):
    def __init__(self, areas: list[Area], roles: list[discord.Role], member: discord.Member):
        self.embed = discord.Embed(title=config.selector.personal.title)
        self._member: discord.Member = member
        self._areas: list[Area] = areas

        self._area_to_role: dict[str, discord.Role] = {}
        for area in areas:
            role = next((r for r in roles if r.name.casefold() == area.name.casefold()), None)
            if role is None:
                print(f"Unknown role for area {area.name}. That's bad!")
                continue
            self._area_to_role[str(area.id)] = role

        role_names = [r.name.casefold() for r in member.roles]

        options = []
        for area in sorted(areas, key=lambda a: a.name):
            if str(area.id) not in self._area_to_role:
                continue
            options.append(
                discord.SelectOption(label=area.name, value=str(area.id), default=area.name.casefold() in role_names)
            )

        super().__init__(options)
        self.generate_description(role_names)

    def generate_description(self, role_names: list[str] | None = None) -> None:
        if role_names is None:
            role_names = []

        self.embed.description = f"{config.selector.personal.description}\n\n"
        for area in self._areas:
            if str(area.id) in self.selected_values or area.name.casefold() in role_names:
                self.embed.description += f"▶ {area.name}\n"

    async def select_callback(self, interaction: discord.Interaction) -> None:
        roles = self._member.roles

        for area in self._areas:
            for role in roles:
                if area.name == role.name:
                    roles.remove(role)

        for value in self.selected_values:
            role = self._area_to_role.get(value)
            if role is None:
                print(f"area id {value} was selected but not found. That's bad!")
                continue

            self._member.roles.append(role)
            roles.append(role)

        for select in self.selects:
            for option in select.options:
                option.default = option.value in self.selected_values

        print(roles)
        await self._member.edit(roles=roles)
        self.generate_description()
        await interaction.response.edit_message(embed=self.embed, view=self)


class Selector:
    def __init__(self, client: VorpBotClient):
        self._client: VorpBotClient = client

    async def send_message(self, interaction: discord.Interaction) -> None:
        guild = await self._client.fetch_guild(interaction.guild_id)
        member = await guild.fetch_member(interaction.user.id)
        roles = await guild.fetch_roles()

        areas = await get_areas()
        view = SelectorView(areas, roles, member)

        await interaction.response.send_message(embed=view.embed, view=view, ephemeral=True)
