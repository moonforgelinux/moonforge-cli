# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import TypeAlias


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
class FeatureVariable:
    name: str
    description: str
    default: str


@dataclass
class FeatureRepo:
    name: str
    url: str | None = None
    commit: str | None = None
    branch: str | None = None
    layers: list[str] = field(default_factory=list)


FeatureIncludeOverride: TypeAlias = dict[str, list[FeatureInclude]]
FeatureFragmentOverride: TypeAlias = dict[str, list[FeatureFragment]]
FeatureRepoOverride: TypeAlias = dict[str, list[FeatureRepo]]
FeatureOverride: TypeAlias = FeatureIncludeOverride | FeatureFragmentOverride | FeatureRepoOverride


@dataclass
class Feature:
    """Class for feature templates."""

    name: str
    description: str
    includes: list[FeatureInclude] = field(default_factory=list)
    local_conf: list[FeatureFragment] = field(default_factory=list)
    machine_overrides: dict[str, FeatureOverride] | None = field(default_factory=dict)
    conflicts: list[str] | None = field(default_factory=list)
    variables: list[FeatureVariable] | None = field(default_factory=list)


def available_features() -> list[Feature]:
    from .docker import DOCKER_FEATURE
    from .graphics_weston import GRAPHICS_WESTON_FEATURE
    from .graphics_wpe import GRAPHICS_WPE_FEATURE
    from .podman import PODMAN_FEATURE
    from .rauc_simple import RAUC_FEATURE

    return [
        DOCKER_FEATURE,
        GRAPHICS_WESTON_FEATURE,
        GRAPHICS_WPE_FEATURE,
        PODMAN_FEATURE,
        RAUC_FEATURE,
    ]


def get_feature(name: str) -> Feature:
    for feature in available_features():
        if feature.name == name:
            return feature
    raise IndexError(f"Feature {name} not found")


def check_conflicts(name: str, features: list[str]) -> list[str]:
    try:
        feature = get_feature(name)
    except IndexError:
        return []

    feature_conflicts = getattr(feature, "conflicts", [])
    if len(feature_conflicts) == 0:
        return []

    res = []
    for feat in features:
        try:
            check = get_feature(feat)
        except IndexError:
            continue

        if check.name in feature_conflicts:
            res.append(check.name)
        else:
            check_conflicts = getattr(check, "conflicts", [])
            if feature.name in check_conflicts:
                res.append(check.name)

    return res
