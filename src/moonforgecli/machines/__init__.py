# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


@dataclass
class Fragment:
    """Class for weighted template fragments."""
    text: str
    weight: int = 0


@dataclass
class Machine:
    """Class for machine templates."""
    name: str
    description: str
    include: str
    local_conf: list[Fragment] | None
    default: bool = False


def available_machines() -> list[Machine]:
    from .qemu import QEMU_MACHINE

    return [
        QEMU_MACHINE,
    ]


def get_machine(machine: str) -> Machine | None:
    for m in available_machines():
        if m.name == machine:
            return m
    return None
