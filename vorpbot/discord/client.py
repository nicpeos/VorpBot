from __future__ import annotations

import discord

from vorpbot.config import config
from vorpbot.poracle import PoracleApi
from .command_area import AreaCommandGroup
from .command_selector import SelectorCommandGroup, SELECTOR_BUTTON
from .command_template import TemplateCommandGroup
from .command_webhook import WebhookCommandGroup
from .selector import Selector


class VorpBotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.none())
        self.tree = discord.app_commands.CommandTree(self)
        self.poracle: PoracleApi = PoracleApi()

    async def setup_hook(self) -> None:
        e = await self.poracle.get_geofences()

        for command in (
            AreaCommandGroup(self),
            TemplateCommandGroup(self),
            SelectorCommandGroup(self),
            WebhookCommandGroup(self),
        ):
            self.tree.add_command(command)

        for guild_id in config.discord.guilds:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"commands synced with guild {guild_id}")

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        custom_id: str = interaction.data.get("custom_id", "")
        if custom_id != SELECTOR_BUTTON:
            return

        selector = Selector(self)
        await selector.send_message(interaction)


client = VorpBotClient()
