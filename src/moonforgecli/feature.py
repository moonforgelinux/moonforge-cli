# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from . import log, term
from .features import available_features, get_feature


HELP_MSG = "Show feature information"

HELP_DESCRIPTION = """The feature command shows the information related to a Moonforge feature.

Each feature can be used in a Moonforge project at initialization time.
"""  # noqa: E501


def add_args(parser) -> None:
    parser.add_argument("action", choices=["info", "list"], help="action to perform")
    parser.add_argument("features", nargs="*", help="optional list of features to query", default=[])


def run(options) -> int:
    match options.action:
        case "list":
            if len(options.features) != 0:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("feature")
                print(f"{heading} {command} {option} list")
                return 1
            res = [term.heading(text="Available features:")]
            max_name_len = 0
            for f in available_features():
                max_name_len = len(f.name) if len(f.name) > max_name_len else max_name_len
            for f in available_features():
                name = term.option(f.name)
                pad = " ".ljust(max_name_len - len(f.name) + 1)
                res.append(f"- {name}:{pad}{f.description}")
            print("\n".join(res))
        case "info":
            if len(options.features) == 0:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("feature")
                print(f"{heading} {command} {option} info FEATURE ...")
                return 1
            features = []
            for feat in options.features:
                try:
                    f = get_feature(feat)
                    features.append(f)
                except IndexError as err:
                    log.error(f"{err}")
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
                if feature.conflicts is not None and len(feature.conflicts) > 0:
                    res.append(term.heading("Conflicts:"))
                    for conflict in feature.conflicts:
                        res.append(f"  - {term.red(conflict)}")
                    res.append("")
                print("\n".join(res))
    return 0
