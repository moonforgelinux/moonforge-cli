# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureFragment, FeatureInclude


GRAPHICS_WESTON_FEATURE = Feature(name="graphics-weston",
                                  description="Graphics support, using Weston",
                                  includes=[
                                    FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-graphics.yml")
                                  ],
                                  conflicts=['graphics-wpe'])
