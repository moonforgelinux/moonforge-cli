# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import sys
import tomllib

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .utils import xdg_config_home


class ConfigSourceType(Enum):
    SYSTEM = 0
    SITE = 1
    USER = 2
    PROJECT = 3

    @staticmethod
    def get_path(source: ConfigSourceType) -> Path:
        match source:
            case ConfigSourceType.SYSTEM:
                return Path(os.path.join(sys.prefix, "share/moonforge/config.toml"))
            case ConfigSourceType.SITE:
                return Path("/etc/moonforge/config.toml")
            case ConfigSourceType.USER:
                return xdg_config_home() / "moonforge" / "config.toml"
            case ConfigSourceType.PROJECT:
                return Path(".moonforge/config.toml")


@dataclass
class ConfigSource:
    source_type: ConfigSourceType
    
