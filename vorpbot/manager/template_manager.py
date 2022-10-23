from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import discord

from vorpbot.db.repository import add_template as write_db, get_areas
from .areatemplate import AreaTemplate, set_up_area_trackings
from .steps import StepEmbed, StepMessageProxy

if TYPE_CHECKING:
    from vorpbot.discord.client import VorpBotClient
    from vorpbot.db.model import Template


class TemplateAddSteps(Enum):
    DB = "Add to database"
    CHANNELS = "Create channels"
    REGISTER = "Register webhooks"
    AREAS = "Add areas"
    TRACKINGS = "Add trackings"


async def add_template(client: VorpBotClient, message: discord.Message, template: Template):
    guild = message.guild

    embed = StepEmbed(title=f"Adding Template `{template.name}`", steps=TemplateAddSteps)
    steps = StepMessageProxy(message, embed)
    await steps.initial_edit()

    await write_db(template)
    await steps.done(TemplateAddSteps.DB)

    areas = await get_areas()

    area_templates: list[AreaTemplate] = []
    categories = await guild.fetch_channels()
    for category in categories:
        if not isinstance(category, discord.CategoryChannel):
            continue

        area = next((a for a in areas if a.name.casefold() == category.name.casefold()), None)
        if area is None:
            continue

        area_template = AreaTemplate(client=client, area=area, template=template)
        await area_template.create_channel(category)
        area_templates.append(area_template)
    await steps.done(TemplateAddSteps.CHANNELS)

    await set_up_area_trackings(
        area_templates, client, steps, TemplateAddSteps.REGISTER, TemplateAddSteps.AREAS, TemplateAddSteps.TRACKINGS
    )
