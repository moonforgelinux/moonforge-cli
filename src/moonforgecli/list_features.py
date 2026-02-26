# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os

from .log import AnsiEscape
from .features import available_features


HELP_MSG = "List the available features"


def add_args(parser) -> None:
    pass


def run(options) -> 0:
    res = [str(AnsiEscape(text="Available features:", mods='BOLD_DEFAULT'))]
    max_name_len = 0
    for f in available_features():
        max_name_len = len(f.name) if len(f.name) > max_name_len else max_name_len
    for f in available_features():
        name = str(AnsiEscape(text=f.name, color='GREEN'))
        pad = " ".ljust(max_name_len - len(f.name) + 1)
        res.append(f"- {name}:{pad}{f.description}")
    print("\n".join(res))
    return 0
