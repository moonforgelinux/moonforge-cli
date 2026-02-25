# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import argparse
import os

from pathlib import Path

from . import log


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
BBFILE_COLLECTION += "{layer_name}"
BBFILE_PATTERN_{layer_name} = "^${{LAYERDIR}}/"
BBFILE_PRIORITY_{layer_name} = "20"

LAYERDEPENDS_{layer_name} = "core meta-moonforge-distro"
LAYERSERIES_COMPAT_{layer_name} = "scarthgap"
"""

PROJECT_CONF_FORMAT = """# {project_name} distro configuration
DISTRO = "{project_name}"
DISTRO_NAME = "Full project name"
DISTRO_VERSION = "1.0"

MAINTAINER = "Someone <someone@example.com>"
"""

IMAGE_BASE_FORMAT = """# {project_name} image base
IMAGE_FEATURES += "ssh-server-openssh"
"""

KAS_IMAGE_BASE_FORMAT = """# {project_name}
header:
  version: 16
  includes:
    - repo: meta-moonforge
      file: kas/include/layer/meta-moonforge-distro.yml

repos:
  meta-moonforge:
    url: https://github.com/moonforgelinux/meta-moonforge.git
    commit: ce8ff3de25dda42215b7c8dfd201fd39c3960b1f
    branch: main
  {layer_name}:
    layers:
      meta-{project_name}-distro:

distro: {project_name}
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


def add_top_level_files(path: Path, project_name: str) -> None:
    log.info(f"Add top level files for {project_name}")
    with open(path / "README.md", "w", encoding="utf-8") as f:
        f.write(README_FORMAT.format(project_name=project_name))


def add_conf_dir(path: Path, project: str) -> None:
    log.info(f"Creating layer configuration for {project}")

    project_name = sanitize_project_name(project)
    layer_name = sanitize_layer_name(project)

    log.info(f"Creating layer meta-{project_name}-distro for {project_name}")
    distro_path = path / f"meta-{project_name}-distro"
    os.makedirs(distro_path, exist_ok=True)
    with open(distro_path / "README.md", "w", encoding="utf-8") as f:
        f.write(DISTRO_README_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating distro layer for {project_name}")
    conf_path = distro_path / "conf"
    os.makedirs(conf_path, exist_ok=True)

    log.info(f"Creating layer.conf for {project_name}")
    layer_conf_path = conf_path / "layer.conf"
    with open(layer_conf_path, "w", encoding="utf-8") as f:
        f.write(LAYER_CONF_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating {project_name}.conf distro configuration for {project_name}")
    os.makedirs(conf_path / "distro", exist_ok=True)
    project_conf = f"{project_name}.conf"
    project_conf_path = conf_path / "distro" / project_conf
    with open(project_conf_path, "w", encoding="utf-8") as f:
        f.write(PROJECT_CONF_FORMAT.format(project_name=project_name, layer_name=layer_name))

    log.info(f"Creating image recipe for {project_name}")
    images_path = conf_path / "recipes-core" / "images"
    os.makedirs(images_path, exist_ok=True)
    with open(images_path / "moonforge-image-base.bbappend", "w", encoding="utf-8") as f:
        f.write(IMAGE_BASE_FORMAT.format(project_name=project_name, layer_name=layer_name))


def add_kas_dir(path: Path, project: str) -> None:
    project_name = sanitize_project_name(project)
    layer_name = sanitize_layer_name(project)

    log.info(f"Creating kas configuration for {project}")
    kas_path = path / "kas"
    os.makedirs(kas_path, exist_ok=True)
    with open(kas_path / f"{project_name}-image-base.yml", "w", encoding="utf-8") as f:
        f.write(KAS_IMAGE_BASE_FORMAT.format(project_name=project_name, layer_name=layer_name))


def init_project(path: str, project_name: str) -> int:
    project_path = Path(path)
    if not project_path.exists():
        os.makedirs(project_path)
    add_top_level_files(project_path, project_name)
    add_conf_dir(project_path, project_name)
    add_kas_dir(project_path, project_name)
    return 0


def add_args(parser):
    parser.add_argument("--name", metavar="NAME", help="the project name")
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
    return init_project(project_path, project_name)
