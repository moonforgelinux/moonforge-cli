# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

try:
    import tomllib              # type: ignore
except ImportError:
    import tomli as tomllib     # type: ignore

from collections.abc import Callable
from functools import partial
from pathlib import Path

from . import kas, log, utils

from .features import Feature, get_feature
from .machines import Machine, get_machine


SAFE_PATHS: dict[str, Callable] = {
    "XDG_CACHE_HOME": utils.xdg_cache_home,
    "XDG_CONFIG_HOME": utils.xdg_config_home,
    "HOME": Path.home,
}

PROJECT_META: dict[str, str] = {
    "PROJECT_NAME": "name",
}

MACHINE_META: dict[str, str] = {
    "MACHINE_NAME": "name",
}

EDITIONS: dict[str, list[str]] = {
    "2026.1": [
        "default_image",
        "edition",
        "images",
        "name",
        "vcs",
    ],
}

EDITION_DEFAULT = "2026.1"


class Image:
    """Metadata associated to an image."""
    def __init__(self, **kwargs):
        self._name = kwargs.get("name", "base")
        self._machine = kwargs.get("machine", "qemux86-64")
        self._features = kwargs.get("features", [])
        self._variables = kwargs.get("variables", [])
        self._is_default = kwargs.get("default", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def machine(self) -> Machine:
        return get_machine(self._machine)

    @property
    def features(self) -> list[Feature]:
        return [get_feature(x) for x in self._features]

    @property
    def variables(self) -> dict[str, str]:
        variables = {}
        for var in self._variables:
            try:
                key, value = var.split("=", 1)
                variables[key] = value
            except ValueError:
                log.warning(f"Invalid variable {var} in project.toml")
        return variables

    @property
    def is_default(self) -> bool:
        return self._is_default

    def to_toml(self) -> list[str]:
        res = []
        res.append(f'name = "{self.name}"')
        res.append(f'machine = "{self.machine.name}"')
        features = []
        for feat in self.features:
            features.append(f'"{feat.name}"')
        if len(features) > 0:
            res.append(f"features = [ {', '.join(features)} ]")
        variables = []
        for key in self.variables:
            variables.append(f'"{key}={self._variables[key]}"')
        if len(variables) > 0:
            res.append(f"variables = [ {', '.join(variables)} ]")
        return res


class Project:
    """The metadata for a Moonforge project."""
    def __init__(self, **kwargs):
        self._edition = kwargs.get("edition", EDITION_DEFAULT)
        self._name = kwargs.get("name")
        self._path = kwargs.get("path")
        self._vcs = kwargs.get("vcs", "none")
        self._images = kwargs.get("images", [])
        self._default_image = kwargs.get("default_image", "base")

        # If we don't get a machine, we construct one by default
        if len(self._images) == 0:
            img_args = {
                "name": "base",
                "machine": kwargs.get("machine", "qemux86-64"),
                "features": kwargs.get("features", []),
                "variables": kwargs.get("variables", []),
                "is_default": True,
            }
            self._images.append(Image(**img_args))

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def images(self) -> list[Image]:
        return self._images

    @property
    def local_repo_name(self) -> str:
        return utils.sanitize_layer_name(self._name)

    @property
    def vcs(self) -> str:
        if self._vcs is None:
            return "none"
        return self._vcs

    @property
    def edition(self) -> str:
        return self._edition

    def get_image(self, image: str) -> Image:
        for img in self._images:
            if img.name == image:
                return img
        raise IndexError(f"No image {image} found")

    def add_image(self, image: Image):
        self._images.append(image)

    def remove_image(self, image: Image):
        self._images.remove(image)

    def to_kas(self, path: Path):
        """Writes the project image files under @path."""
        project_name = utils.sanitize_project_name(self.name)

        for img in self._images:
            kf = kas.KasFile()
            kf.add_include(repo=None, file="kas/include/repo/meta-moonforge.yml")
            kf.add_include(repo="meta-moonforge", file="kas/include/layer/meta-moonforge-distro.yml")
            kf.add_local_repo(name=f"{self.local_repo_name}", layers=[f"{self.local_repo_name}-distro"])
            kf.set_distro(self._name)
            kf.set_machine(img.machine)
            for feat in img.features:
                kf.add_feature(feat)
            for key in img.variables:
                kf.add_variable(key, img.variables[key])

            with open(path / f"{project_name}-image-{img.name}-{img.machine.name}.yml", "w", encoding="utf-8") as f:
                f.write(str(kf))

    @classmethod
    def from_toml(cls, path: Path) -> "Project":
        project_toml_path = path.absolute() / ".moonforge" / "project.toml"
        if not path.exists():
            log.error(f"No project found at {path}; use 'moonforge init' to initialize a project.")
        with open(project_toml_path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception as err:
                log.error(f"Invalid project at {path}: {err}")
            edition = data["project"].get("edition", EDITION_DEFAULT)
            if edition not in EDITIONS:
                log.error(f"Invalid edition '{edition}' for the project file.")

            def validate_fields(check, edition_id, valid_fields):
                for field in check:
                    if field not in valid_fields:
                        log.error(f"Invalid field {field} for the given project edition {edition_id}")

            validate_fields(data["project"], edition, EDITIONS[edition])

            def get_2026_1_fields(source):
                args = {}
                for field in EDITIONS["2026.1"]:
                    match field:
                        case _:
                            args[field] = source.get(field)
                return args

            match edition:
                case "2026.1":
                    kwargs = get_2026_1_fields(data["project"])
                case _:
                    log.error(f"Unknown edition {edition}")

            images = []
            for img_data in data["images"]:
                images.append(Image(**img_data))

            kwargs["images"] = images

            return cls(path=path, **kwargs)

    def to_toml(self) -> str:
        res = [
            "[project]",
            f'edition = "{self.edition}"',
            f'name = "{self.name}"',
        ]
        for img in self._images:
            res.extend(["", "[[images]]"])
            res.extend(img.to_toml())
        return "\n".join(res)

    def safe_path_replace(self, path: str, image: str) -> Path:
        """Replace known variables inside paths."""
        res = path
        for env in SAFE_PATHS:
            path_gen = partial(SAFE_PATHS[env])
            res = res.replace(f"@{env}@", str(path_gen()))
        for env in PROJECT_META:
            data = getattr(self, PROJECT_META[env], "")
            res = res.replace(f"@{env}@", data)
        for img in self.images:
            if img.name == image:
                if img.machine is not None:
                    for env in MACHINE_META:
                        data = getattr(img.machine, MACHINE_META[env], "")
                        res = res.replace(f"@{env}@", data)
        return Path(res)
