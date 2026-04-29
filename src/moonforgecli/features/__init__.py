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
    conflicts: list[str] | None = field(default_factory=list)


def available_features() -> list[Features]:
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


def get_feature(name: str) -> Feature | None:
    for feature in available_features():
        if feature.name == name:
            return feature
    return None


def check_conflicts(name: str, features: list[str]) -> list[str] | None:
    feature = get_feature(name)
    feature_conflicts = getattr(feature, "conflicts", [])
    if len(feature_conflicts) == 0:
        return None

    res = []
    for feat in features:
        check = get_feature(feat)
        if check.name in feature_conflicts:
            res.append(check.name)
        else:
            check_conflicts = getattr(check, "conflicts", [])
            if feature.name in check_conflicts:
                res.append(check.name)

    if len(res) == 0:
        return None

    return res
