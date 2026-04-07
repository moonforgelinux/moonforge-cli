# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os
import sys

from . import log
from .term import AnsiEscape
from .features import available_features, get_feature


HELP_MSG = "Show feature information"


def add_args(parser) -> None:
    parser.add_argument("--list", default=False, dest="list", action="store_true",
                        help="list all available features")
    parser.add_argument("features", nargs="*",
                        help="optional list of features to query")


def run(options) -> int:
    if options.list:
        res = [str(AnsiEscape(text="Available features:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD))]
        max_name_len = 0
        for f in available_features():
            max_name_len = len(f.name) if len(f.name) > max_name_len else max_name_len
        for f in available_features():
            name = str(AnsiEscape(text=f.name, fg_color=AnsiEscape.GREEN_FG))
            pad = " ".ljust(max_name_len - len(f.name) + 1)
            res.append(f"- {name}:{pad}{f.description}")
        print("\n".join(res))
        return 0

    if len(options.features) == 0:
        print(f"{AnsiEscape(text="usage:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)} moonforge feature FEATURE...")
        return 1

    features = []
    for feat in options.features:
        f = get_feature(feat)
        if f is None:
            log.error(f"Invalid feature {feat}.")
        features.append(f)
    
    for feature in features:
        res = []
        res.append(str(AnsiEscape(text="Feature: ", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)) + str(AnsiEscape(text=feature.name, mods=AnsiEscape.BOLD)))
        res.append("")
        res.append(f"  {feature.description}")
        res.append("")
        if len(feature.includes) > 0:
            res.append(str(AnsiEscape(text="Includes:", fg_color=AnsiEscape.BLUE_FG, mods=AnsiEscape.BOLD)))
            for include in feature.includes:
                res.append(f"  - {AnsiEscape(text=include.file, fg_color=AnsiEscape.GREEN_FG)} from {AnsiEscape(text=include.repo, fg_color=AnsiEscape.GREEN_FG)}")
            res.append("")
        print("\n".join(res))

    return 0
