from __future__ import annotations
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

RGB = tuple[int, int, int]

@dataclass(slots=True)
class Definition:
    rgb_to_id: dict[RGB, int]
    id_to_rgb: dict[int, RGB]
    warnings: list[str] = field(default_factory=list)

@dataclass(slots=True)
class ControlPoint:
    map_point: tuple[float, float]
    screen_point: tuple[float, float]

@dataclass(slots=True)
class ProvinceObservation:
    province_id: int
    rgb: RGB
    lab: tuple[float, float, float]
    sample_count: int
    dispersion: float
    visible_fraction: float
    confidence: float
    source_image: str = ""
    cluster_id: str = ""
    entity_name: str = ""
    excluded: bool = False
    conflict: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
