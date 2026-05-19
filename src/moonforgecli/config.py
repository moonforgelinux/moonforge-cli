# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import tomllib

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import log, term

from .utils import xdg_config_home


class ConfigSourceType(Enum):
    """Type of configuration file source."""
    PROJECT = 0
    USER = 1

    def get_path(self, project_path: Path | None = None) -> Path:
        match self:
            case ConfigSourceType.USER:
                return xdg_config_home() / "moonforge" / "config.toml"
            case ConfigSourceType.PROJECT:
                if project_path is not None:
                    return project_path / ".moonforge" / "config.toml"
                else:
                    return Path(".moonforge/config.toml").absolute()


# Default keys and values for the "container" section
CONTAINER_DEFAULTS: dict[str, str] = {
    "engine": "docker",
    "image_path": "ghcr.io/siemens/kas",
    "image_name": "kas",
    "image_version": "5.0",
}

# Default keys and values for the "build" section
BUILD_DEFAULTS: dict[str, str] = {
    "sstate_dir": "@XDG_CACHE_HOME@/moonforge/@PROJECT_NAME@/sstate/",
    "download_dir": "@XDG_CACHE_HOME@/moonforge/@PROJECT_NAME@/downloads/",
}


@dataclass
class ConfigContainerSection:
    """Configuration for the 'container' section."""
    engine: str = CONTAINER_DEFAULTS["engine"]
    image_path: str = CONTAINER_DEFAULTS["image_path"]
    image_name: str = CONTAINER_DEFAULTS["image_name"]
    image_version: str = CONTAINER_DEFAULTS["image_version"]

    def to_toml(self) -> list[str]:
        return [
            "[container]",
            f'engine = "{self.engine}"',
            f'image_path = "{self.image_path}"',
            f'image_name = "{self.image_name}"',
            f'image_version = "{self.image_version}"',
        ]


@dataclass
class ConfigBuildSection:
    """Configuration for the 'build' section."""
    sstate_dir: str = BUILD_DEFAULTS["sstate_dir"]
    download_dir: str = BUILD_DEFAULTS["download_dir"]

    def to_toml(self) -> list[str]:
        return [
            "[build]"
            f'sstate_dir = "{self.sstate_dir}"',
            f'download_dir = "{self.download_dir}"',
        ]


class ConfigSource:
    def __init__(self, source_type: ConfigSourceType):
        self._source_type = source_type
        self._container = ConfigContainerSection()
        self._build = ConfigBuildSection()

    @property
    def source_type(self) -> ConfigSourceType:
        return self._source_type

    @classmethod
    def load_all(cls, project_path: Path | None = None) -> "ConfigSource":
        res = None
        for source_type in ConfigSourceType:
            path = source_type.get_path(project_path)
            if not path.exists():
                continue
            with path.open(mode="rb") as f:
                try:
                    data = tomllib.load(f)
                except Exception as err:
                    log.warning(f"Invalid configuration at {path}: {err}")
                    continue
                if res is None:
                    res = cls(ConfigSourceType.PROJECT)
                for key in data.get("container", {}):
                    setattr(res._container, key, data["container"][key])
                for key in data.get("build", {}):
                    setattr(res._build, key, data["build"][key])
        if res is None:
            res = cls(ConfigSourceType.PROJECT)
        return res

    @classmethod
    def from_toml(cls, source_type: ConfigSourceType) -> "ConfigSource":
        res = cls(source_type)
        path = source_type.get_path()
        if not path.exists():
            return res
        with open(path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception as err:
                if not path.exists():
                    log.info(f"No configuration found at {path}")
                else:
                    log.warning(f"Invalid configuration at {path}: {err}")
                return res
            container = data.get("container")
            if container is not None:
                res._container.engine = container.get("engine", CONTAINER_DEFAULTS["engine"])
                res._container.image_path = container.get("image_path", CONTAINER_DEFAULTS["image_path"])
                res._container.image_name = container.get("image_name", CONTAINER_DEFAULTS["image_name"])
                res._container.image_version = container.get("image_version", CONTAINER_DEFAULTS["image_version"])
            build = data.get("build")
            if build is not None:
                res._build.sstate_dir = build.get("sstate_dir", BUILD_DEFAULTS["sstate_dir"])
                res._build.download_dir = build.get("download_dir", BUILD_DEFAULTS["download_dir"])
        return res

    def to_toml(self):
        file_path = self._source_type.get_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(mode="w", encoding="utf-8") as f:
            res = []
            res.extend(self._container.to_toml())
            res.extend(self._build.to_toml())
            f.write("\n".join(res))

    def __iter__(self):
        keys = []
        for k in self._container.__dict__.keys():
            keys.append(f"container.{k}")
        for k in self._build.__dict__.keys():
            keys.append(f"build.{k}")
        return iter(keys)

    def __contains__(self, key):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            return False
        match section:
            case "container":
                return subkey in CONTAINER_DEFAULTS
            case "build":
                return subkey in BUILD_DEFAULTS
        return False

    def __getitem__(self, key):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            raise KeyError(f"Invalid configuration key {key!r}; use 'section.key'")
        match section:
            case "container":
                if subkey not in CONTAINER_DEFAULTS:
                    raise KeyError(f"Unknown key {subkey} inside 'container'")
                return getattr(self._container, subkey)
            case "build":
                if subkey not in BUILD_DEFAULTS:
                    raise KeyError(f"Unknown key {subkey} inside 'build'")
                return getattr(self._build, subkey)
            case _:
                raise KeyError(f"Unknown section {section}")

    def __setitem__(self, key, value):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            raise KeyError(f"Invalid configuration key {key!r}; use 'section.key'")
        match section:
            case "container":
                if subkey not in CONTAINER_DEFAULTS:
                    raise KeyError(f"Unknown key {subkey} inside 'container'")
                setattr(self._container, subkey, value)
            case "build":
                if subkey not in BUILD_DEFAULTS:
                    raise KeyError(f"Unknown key {subkey} inside 'build'")
                setattr(self._build, subkey, value)
            case _:
                raise KeyError(f"Unknwon section {section}")


HELP_MSG = "Configure the Moonforge CLI tool"

HELP_DESCRIPTION = """The config command queries, sets, and lists the configuration options for Moonforge.

Each configuration key is composed of a section and a name, separated by a dot.

The config command supports the following actions:

- list: Lists all the keys set in the configuration files, along with their value
- get: Prints the value of the given key
- set: Sets the value of the given key

Moonforge uses different configuration files; they are, in order of precendence from least important to most important:

- user configuration, stored under XDG_CONFIG_HOME/moonforge/config.toml
- project configuration, stored in .moonforge/config.toml under the project's root

Unless specified differently, the config command will query all the configuration files in the same order.

Examples:

# read from all scopes
moonforge config list

# read from project scope
moonforge config --project get container.engine

# write to the user scope
moonforge config --user set container.engine podman

# read from all scopes, write to the project scope
moonforge config set container.engine podman
"""


def add_args(parser):
    parser.add_argument("--project", dest="config", action="store_const", const="project",
                        help="Use the project's local configuration file")
    parser.add_argument("--user", dest="config", action="store_const", const="user",
                        help="Use the user's global configuration file")
    parser.add_argument("action", metavar="ACTION", choices=["get", "set", "list"],
                        help="the action to perform")
    parser.add_argument("key", metavar="KEY", nargs="?", help="the configuration key")
    parser.add_argument("value", metavar="VALUE", nargs="?", help="the key value")


def run(options):
    match options.config:
        case "project":
            source = ConfigSource.from_toml(ConfigSourceType.PROJECT)

        case "user":
            source = ConfigSource.from_toml(ConfigSourceType.USER)

        case _:
            source = ConfigSource.load_all()

    if options.action == "get":
        if options.value is not None:
            heading = term.heading("usage:")
            command = term.command("moonforge")
            option = term.option("config get")
            print(f"{heading} {command} {option} KEY")
            return 1
        try:
            print(f"{source[options.key]}")
        except Exception as err:
            log.error(f"{err}")
    elif options.action == "set":
        if options.value is None:
            heading = term.heading("usage:")
            command = term.command("moonforge")
            option = term.option("config set")
            print(f"{heading} {command} {option} KEY VALUE")
            return 1
        try:
            source[options.key] = options.value
            source.to_toml()
        except Exception as err:
            log.error(f"Unable to set key {options.key}: {err}")
    elif options.action == "list":
        if options.key is not None:
            heading = term.heading("usage:")
            command = term.command("moonforge")
            option = term.option("config list")
            print(f"{heading} {command} {option}")
            return 1
        for key in source:
            print(f"{key} = {source[key]}")

    return 0
