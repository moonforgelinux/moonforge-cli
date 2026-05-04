# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureInclude


PODMAN_FEATURE = Feature(name="podman",
                         description="Container support using Podman",
                         includes=[
                           FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-podman.yml")
                         ],
                         conflicts=["docker"])
