# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from pathlib import Path

from . import log, kas, utils

from .features import Feature
from .machines import Machine


class Project:
    """The metadata for a Moonforge project."""
    def __init__(self, name: str, path: Path, machine: Machine, features: list[Feature], variables: dict[str], vcs: str):
        self._name = name
        self._path = path
        self._machine = machine
        self._features = features
        self._variables = variables
        self._vcs = vcs

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def machine(self) -> Machine:
        return self._machine

    @property
    def features(self) -> list[Feature]:
        return self._features

    @property
    def local_repo_name(self) -> str:
        return utils.sanitize_layer_name(self._name)

    @property
    def vcs(self) -> str:
        return self._vcs

    def to_kas(self) -> str:
        kf = kas.KasFile()
        kf.add_include(repo=None, file="kas/include/repo/meta-moonforge.yml")
        kf.add_include(repo="meta-moonforge", file="kas/include/layer/meta-moonforge-distro.yml")
        kf.add_local_repo(name=f"{self.local_repo_name}", layers=[f"{self.local_repo_name}-distro"])
        kf.set_distro(self._name)
        kf.set_machine(self._machine)
        for feat in self._features:
            kf.add_feature(feat)
        for key in self._variables:
            kf.add_variable(key, self._variables[key])
        return str(kf)

    def to_toml(self) -> str:
        res = [
            "[project]",
            f'name = "{self._name}"',
        ]
        if self._machine is not None:
            res.append(f'machine = "{self._machine.name}"')
        features = []
        for feat in self._features:
            features.append(f'"{feat.name}"')
        if len(features) > 0:
            res.append(f"features = [ {', '.join(features)} ]")
        variables = []
        for key in self._variables:
            variables.append(f'"{key}={self._variables[key]}"')
        if len(variables) > 0:
            res.append(f"variables = [ {', '.join(variables)} ]")
        return "\n".join(res)
