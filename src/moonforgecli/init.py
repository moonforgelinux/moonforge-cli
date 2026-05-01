# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os
import subprocess

from pathlib import Path

from . import log, kas, utils
from .features import check_conflicts, get_feature
from .machines import get_machine
from .project import Project


HELP_MSG = "Initialize a Moonforge project"

README_FORMAT = """# {project_name}

This is a Moonforge OS derivative distribution.

## Set up

The host requirements are:

- docker or podman
- Python 3
- Pip

Install the kas container with the required tooling using pip:

```sh
$ pip install --user kas==5.0
```
"""

DISTRO_README_FORMAT = """# meta-{project_name}-distro

This layer extends meta-moonforge-distro with customizations needed to build a
derivative distribution.
"""

LAYER_CONF_FORMAT = """# {project_name} layer configuration
BBPATH .= ":${{LAYERDIR}}"
BBFILES += "${{LAYERDIR}}/recipes-*/*/*.bb ${{LAYERDIR}}/recipes-*/*/*.bbappend"
BBFILE_COLLECTIONS += "{layer_name}-distro"
BBFILE_PATTERN_{layer_name}-distro = "^${{LAYERDIR}}/"
BBFILE_PRIORITY_{layer_name}-distro = "20"

LAYERDEPENDS_{layer_name}-distro = "core meta-moonforge-distro"
LAYERSERIES_COMPAT_{layer_name}-distro = "scarthgap"
"""

PROJECT_CONF_FORMAT = """# {project_name} distro configuration
require conf/distro/moonforge.conf

DISTRO = "{project_name}"
DISTRO_NAME = "Full project name"
DISTRO_VERSION = "1.0"

MAINTAINER = "Someone <someone@example.com>"
"""

IMAGE_BASE_FORMAT = """# {project_name} image base
IMAGE_FEATURES += "ssh-server-openssh"
"""

META_MOONFORGE_YML = """header:
  version: 16

repos:
  meta-moonforge:
    url: {url}
    commit: {commit}
    branch: {branch}
"""

META_MOONFORGE_URL = "https://github.com/moonforgelinux/meta-moonforge.git"

META_MOONFORGE_COMMIT = "42b1aeefb1327785c48925e62719fa13d55c8e13"

META_MOONFORGE_BRANCH = "main"


def add_top_level_files(project: Project) -> None:
    log.info(f"Add top level files for {project.name}")
    with open(project.path / "README.md", "w", encoding="utf-8") as f:
        f.write(README_FORMAT.format(project_name=project.name))


def add_conf_dir(project: Project) -> None:
    log.info(f"Creating layer configuration for {project.name}")

    project_name = utils.sanitize_project_name(project.name)
    layer_name = utils.sanitize_layer_name(project.name)

    log.info(f"Creating layer meta-{project_name}-distro for {project.name}")
    distro_path = project.path / f"meta-{project_name}-distro"
    os.makedirs(distro_path, exist_ok=True)
    with open(distro_path / "README.md", "w", encoding="utf-8") as f:
        f.write(DISTRO_README_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating distro layer for {project.name}")
    conf_path = distro_path / "conf"
    os.makedirs(conf_path, exist_ok=True)

    log.info(f"Creating layer.conf for {project.name}")
    layer_conf_path = conf_path / "layer.conf"
    with open(layer_conf_path, "w", encoding="utf-8") as f:
        f.write(LAYER_CONF_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating {project_name}.conf distro configuration for {project.name}")
    os.makedirs(conf_path / "distro", exist_ok=True)
    project_conf = f"{project_name}.conf"
    project_conf_path = conf_path / "distro" / project_conf
    with open(project_conf_path, "w", encoding="utf-8") as f:
        f.write(PROJECT_CONF_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating image recipe for {project.name}")
    images_path = distro_path / "recipes-core" / "images"
    os.makedirs(images_path, exist_ok=True)
    with open(images_path / "moonforge-image-base.bbappend", "w", encoding="utf-8") as f:
        f.write(IMAGE_BASE_FORMAT.format(project_name=project_name, layer_name=layer_name))


def add_kas_dir(project: Project) -> None:
    project_name = utils.sanitize_project_name(project.name)
    layer_name = utils.sanitize_layer_name(project.name)

    kas_path = project.path / "kas"
    os.makedirs(kas_path, exist_ok=True)

    log.info(f"Creating kas include directories for {project.name}")
    repo_include_path = kas_path / "include" / "repo"
    os.makedirs(repo_include_path, exist_ok=True)
    with open(repo_include_path / "meta-moonforge.yml", "w", encoding="utf-8") as f:
        f.write(META_MOONFORGE_YML.format(url=META_MOONFORGE_URL,
                                          commit=META_MOONFORGE_COMMIT,
                                          branch=META_MOONFORGE_BRANCH))

    log.info(f"Creating kas configuration for {project.name}")
    with open(kas_path / f"{project_name}-image-base-{project.machine.name}.yml", "w", encoding="utf-8") as f:
        f.write(project.to_kas())


def init_vcs(project: Project) -> None:
    args = []
    if project.vcs == "none":
        return
    elif project.vcs == "git":
        git_bin = utils.find_program("git")
        if not git_bin:
            log.warning("Unable to find git in the path")
            return
        args += [git_bin, "init", str(project.path)]

        with open(project.path / ".gitignore", "w", encoding="utf-8") as f:
            f.write("/build")

    try:
        log.info(f"Initializing {project.vcs} repository")
        proc = subprocess.Popen(args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        if proc.returncode:
            log.warning(f"Unable to initialize VCS: {err}")
            return
    except Exception as e:
        log.warning(f"Unable to initialize VCS: {e}")


def init_project(project: Project) -> int:
    if not project.path.exists():
        os.makedirs(project.path)
    add_top_level_files(project)
    add_conf_dir(project)
    add_kas_dir(project)
    init_vcs(project)
    return 0


def add_args(parser):
    parser.add_argument("--name", metavar="NAME", help="the project name")
    parser.add_argument("--machine", metavar="MACHINE", default="default",
                        help="the target machine")
    parser.add_argument("--feature", metavar="FEATURE", action="append",
                        dest="features", default=[], help="enabled features")
    parser.add_argument("--variable", metavar="KEY=VALUE", action="append",
                        dest="variables", default=[], help="layer variables")
    parser.add_argument("--vcs", metavar="VCS", default="git", choices=["none", "git"],
                        help="initialize the project for the given version control (values: git, none)")
    parser.add_argument("path", metavar="PATH", default=".",
                        help="the path of the project")


def run(options):
    project_name = options.name or "Custom"
    if options.path == ".":
        project_path = os.getcwd()
    else:
        project_path = os.path.abspath(options.path)
    path = Path(project_path)
    if path.exists() and not path.is_dir():
        log.error(f"Project path {path} exists and is not a directory.")
    machine = get_machine(options.machine)
    if machine is None:
        log.error(f"Invalid target machine {options.machine}. "
                   "Use 'list-machines' to list the available machines.")
    features = []
    for feat in options.features:
        f = get_feature(feat)
        if f is None:
            log.error(f"Invalid feature {feat}.")
        conflicts = check_conflicts(feat, options.features)
        if conflicts is not None:
            res = ", ".join(conflicts)
            log.error(f"Feature {feat} conflicts with the following features: {res}")
        features.append(f)
    variables = {}
    for var in options.variables:
        try:
            (key, value) = var.split("=", 1)
        except ValueError as err:
            log.error(f"Invalid variable '{var}': {err}")
        found = False
        for feat in features:
            for var in feat.variables:
                if var.name == key:
                    found = True
                    break
        if not found:
            log.error(f"Variable {key} is not part of any feature")
        variables[key] = value
    project = Project(project_name, path, machine, features, variables, options.vcs)
    return init_project(project)
