# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from . import log, term
from .features import available_features, get_feature


HELP_MSG = "Show feature information"


def add_args(parser) -> None:
    parser.add_argument("--list", default=False, dest="list", action="store_true",
                        help="list all available features")
    parser.add_argument("features", nargs="*",
                        help="optional list of features to query")


def run(options) -> int:
    if options.list:
        res = [term.heading(text="Available features:")]
        max_name_len = 0
        for f in available_features():
            max_name_len = len(f.name) if len(f.name) > max_name_len else max_name_len
        for f in available_features():
            name = term.option(f.name)
            pad = " ".ljust(max_name_len - len(f.name) + 1)
            res.append(f"- {name}:{pad}{f.description}")
        print("\n".join(res))
        return 0

    if len(options.features) == 0:
        heading = term.heading("usage:")
        command = term.command("moonforge")
        option = term.option("feature")
        print(f"{heading} {command} {option} FEATURE...")
        return 1

    features = []
    for feat in options.features:
        f = get_feature(feat)
        if f is None:
            log.error(f"Invalid feature {feat}.")
        features.append(f)
    
    for feature in features:
        res = []
        res.append(f"{term.heading('Feature:')} {term.bold(feature.name)}")
        res.append("")
        res.append(f"  {feature.description}")
        res.append("")
        if feature.variables is not None:
            res.append(term.heading("Variables:"))
            for var in feature.variables:
                res.append(f"  - {term.green(var.name)}:")
                res.append(f"    {var.description}")
                res.append(f"    Default value: {var.default}")
            res.append("")
        if len(feature.includes) > 0:
            res.append(term.heading("Includes:"))
            for include in feature.includes:
                res.append(f"  - {term.green(include.file)} from {term.green(include.repo)}")
            res.append("")
        if len(feature.conflicts) > 0:
            res.append(term.heading("Conflicts:"))
            for conflict in feature.conflicts:
                res.append(f"  - {term.red(conflict)}")
            res.append("")
        print("\n".join(res))

    return 0
