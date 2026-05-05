# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field


@dataclass
class MachineFragment:
    """Class for weighted template fragments."""
    section: str
    key: str
    value: str
    weight: int = 0


@dataclass
class MachineInclude:
    repo: str
    file: str


@dataclass
class MachineRepo:
    name: str
    url: str | None = None
    commit: str | None = None
    branch: str | None = None
    layers: list[str] = field(default_factory=list)


@dataclass
class Machine:
    """Class for machine templates."""
    name: str
    description: str
    includes: list[MachineInclude] = field(default_factory=list)
    local_conf: list[MachineFragment] = field(default_factory=list)
    repos: list[MachineRepo] = field(default_factory=list)
    default: bool = False


def available_machines() -> list[Machine]:
    from .qemu import QEMU_MACHINE
    from .raspberrypi5 import RPI5_MACHINE

    return [
        QEMU_MACHINE,
        RPI5_MACHINE,
    ]


def get_machine(name: str) -> Machine:
    for machine in available_machines():
        if name == "default" and machine.default:
            return machine
        if machine.name == name:
            return machine
    raise IndexError(f"Machine {name} not found")
