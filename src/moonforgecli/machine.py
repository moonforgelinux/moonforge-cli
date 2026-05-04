# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from . import log, term
from .machines import available_machines, get_machine


HELP_MSG = "Show feature information"


def add_args(parser) -> None:
    parser.add_argument("--list", default=False, dest="list", action="store_true",
                        help="list all available machines")
    parser.add_argument("machines", nargs="*",
                        help="optional list of machines to query")


def run(options) -> int:
    if options.list:
        res = [term.heading(text="Available machines:")]
        max_name_len = 0
        for m in available_machines():
            max_name_len = len(m.name) if len(m.name) > max_name_len else max_name_len
        for m in available_machines():
            name = term.option(m.name)
            pad = " ".ljust(max_name_len - len(m.name) + 1)
            res.append(f"- {name}:{pad}{m.description}")
        print("\n".join(res))
        return 0

    if len(options.machines) == 0:
        heading = term.heading("usage:")
        command = term.command("moonforge")
        option = term.option("machine")
        print(f"{heading} {command} {option} MACHINE...")
        return 1

    machines = []
    for machine in options.machines:
        m = get_machine(machine)
        if m is None:
            log.error(f"Invalid machine {machine}.")
        machines.append(m)
    for machine in machines:
        res = []
        res.append(f"{term.heading('Machine:')} {term.bold(machine.name)}")
        res.append("")
        res.append(f"  {machine.description}")
        res.append("")
        if len(machine.includes) > 0:
            res.append(term.heading("Includes:"))
            for include in machine.includes:
                res.append(f"  - {term.green(include.file)} from {term.green(include.repo)}")
            res.append("")
        print("\n".join(res))

    return 0
