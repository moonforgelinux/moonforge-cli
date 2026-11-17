# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os

from pathlib import Path

from . import log, term
from .features import Feature, check_conflicts, get_feature
from .machines import get_machine


FOUND_PROGRAMS: dict[str, str] = {}


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


def xdg_config_home() -> Path:
    """Get a path for XDG_CONFIG_HOME."""
    env_dir = os.environ.get("XDG_CONFIG_HOME")
    if env_dir is not None:
        res = Path(env_dir)
    else:
        res = Path.home() / ".config"
    os.makedirs(res, exist_ok=True)
    return res


def xdg_cache_home() -> Path:
    """Get a path for XDG_CACHE_HOME."""
    env_dir = os.environ.get("XDG_CACHE_HOME")
    if env_dir is not None:
        res = Path(env_dir)
    else:
        res = Path.home() / ".cache"
    os.makedirs(res, exist_ok=True)
    return res


def validate_machine(machine: str):
    """Validates the machine name. Aborts on error."""
    try:
        _ = get_machine(machine)
    except IndexError:
        log.error(f"Invalid target machine {machine}. "
                  f"Use {term.command('machine')} to list the available machines.")


def validate_features(features: list[str]):
    """Validates a list of feature names, and checks for conflicts. Aborts on error."""
    local_features: list[Feature] = []
    for feat in features:
        try:
            f = get_feature(feat)
        except IndexError:
            log.error(f"Invalid feature {feat}. "
                      f"Use {term.command('feature')} to list the available features.")
        conflicts = check_conflicts(feat, features)
        if len(conflicts) > 0:
            res = ", ".join(conflicts)
            log.error(f"Feature {feat} conflicts with the following features: {res}")
        local_features.append(f)


def validate_variables(variables: list[str], features: list[str]):
    """Validates a list of variables. Aborts on error."""
    local_features: list[Feature] = []
    for feat in features:
        try:
            f = get_feature(feat)
        except IndexError:
            log.error(f"Invalid feature {feat}. "
                      f"Use {term.command('feature')} to list the available features.")
        conflicts = check_conflicts(feat, features)
        if len(conflicts) > 0:
            res = ", ".join(conflicts)
            log.error(f"Feature {feat} conflicts with the following features: {res}")
        local_features.append(f)
    if len(variables) != 0 and len(local_features) == 0:
        log.error("No features specified")
    local_variables: dict[str, str] = {}
    for var in variables:
        try:
            (key, value) = var.split("=", 1)
        except ValueError as err:
            log.error(f"Invalid variable '{var}': {err}")
        found = False
        for local_feat in local_features:
            if local_feat.variables is None:
                continue
            for local_var in local_feat.variables:
                if local_var.name == key:
                    found = True
                    break
        if not found:
            log.error(f"Variable {key} is not part of any feature")
        local_variables[key] = value
