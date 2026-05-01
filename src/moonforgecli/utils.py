# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os
import sys

from . import log


FOUND_PROGRAMS = {}


def find_program(bin_name: str, path: str | None = None, error_if_not_found: bool = False) -> str | None:
    """Find a program @bin_name inside the given @path, and returns
    its full path if found, or None if the program could not be found.

    The @bin_name will automatically get an extension depending on the
    platform.

    The search @path has the same format of os.environ["PATH"].

    If @error_if_not_found is True, then we'll log an error."""

    # Cache programs to avoid doing the works multiple times
    global FOUND_PROGRAMS

    if path is None and bin_name in FOUND_PROGRAMS:
        return FOUND_PROGRAMS[bin_name]

    if path is None:
        search_paths = os.environ["PATH"].split(os.pathsep)
    else:
        search_paths = path.split(os.pathsep)

    for p in search_paths:
        full_path = os.path.join(p, bin_name)
        if os.path.isfile(full_path):
            if path is None:
                FOUND_PROGRAMS[bin_name] = full_path
            return full_path

    if error_if_not_found:
        log.error(f"Unable to find {bin_name}")

    return None


def sanitize_layer_name(name: str) -> str:
    """Turns a project name into a layer name."""
    tokens = [x.lower() for x in name.split()]
    res = "-".join(tokens)
    if not res.startswith("meta-"):
        res = "meta-" + res
    return res


def sanitize_project_name(name: str) -> str:
    """Sanitizes the project name for use inside a project."""
    tokens = [x.lower() for x in name.split()]
    return tokens[0]
