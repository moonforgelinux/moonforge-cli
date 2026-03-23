# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os

from .log import AnsiEscape
from .machines import available_machines


HELP_MSG = "List the available machines"


def add_args(parser) -> None:
    pass


def run(options) -> 0:
    res = [str(AnsiEscape(text="Available machines:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD))]

    max_name_len = 0
    for m in available_machines():
        max_name_len = len(m.name) if len(m.name) > max_name_len else max_name_len
    for m in available_machines():
        name = str(AnsiEscape(text=m.name, fg_color=AnsiEscape.GREEN_FG))
        if m.default:
            default = " (default: ✅)"
        else:
            default = ""
        pad = " ".ljust(max_name_len - len(m.name) + 1)
        res.append(f"- {name}:{pad}{m.description}{default}")
    print("\n".join(res))
    return 0
