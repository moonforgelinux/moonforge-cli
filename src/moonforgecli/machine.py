# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os
import sys

from . import log
from .log import AnsiEscape
from .machines import available_machines, get_machine


HELP_MSG = "Show feature information"


def add_args(parser) -> None:
    parser.add_argument("--list", default=False, dest="list", action="store_true",
                        help="list all available machines")
    parser.add_argument("machines", nargs="*",
                        help="optional list of machines to query")


def run(options) -> int:
    if options.list:
        res = [str(AnsiEscape(text="Available machines:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD))]
        max_name_len = 0
        for m in available_machines():
            max_name_len = len(m.name) if len(m.name) > max_name_len else max_name_len
        for m in available_machines():
            name = str(AnsiEscape(text=m.name, fg_color=AnsiEscape.GREEN_FG))
            pad = " ".ljust(max_name_len - len(m.name) + 1)
            res.append(f"- {name}:{pad}{m.description}")
        print("\n".join(res))
        return 0

    if len(options.machines) == 0:
        print(f"{AnsiEscape(text="usage:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)} moonforge machine MACHINE...")
        return 1

    machines = []
    for machine in options.machines:
        m = get_machine(machine)
        if m is None:
            log.error(f"Invalid machine {machine}.")
        machines.append(m)
    
    for machine in machines:
        res = []
        res.append(str(AnsiEscape(text="Machine: ", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)) + str(AnsiEscape(text=machine.name, mods=AnsiEscape.BOLD)))
        res.append("")
        res.append(f"  {machine.description}")
        res.append("")
        if len(machine.includes) > 0:
            res.append(str(AnsiEscape(text="Includes:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)))
            for include in machine.includes:
                res.append(f"  - {AnsiEscape(text=include.file, fg_color=AnsiEscape.GREEN_FG)} from {AnsiEscape(text=include.repo, fg_color=AnsiEscape.GREEN_FG)}")
            res.append("")
        print("\n".join(res))

    return 0
