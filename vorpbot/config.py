from __future__ import annotations

import sys

import rtoml
from pydantic import BaseModel, ValidationError


class Discord(BaseModel):
    token: str
    guilds: list[int]
    poracle_id: int
    trash_channel_id: int


class Poracle(BaseModel):
    blacklisted_prefixes: list[str] = []
    secret: str
    url: str


class Db(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str


class StaticEmbed(BaseModel):
    description: str
    footer: str
    button: str


class Personal(BaseModel):
    title: str
    description: str


class Selector(BaseModel):
    static_embed: StaticEmbed
    personal: Personal


class Config(BaseModel):
    discord: Discord
    poracle: Poracle
    db: Db
    selector: Selector


with open("config.toml", mode="r") as _config_file:
    _raw_config = rtoml.load(_config_file)

try:
    _config = Config(**_raw_config)
except ValidationError as e:
    print(f"Config validation error!\n{e}")
    sys.exit(1)

config = _config
