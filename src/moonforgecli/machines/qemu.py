# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Machine, MachineFragment, MachineInclude


QEMU_MACHINE = Machine(
    name="qemux86-64",
    description="QEMU x86_64 builds",
    includes=[
        MachineInclude("meta-moonforge", "kas/include/layer/meta-moonforge-qemu.yml")
    ],
    local_conf=[
        MachineFragment(
            section="meta-moonforge-distro",
            weight=20,
            key="OVERLAYFS_ETC_DEVICE",
            value="/dev/sda4",
        ),
        MachineFragment(
            section="meta-moonforge-distro",
            weight=20,
            key="IMAGE_DATA_MIN_SIZE",
            value="4096M",
        ),
        MachineFragment(
            section="meta-moonforge-qemu",
            weight=20,
            key="WKS_FILE",
            value="moonforge-image-base-qemux86-64.wks.in",
        ),
    ],
    default=True,
)
