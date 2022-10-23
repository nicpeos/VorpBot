from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import discord

from vorpbot.db.repository import add_area as write_db, get_templates
from .areatemplate import AreaTemplate, set_up_area_trackings
from .steps import StepEmbed, StepMessageProxy

if TYPE_CHECKING:
    from vorpbot.discord.client import VorpBotClient
    from vorpbot.db.model import Area


class ArbitraryRole(discord.Role):
    """Workaround for a weird quirk in discord.py"""

    def __init__(self, id_: int):
        self.id = id_


class AreaAddSteps(Enum):
    DB = "Add to database"
    ROLE = "Create role"
    CATEGORY = "Create category"
    CHANNELS = "Create channels"
    REGISTER = "Register webhooks"
    AREAS = "Add areas"
    TRACKINGS = "Add trackings"


async def add_area(client: VorpBotClient, message: discord.Message, area: Area):
    guild = message.guild

    embed = StepEmbed(title=f"Adding Area `{area.name}`", steps=AreaAddSteps)
    steps = StepMessageProxy(message, embed)
    await steps.initial_edit()

    await write_db(area)
    await steps.done(AreaAddSteps.DB)

    role = await guild.create_role(name=area.name)
    await steps.done(AreaAddSteps.ROLE)

    overwrites = {
        ArbitraryRole(guild.id): discord.PermissionOverwrite(read_messages=False, send_messages=False),
        role: discord.PermissionOverwrite(read_messages=True),
    }
    category = await guild.create_category(name=area.name, overwrites=overwrites)
    await steps.done(AreaAddSteps.CATEGORY)

    templates = await get_templates()
    area_templates: list[AreaTemplate] = []
    for template in templates:
        area_template = AreaTemplate(client=client, area=area, template=template)
        await area_template.create_channel(category)
        area_templates.append(area_template)
    await steps.done(AreaAddSteps.CHANNELS)

    await set_up_area_trackings(
        area_templates, client, steps, AreaAddSteps.REGISTER, AreaAddSteps.AREAS, AreaAddSteps.TRACKINGS
    )
