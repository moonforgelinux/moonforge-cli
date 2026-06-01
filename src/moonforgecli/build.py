# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

import os

from pathlib import Path

from . import container, log
from .config import ConfigSource
from .project import Project


HELP_MSG = "Build a Moonforge project"

HELP_DESCRIPTION = """The build command sets up a containerized environment to build the Moonforge project at the given PATH.

The container engine is defined by the 'container.engine' configuration key.

The container image is defined by the 'container.image_path', 'container.image_name', and 'container.image_version' configuration keys'.

The cached sstate directory is defined by the 'build.sstate_dir' configuration key.

The cached downloads directory is defined by the 'build.download_dir' configuration key.

The values of 'build.sstate_dir' and 'build.download_dir' can contain these placeholders:

- @XDG_CACHE_HOME@: expands to the XDG_CACHE_HOME environment variable
- @XDG_CONFIG_HOME@: expands to the XDG_CONFIG_HOME environment variable
- @HOME@: expands to the HOME environment variable
- @PROJECT_NAME@: expands to the project's name
- @MACHINE_NAME@: expands to the project's machine name

The build artefacts are stored in the "build" directory.

Examples:

- Build the project in the current directory:

    moonforge build .

- Build the project in the Project/derivative directory:

    moonforge build Project/derivative

- Build the project in the current directory, with an additional fragment:

    moonforge build --fragment kas/common/debug.yml .
"""  # noqa: E501


def build_project(
    project: Project,
    source: ConfigSource,
    fragments: list[Path],
    runtime_args: str | None,
) -> int:
    log.info(f"Building project {project.name} at {project.path}")

    return container.setup_container(
        project,
        source,
        container.ContainerCommand.BUILD,
        interactive=False,
        writable=False,
        fragments=fragments,
        runtime_args=runtime_args,
    )


def add_args(parser):
    parser.add_argument("--fragment", metavar="FILE", dest="fragments",
                        action="append", default=[], help="additional kas fragments")
    parser.add_argument("--runtime-args", help="additional arguments for the container runtime")
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
    source = ConfigSource.load_all(project_path=path)
    fragments = []
    for frag in options.fragments:
        try:
            p = Path(frag).resolve(strict=True)
        except OSError as err:
            log.error(f"Unable to resolve fragment {frag}: {err}")
        fragments.append(p)
    return build_project(project, source, fragments, options.runtime_args)
