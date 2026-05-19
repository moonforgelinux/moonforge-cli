# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import tomllib

from collections.abc import Callable
from functools import partial
from pathlib import Path

from . import kas, log, utils

from .features import Feature, get_feature
from .machines import Machine, get_machine


SAFE_PATHS: dict[str, Callable] = {
    "XDG_CACHE_HOME": utils.xdg_cache_home,
    "XDG_CONFIG_HOME": utils.xdg_config_home,
    "HOME": Path.home,
}

PROJECT_META: dict[str, str] = {
    "PROJECT_NAME": "name",
}


class Project:
    """The metadata for a Moonforge project."""
    def __init__(self, name: str, path: Path, machine: Machine, features: list[Feature], variables: dict[str, str], vcs: str | None = None):
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
    def variables(self) -> dict[str, str]:
        return self._variables

    @property
    def local_repo_name(self) -> str:
        return utils.sanitize_layer_name(self._name)

    @property
    def vcs(self) -> str:
        if self._vcs is None:
            return "none"
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

    @classmethod
    def from_toml(cls, path: Path) -> "Project":
        project_toml_path = path.absolute() / ".moonforge" / "project.toml"
        if not path.exists():
            log.error(f"No project found at {path}")
        with open(project_toml_path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception as err:
                log.error(f"Invalid project at {path}: {err}")
            name = data["project"]["name"]
            machine = get_machine(data["project"]["machine"])
            features = [get_feature(x) for x in data["project"].get("features", [])]
            variables = {}
            for variable in data["project"].get("variables", []):
                try:
                    key, value = variable.split("=", 1)
                    variables[key] = value
                except ValueError:
                    log.warning(f"Invalid variable {variable} in configuration")
            return cls(name, path.absolute(), machine, features, variables, "none")

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

    def safe_path_replace(self, path: str) -> Path:
        """Replace known variables inside paths."""
        res = path
        for env in SAFE_PATHS:
            path_gen = partial(SAFE_PATHS[env])
            res = res.replace(f"@{env}@", str(path_gen()))
        for env in PROJECT_META:
            data = getattr(self, PROJECT_META[env], "")
            res = res.replace(f"@{env}@", data)
        return Path(res)
