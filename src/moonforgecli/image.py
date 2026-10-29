# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import os

from pathlib import Path

from . import log, term, utils
# from .features import available_features, get_feature
# from .machines import available_machines, get_machine
from .project import Image, Project


HELP_MSG = "Manage image files"

HELP_DESCRIPTION = """The image command manages the image files for a Moonforge project.

Each image can have a machine target and a set of features.
"""  # noqa: E501


def add_args(parser) -> None:
    parser.add_argument("--name", help="The name of the image")
    parser.add_argument("--machine", metavar="MACHINE", default="default",
                        help="the target machine")
    parser.add_argument("--feature", metavar="FEATURE", action="append",
                        dest="features", default=[], help="enabled features")
    parser.add_argument("--variable", metavar="KEY=VALUE", action="append",
                        dest="variables", default=[], help="layer variables")
    parser.add_argument("action", choices=["add", "remove", "list"], help="action to perform")
    parser.add_argument("path", metavar="PATH", default=".",
                        help="the path of the project")


def run(options) -> int:
    if options.path == ".":
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(options.path)
    path = Path(project_path)
    if path.exists() and not path.is_dir():
        log.error(f"Project path {path} exists and is not a directory.")
    project = Project.from_toml(path)
    match options.action:
        case "list":
            res = [term.heading(text="Available images:")]
            for img in project.images:
                name = term.option(img.name)
                res.append(f"- {name}:")
                res.append(f"  machine: {img.machine.name}")
                if len(img.features) > 0:
                    res.append("  features: ")
                    for feat in img.features:
                        res.append(f"    - {feat.name}")
                if len(img.variables) > 0:
                    res.append("  variables: ")
                    for var in img.variables:
                        res.append(f"    - {var} = {img.variables[var]}")
            print("\n".join(res))

        case "add":
            for img in project.images:
                if img.name == options.name:
                    log.error(f"The project already contains an image named {img.name}")
            utils.validate_machine(options.machine)
            utils.validate_features(options.features)
            utils.validate_variables(options.variables, options.features)
            img_args = {
                "name": options.name,
                "machine": options.machine,
                "features": options.features,
                "variables": options.variables,
            }
            project.add_image(Image(**img_args))
            project.update_and_save()

        case "remove":
            found = False
            for img in project.images:
                if img.name == options.name:
                    project.remove_image(img)
                    found = True
                    break

            if not found:
                log.error(f"Unknown image {options.name}")

            project.update_and_save()

    return 0
