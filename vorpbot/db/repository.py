from __future__ import annotations

from typing import TypeVar, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from vorpbot.config import config
from .model import Base, Area, Template

db_uri: str = (
    f"mysql+aiomysql://{config.db.username}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"
)


engine = create_async_engine(db_uri, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_models() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _add_any(model: Base) -> None:
    async with async_session() as session:
        session.add(model)
        await session.commit()


AnyModel = TypeVar("AnyModel", bound=Base)


async def _get_any(model: Type[AnyModel]) -> list[AnyModel]:
    async with async_session() as session:
        result = await session.execute(select(model))
        return result.scalars().all()


async def add_area(area: Area) -> None:
    async with async_session() as session:
        session.add(area)
        await session.commit()


async def get_areas() -> list[Area]:
    return await _get_any(Area)


async def add_template(template: Template) -> None:
    await _add_any(template)


async def get_templates() -> list[Template]:
    return await _get_any(Template)
