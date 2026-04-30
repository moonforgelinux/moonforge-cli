# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureFragment, FeatureInclude, FeatureVariable


RAUC_FEATURE = Feature(name="rauc-simple",
                       description="RAUC support with update bundles via update script",
                       includes=[
                         FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-update.yml"),
                       ],
                       local_conf=[
                         FeatureFragment(section="meta-moonforge-rauc-update",
                                         weight=40,
                                         key="RAUC_BUNDLE_URL",
                                         value="http://10.0.2.2:3333/LATEST.raucb"),
                         FeatureFragment(section="meta-moonforge-rauc-update",
                                         weight=40,
                                         key="RAUC_FORCE_REBOOT_ON_UPDATE",
                                         value="1"),
                       ],
                       machine_overrides={
                         "local_conf": {
                           "qemux86-64": [
                             FeatureFragment(section="meta-moonforge-rauc-qemu",
                                             weight=40,
                                             key="WKS_FILE",
                                             value="moonforge-image-rauc-qemux86-64.wks.in"),
                           ],
                           "raspberrypi5": [
                             FeatureFragment(section="meta-moonforge-rauc-raspberry",
                                             weight=40,
                                             key="WKS_FILE",
                                             value="moonforge-image-rauc-raspberrypi.wks.in"),
                             FeatureFragment(section="meta-moonforge-distro",
                                             weight=20,
                                             key="OVERLAYFS_ETC_DEVICE",
                                             value="/dev/mmcblk0p4"),
                           ],
                         },
                         "includes": {
                           "qemux86-64": [
                             FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-qemu.yml"),
                           ],
                           "raspberrypi5": [
                             FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-rauc-raspberrypi.yml"),
                           ],
                         },
                       },
                       variables=[
                         FeatureVariable(name="RAUC_FORCE_REBOOT_ON_UPDATE",
                                         description="Reboot on update",
                                         default="1"),
                       ])
