# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field


@dataclass
class FeatureFragment:
    """Class for weighted template fragments."""
    section: str
    text: list[str]
    weight: int = 0


@dataclass
class FeatureInclude:
    repo: str
    file: str


@dataclass
class Feature:
    """Class for feature templates."""
    name: str
    description: str
    includes: list[FeatureInclude] = field(default_factory=list)
    local_conf: list[FeatureFragment] = field(default_factory=list)


def available_features() -> list[Features]:
    from .docker import DOCKER_FEATURE
    return [
        DOCKER_FEATURE,
    ]


def get_feature(name: str) -> Feature | None:
    for feature in available_features():
        if feature.name == name:
            return feature
    return None
