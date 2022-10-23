from __future__ import annotations

from enum import Enum
from typing import Type

import discord

WAITING = "⏳"
DONE = "✅"


class StepEmbed(discord.Embed):
    def __init__(self, title: str, steps: Type[Enum]):
        super().__init__(title=title)
        self._steps: dict[Enum, str] = {e: WAITING for e in steps}
        self.generate_description()

    def generate_description(self) -> None:
        self.description = ""
        for step, emoji in self._steps.items():
            self.description += f"{step.value}: {emoji}\n"

    def update_step(self, step: Enum, emoji: str) -> None:
        self._steps[step] = emoji
        self.generate_description()


class StepMessageProxy:
    def __init__(self, message: discord.Message, embed: StepEmbed):
        self._message: discord.Message = message
        self._embed: StepEmbed = embed

    async def initial_edit(self) -> None:
        await self._message.edit(embed=self._embed)

    async def update(self, step: Enum, emoji: str) -> None:
        self._embed.update_step(step, emoji)
        await self._message.edit(embed=self._embed)

    async def done(self, step: Enum) -> None:
        await self.update(step, DONE)
