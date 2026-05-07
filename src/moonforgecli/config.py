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

    def get_path(self) -> Path:
        match self:
            case ConfigSourceType.USER:
                return xdg_config_home() / "moonforge" / "config.toml"
            case ConfigSourceType.PROJECT:
                return Path(".moonforge/config.toml")


# Default values for the "container" section
CONTAINER_DEFAULTS: dict[str, str] = {
    "engine": "docker",
    "image_path": "ghcr.io/siemens/kas",
    "image_name": "kas",
    "image_version": "4.6",
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
            f'engine = "{self._container.engine}"',
            f'image_path = "{self._container.image_path}"',
            f'image_name = "{self._container.image_name}"',
            f'image_version = "{self._container.image_version}"',
        ]


class ConfigSource:
    def __init__(self, source_type: ConfigSourceType):
        self._source_type = source_type
        self._container = ConfigContainerSection()

    @property
    def source_type(self) -> ConfigSourceType:
        return self._source_type

    @staticmethod
    def load_all() -> ConfigSource:
        res = None
        for source_type in ConfigSourceType:
            path = source_type.get_path().absolute()
            if not path.exists():
                continue
            with path.open(mode="rb") as f:
                try:
                    data = tomllib.load(f)
                except Exception as err:
                    log.warning(f"Invalid configuration at {path}: {err}")
                    continue
                if res is None:
                    res = ConfigSource(ConfigSourceType.PROJECT)
                for key in data.get("container", {}):
                    setattr(res._container, key, data["container"][key])
        if res is None:
            res = ConfigSource(ConfigSourceType.PROJECT)
        return res

    @staticmethod
    def from_toml(source_type: ConfigSourceType) -> ConfigSource:
        res = ConfigSource(source_type)
        path = source_type.get_path().absolute()
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
        return res

    def to_toml(self):
        file_path = self._source_type.get_path().absolute()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(mode="w", encoding="utf-8") as f:
            res = []
            res.extend(self._container.to_toml())
            f.write("\n".join(res))

    def __iter__(self):
        keys = []
        for k in self._container.__dict__.keys():
            keys.append(f"container.{k}")
        return iter(keys)

    def __contains__(self, key):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            return False
        if section == "container":
            return subkey in CONTAINER_DEFAULTS
        return False

    def __getitem__(self, key):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            raise KeyError(f"Invalid configuration key {key!r}; use 'section.key'")
        if section == "container":
            if subkey not in CONTAINER_DEFAULTS:
                raise KeyError(f"Unknown key {subkey} inside 'container'")
            return getattr(self._container, subkey)
        else:
            raise KeyError(f"Unknown section {section}")

    def __setitem__(self, key, value):
        try:
            (section, subkey) = key.split(".", 1)
        except Exception:
            raise KeyError(f"Invalid configuration key {key!r}; use 'section.key'")
        if section == "container":
            if subkey not in CONTAINER_DEFAULTS:
                raise KeyError(f"Unknown key {subkey} inside 'container'")
            setattr(self._container, subkey, value)
        else:
            raise KeyError(f"Unknwon section {section}")


HELP_MSG = "Configure the Moonforge CLI tool"


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
