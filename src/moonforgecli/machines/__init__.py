# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field


@dataclass
class Fragment:
    """Class for weighted template fragments."""
    section: str
    text: list[str]
    weight: int = 0


@dataclass
class MachineInclude:
    repo: str
    file: str


@dataclass
class Machine:
    """Class for machine templates."""
    name: str
    description: str
    includes: list[MachineInclude] = field(default_factory=list)
    local_conf: list[Fragment] = field(default_factory=list)
    default: bool = False


def available_machines() -> list[Machine]:
    from .qemu import QEMU_MACHINE
    from .raspberrypi5 import RPI5_MACHINE

    return [
        QEMU_MACHINE,
        RPI5_MACHINE,
    ]


def get_machine(machine: str) -> Machine | None:
    for m in available_machines():
        if m.name == machine:
            return m
    return None
