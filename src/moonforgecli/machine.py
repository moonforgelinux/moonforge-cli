# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from . import log, term
from .machines import available_machines, get_machine


HELP_MSG = "Show feature information"

HELP_DESCRIPTION = """The machine command shows the information related to a target machine.

Each machine can be used in a Moonforge project at initialization time.
"""  # noqa: E501


def add_args(parser) -> None:
    parser.add_argument("action", choices=["info", "list"], help="action to perform")
    parser.add_argument("machines", nargs="*", help="optional machines", default=[])


def run(options) -> int:
    match options.action:
        case "list":
            if len(options.machines) != 0:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("info")
                print(f"{heading} {command} {option} MACHINE ...")
                return 1
            res = [term.heading(text="Available machines:")]
            max_name_len = 0
            for m in available_machines():
                max_name_len = len(m.name) if len(m.name) > max_name_len else max_name_len
            for m in available_machines():
                name = term.option(m.name)
                pad = " ".ljust(max_name_len - len(m.name) + 1)
                res.append(f"- {name}:{pad}{m.description}")
            print("\n".join(res))
        case "info":
            if len(options.machines) == 0:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("info")
                print(f"{heading} {command} {option} MACHINE ...")
                return 1
            machines = []
            for machine in options.machines:
                try:
                    m = get_machine(machine)
                    machines.append(m)
                except IndexError as err:
                    log.error(f"{err}")
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
