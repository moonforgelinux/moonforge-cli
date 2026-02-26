# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Machine, MachineFragment, MachineInclude


RPI5_CONF = ['WKS_FILE = "moonforge-image-base-raspberrypi.wks.in"']

RPI5_DISTRO_CONF = [
    'OVERLAYFS_ETC_DEVICE = "/dev/mmcblk0p3"',
    'IMAGE_DATA_MIN_SIZE = "4096M"',
]

RPI5_MACHINE = Machine(name="raspberrypi5",
                       description="RaspberryPi 5 builds",
                       includes=[
                         MachineInclude("meta-moonforge", "kas/include/layer/meta-moonforge-raspberrypi.yml"),
                       ],
                       local_conf=[
                         MachineFragment(section='meta-moonforge-raspberrypi', text=RPI5_CONF, weight=30),
                         MachineFragment(section='meta-moonforge-distro', text=RPI5_DISTRO_CONF, weight=20),
                       ])
