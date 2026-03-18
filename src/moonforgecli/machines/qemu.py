# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Machine, MachineFragment, MachineInclude


QEMU_MACHINE = Machine(name="qemux86-64",
                       description="QEMU x86_64 builds",
                       includes=[
                         MachineInclude("meta-moonforge", "kas/include/layer/meta-moonforge-qemu.yml")
                       ],
                       wks_file=[
                         MachineFragment(section="meta-moonforge-qemu",
                                         weight=20,
                                         text=['WKS_FILE = "moonforge-image-base-qemux86-64.wks.in"']),
                       ],
                       default=True)
