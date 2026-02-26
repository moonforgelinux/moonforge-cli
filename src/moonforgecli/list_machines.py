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
    res = [str(AnsiEscape(text="Available machines:", mods='BOLD_DEFAULT'))]
    max_name_len = 0
    for m in available_machines():
        max_name_len = len(m.name) if len(m.name) > max_name_len else max_name_len
    for m in available_machines():
        name = str(AnsiEscape(text=m.name, color='GREEN'))
        if m.default:
            default = " ✅"
        else:
            default = ""
        res.append(f"- {name.ljust(max_name_len)}: {m.description}{default}")
    print("\n".join(res))
    return 0
