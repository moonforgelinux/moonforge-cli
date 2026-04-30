# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field


@dataclass
class FeatureFragment:
    """Class for weighted template fragments."""
    section: str
    key: str
    value: str
    weight: int = 0


@dataclass
class FeatureInclude:
    repo: str
    file: str


@dataclass
class FeatureRepo:
    name: str
    url: str | None = None
    commit: str | None = None
    branch: str | None = None
    layers: list[str] = field(default_factory=list)


type FeatureIncludeOverride = dict[str, list[FeatureInclude]]
type FeatureFragmentOverride = dict[str, list[FeatureFragment]]
type FeatureRepoOverride = dict[str, list[FeatureRepo]]
type FeatureOverride = FeatureIncludeOverride | FeatureFragmentOverride | FeatureRepoOverride


@dataclass
class Feature:
    """Class for feature templates."""
    name: str
    description: str
    includes: list[FeatureInclude] = field(default_factory=list)
    local_conf: list[FeatureFragment] = field(default_factory=list)
    machine_overrides: dict[str, FeatureOverride] | None = field(default_factory=dict)


def available_features() -> list[Features]:
    from .docker import DOCKER_FEATURE
    from .rauc_simple import RAUC_FEATURE
    return [
        DOCKER_FEATURE,
        RAUC_FEATURE,
    ]


def get_feature(name: str) -> Feature | None:
    for feature in available_features():
        if feature.name == name:
            return feature
    return None
