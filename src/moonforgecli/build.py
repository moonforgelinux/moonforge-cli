# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os
import subprocess

from pathlib import Path

from . import log, kas, utils
from .project import Project


HELP_MSG = "Build a Moonforge project"


def build_project(project: Project) -> int:
    print(f"Building project {project.name} at {project.path}")
    print(f"Machine: {project.machine.name}")
    features = ", ".join([ f.name for f in project.features ])
    print(f"Features: {features}")
    variables = ", ".join([ x for x in project.variables ])
    print(f"Variables: {variables}")
    print(f"Local repo name: {project.local_repo_name}")
    print(f"KAS file: kas/{project.name}-image-base-{project.machine.name}.yml")
    return 0


def add_args(parser):
    parser.add_argument("path", metavar="PATH", default=".",
                        help="the path of the project")


def run(options):
    if options.path == ".":
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(options.path)
    path = Path(project_path)
    if path.exists() and not path.is_dir():
        log.error(f"Project path {path} exists and is not a directory.")
    project = Project.from_toml(path)
    return build_project(project)
