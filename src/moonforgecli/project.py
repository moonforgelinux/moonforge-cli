# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

try:
    import tomllib              # type: ignore
except ImportError:
    import tomli as tomllib     # type: ignore

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

MACHINE_META: dict[str, str] = {
    "MACHINE_NAME": "name",
}

EDITIONS: dict[str, list[str]] = {
    "2026.1": [
        "edition",
        "features",
        "machine",
        "name",
        "repos",
        "variables",
        "vcs",
    ],
}

EDITION_DEFAULT = "2026.1"


class Project:
    """The metadata for a Moonforge project."""
    def __init__(self, **kwargs):
        self._edition = kwargs.get("edition", EDITION_DEFAULT)
        self._name = kwargs.get("name")
        self._path = kwargs.get("path")
        self._machine = kwargs.get("machine")
        self._features = kwargs.get("features", [])
        self._variables = kwargs.get("variables", {})
        self._vcs = kwargs.get("vcs", "none")
        self._repos = kwargs.get("repos", {})

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

    @property
    def edition(self) -> str:
        return self._edition

    @property
    def repos(self) -> dict[str, dict[str, str]]:
        return self._repos

    def add_repo(self, name: str, url: str, commit: str, branch: str, required: bool = False) -> None:
        self._repos[name] = {
            "url": url,
            "commit": commit,
            "branch": branch,
            "required": required,
        }

    def remove_repo(self, name: str) -> None:
        try:
            repo = self._repos[name]
            if repo["required"]:
                log.error(f"Repository {name} is required and cannot be removed")
            del self._repos[name]
        except KeyError:
            log.error(f"Could not remove repository {name}")

    def to_kas(self) -> str:
        kf = kas.KasFile()
        for name in self._repos:
            kf.add_include(repo=None, file=f"kas/include/repo/{name}.yml")
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
            log.error(f"No project found at {path}; use 'moonforge init' to initialize a project.")
        with open(project_toml_path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception as err:
                log.error(f"Invalid project at {path}: {err}")
            edition = data["project"].get("edition", EDITION_DEFAULT)
            if edition not in EDITIONS:
                log.error(f"Invalid edition '{edition}' for the project file.")

            def validate_fields(check, edition_id, valid_fields):
                for field in check:
                    if field not in valid_fields:
                        log.error(f"Invalid field {field} for the given project edition {edition_id}")

            validate_fields(data["project"], edition, EDITIONS[edition])

            def get_2026_1_fields(source):
                args = {}
                for field in EDITIONS["2026.1"]:
                    match field:
                        case "machine":
                            args["machine"] = get_machine(source["machine"])
                        case "features":
                            args["features"] = [get_feature(x) for x in source.get("features", [])]
                        case "variables":
                            variables = {}
                            for var in source.get("variables", []):
                                try:
                                    key, value = var.split("=", 1)
                                    variables[key] = value
                                except ValueError:
                                    log.warning(f"Invalid variable {var} in project.toml")
                            args["variables"] = variables
                        case "repos":
                            source_repos = source.get("repos", {})
                            repos = {}
                            for name in source_repos:
                                if not all(k in source_repos[name] for k in ("url", "commit", "branch")):
                                    log.warning(f"Invalid repository {name} in project.toml")
                                    continue
                                repo = source_repos[name]
                                repos[name] = {
                                    "url": repo["url"],
                                    "commit": repo["commit"],
                                    "branch": repo["branch"],
                                    "required": repo.get("required", False),
                                }
                            args["repos"] = repos
                        case _:
                            args[field] = source.get(field)
                return args

            match edition:
                case "2026.1":
                    kwargs = get_2026_1_fields(data["project"])
                case _:
                    log.error(f"Unknown edition {edition}")

            return cls(path=path, **kwargs)

    def to_toml(self) -> str:
        res = [
            "[project]",
            f'edition = "{self.edition}"',
            f'name = "{self.name}"',
        ]
        if self._machine is not None:
            res.append(f'machine = "{self.machine.name}"')
        features = []
        for feat in self.features:
            features.append(f'"{feat.name}"')
        if len(features) > 0:
            res.append(f"features = [ {', '.join(features)} ]")
        variables = []
        for key in self.variables:
            variables.append(f'"{key}={self._variables[key]}"')
        if len(variables) > 0:
            res.append(f"variables = [ {', '.join(variables)} ]")
        if len(self.repos) > 0:
            for name in self.repos:
                repo = self.repos[name]
                if repo["required"]:
                    res.append(f'repos."{name}" = {{ required = true, url = "{repo['url']}", commit = "{repo['commit']}", branch = "{repo['branch']}" }}')  # noqa: E501
                else:
                    res.append(f'repos."{name}" = {{ url = "{repo['url']}", commit = "{repo['commit']}", branch = "{repo['branch']}" }}')  # noqa: E501
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
        if self.machine is not None:
            for env in MACHINE_META:
                data = getattr(self.machine, MACHINE_META[env], "")
                res = res.replace(f"@{env}@", data)
        return Path(res)
