# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureFragment, FeatureInclude, FeatureVariable


GRAPHICS_WPE_FEATURE = Feature(name="graphics-wpe",
                               description="Web Platform for Embedded",
                               includes=[
                                 FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-graphics.yml"),
                                 FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-wpe.yml"),
                               ],
                               local_conf=[
                                 FeatureFragment(section="meta-moonforge-wpe",
                                                 weight=30,
                                                 key="WAYLAND_COG_LAUNCH_URL",
                                                 value="http://10.0.2.2:8080"),
                               ],
                               conflicts=['graphics-weston'],
                               variables=[
                                 FeatureVariable(name="WAYLAND_COG_LAUNCH_URL",
                                                 description="The URL to display at boot",
                                                 default="http://10.0.2.2:8080"),
                               ])
