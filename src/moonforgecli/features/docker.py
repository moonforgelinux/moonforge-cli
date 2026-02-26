# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

from . import Feature, FeatureFragment, FeatureInclude


DOCKER_FEATURE = Feature(name="docker",
                         description="Docker support",
                         includes=[
                           FeatureInclude("meta-moonforge", "kas/include/layer/meta-moonforge-docker.yml")
                         ])
