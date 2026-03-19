# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os

from pathlib import Path

from . import log, kas
from .features import get_feature
from .machines import get_machine


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
BBFILE_COLLECTION += "{layer_name}-distro"
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

def sanitize_layer_name(name: str) -> str:
    tokens = [x.lower() for x in name.split()]
    res = "-".join(tokens)
    if not res.startswith("meta-"):
        res = "meta-" + res
    return res


def sanitize_project_name(name: str) -> str:
    tokens = [x.lower() for x in name.split()]
    return tokens[0]


class Project:
    def __init__(self, name: str, path: Path, machine: Machine, features: list[Feature]):
        self._name = name
        self._path = path
        self._machine = machine
        self._features = features

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def machine(self) -> Machine:
        return self._machine

    @property
    def features(self) -> list[Feature]:
        return self._features

    @property
    def local_repo_name(self) -> str:
        return sanitize_layer_name(self._name)

    def to_kas(self) -> str:
        kf = kas.KasFile()
        kf.add_include("meta-moonforge", "kas/include/layer/meta-moonforge-distro.yml")
        kf.add_repo(name="meta-moonforge", url="https://github.com/moonforgelinux/meta-moonforge.git",
                    commit="ce8ff3de25dda42215b7c8dfd201fd39c3960b1f", branch="main")
        kf.add_local_repo(name=f"{self.local_repo_name}", layers=[f"{self.local_repo_name}-distro"])
        kf.set_distro(self._name)
        kf.set_machine(self._machine)
        for feat in self._features:
            kf.add_feature(feat)
        return str(kf)


def add_top_level_files(project: Project) -> None:
    log.info(f"Add top level files for {project.name}")
    with open(project.path / "README.md", "w", encoding="utf-8") as f:
        f.write(README_FORMAT.format(project_name=project.name))


def add_conf_dir(project: Project) -> None:
    log.info(f"Creating layer configuration for {project.name}")

    project_name = sanitize_project_name(project.name)
    layer_name = sanitize_layer_name(project.name)

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
    project_name = sanitize_project_name(project.name)
    layer_name = sanitize_layer_name(project.name)

    log.info(f"Creating kas configuration for {project.name}")
    kas_path = project.path / "kas"
    os.makedirs(kas_path, exist_ok=True)
    with open(kas_path / f"{project_name}-image-base.yml", "w", encoding="utf-8") as f:
        f.write(project.to_kas())


def init_project(path: str, project_name: str, machine: Machine, features: list[Feature]) -> int:
    project_path = Path(path)
    if not project_path.exists():
        os.makedirs(project_path)
    project = Project(project_name, project_path, machine, features)
    add_top_level_files(project)
    add_conf_dir(project)
    add_kas_dir(project)
    return 0


def add_args(parser):
    parser.add_argument("--name", metavar="NAME", help="the project name")
    parser.add_argument("--machine", metavar="MACHINE", default="qemu", help="the target machine")
    parser.add_argument("--feature", metavar="FEATURE", action="append", dest="features", default=[], help="enabled features")
    parser.add_argument("path", metavar="PATH", default=".", help="the path of the project")


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
        features.append(f)
    return init_project(project_path, project_name, machine, features)
