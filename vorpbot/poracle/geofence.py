from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Geofence:
    name: str
    group: str | None = None


def from_geojson(geojson: dict) -> list[Geofence]:
    geofences = []
    for feature in geojson.get("features", []):
        props: dict = feature.get("properties", {})
        name = props.get("name", "?")
        group = props.get("group")
        geofences.append(Geofence(name=name, group=group))
    return geofences
