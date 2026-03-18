# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureFragment, FeatureInclude


RAUC_UPDATE_CONF = [
    'RAUC_BUNDLE_URL = "http://10.0.2.2:3333/LATEST.raucb"',
    'RAUC_FORCE_REBOOT_ON_UPDATE = "1"',
]

RAUC_FEATURE = Feature(name="rauc",
                       description="RAUC support with update bundles",
                       includes=[
                         FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-update.yml"),
                       ],
                       local_conf=[
                         FeatureFragment(section="meta-moonforge-rauc-update",
                                         weight=40,
                                         text=RAUC_UPDATE_CONF),
                       ],
                       machine_overrides={
                         "wks_file": {
                           "qemu": [
                             FeatureFragment(section="meta-moonforge-rauc-qemu",
                                             weight=40,
                                             text=['WKS_FILE = "moonforge-image-rauc-qemux86-64.wks.in"']),
                           ],
                           "raspberrypi5": [
                             FeatureFragment(section="meta-moonforge-rauc-raspberry",
                                             weight=40,
                                             text=['WKS_FILE = "moonforge-image-rauc-raspberrypi.wks.in"']),
                           ],
                         },
                         "includes": {
                           "qemu": [
                             FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-qemu.yml"),
                           ],
                           "raspberrypi5": [
                             FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-raspberrypi.yml"),
                           ],
                         },
                       })
