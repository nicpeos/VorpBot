from __future__ import annotations

import json

from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import MEDIUMTEXT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Area(Base):
    __tablename__ = "area"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(MEDIUMTEXT)
    abbreviation = Column(VARCHAR(5))
    _poracle_names = Column("poracle_names", MEDIUMTEXT)

    @classmethod
    def create(cls, name: str, poracle_names: list[str]) -> Area:
        return cls(name=name, _poracle_names=json.dumps(poracle_names))

    @property
    def poracle_names(self) -> list[str]:
        return json.loads(self._poracle_names)

    @poracle_names.setter
    def poracle_names(self, value: list[str]) -> None:
        self._poracle_names = json.dumps(value)

    def add_poracle_name(self, name: str) -> None:
        new_names = self.poracle_names
        new_names.append(name)
        self.poracle_names = new_names

    def remove_poracle_name(self, name: str) -> None:
        new_names = self.poracle_names
        new_names.remove(name)
        self.poracle_names = new_names


class Template(Base):
    __tablename__ = "template"

    name = Column(VARCHAR(128), primary_key=True)
    command = Column(MEDIUMTEXT)
