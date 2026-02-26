# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Fragment, Machine


QEMU_LOCAL_CONF = 'WKS_FILE = "moonforge-image-base-qemux86-64.wks.in"'

QEMU_MACHINE = Machine(name="qemu",
                       description="QEMU x86_64 builds",
                       include="kas/include/layer/meta-moonforge-qemu.yml",
                       local_conf=[Fragment(text=QEMU_LOCAL_CONF, weight=20)],
                       default=True)
