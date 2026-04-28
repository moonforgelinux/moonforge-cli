# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Machine, MachineFragment, MachineInclude


RPI5_MACHINE = Machine(name="raspberrypi5",
                       description="RaspberryPi 5 builds",
                       includes=[
                         MachineInclude("meta-moonforge", "kas/include/layer/meta-moonforge-raspberrypi.yml"),
                       ],
                       local_conf=[
                         MachineFragment(section="meta-moonforge-raspberrypi",
                                         weight=20,
                                         key="WKS_FILE",
                                         value="moonforge-image-base-raspberrypi.wks.in"),
                         MachineFragment(section="meta-moonforge-distro",
                                         weight=20,
                                         key="OVERLAYFS_ETC_DEVICE",
                                         value="/dev/mmcblk0p3"),
                         MachineFragment(section="meta-moonforge-distro",
                                         weight=20,
                                         key="IMAGE_DATA_MIN_SIZE",
                                         value="4096M"),
                       ])
