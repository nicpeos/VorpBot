from __future__ import annotations

from typing import Iterable

import discord
from discord import ui


class OverflowView(ui.View):
    def __init__(self, options: list[discord.SelectOption], max_options: int = 5, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        options = sorted(options, key=lambda o: o.label)

        current_select: ui.Select
        for i, option in enumerate(options):
            if i % 25 == 0:
                if len(self.children) == max_options + 1:
                    break

                current_select = ui.Select(min_values=0)
                current_select.callback = self.select_callback
                self.add_item(current_select)
            current_select.append_option(option)

        for item in self.selects:
            first, last = item.options[0], item.options[-1]
            item.placeholder = f"{first.label[0]} – {last.label[0]}".upper()
            item.max_values = len(item.options)

    @property
    def selects(self) -> Iterable[ui.Select]:
        for item in self.children:
            if isinstance(item, ui.Select):
                yield item

    @property
    def selected_values(self) -> Iterable[str]:
        for item in self.selects:
            yield from item.values

    async def select_callback(self, interaction: discord.Interaction) -> None:
        pass
