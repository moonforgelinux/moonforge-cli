# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field

from .features import FeatureFragment, Feature
from .machines import MachineFragment, Machine

from . import log


@dataclass
class KasInclude:
    """Class for kas include directives."""
    repo: str
    file: str


@dataclass
class KasHeader:
    """Class for kas header blocks."""
    includes: list[KasInclude] = field(default_factory=list)
    version: int = 16


@dataclass
class KasFragment:
    section: str
    text: list[str]
    weight: int = 0


@dataclass
class KasRepo:
    """Class for kas repo directives."""
    name: str
    url: str | None = None
    commit: str | None = None
    branch: str | None = None
    layers: list[str] = field(default_factory=list)


class KasFile:
    """Class for kas files."""
    def __init__(self):
        self._header: KasHeader = KasHeader()
        self._repos: list[KasRepo] = []
        self._distro: str | None = None
        self._machine: Machine | None = None
        self._features: list[Feature] | None = []
        self._local_conf: list[KasFragment] = []
        self._wks: list[KasFragment] = []

    def add_include(self, repo: str, file: str) -> None:
        self._header.includes.append(KasInclude(repo, file))

    def add_repo(self, name: str, url: str, commit: str | None = None, branch: str = None) -> None:
        for r in self._repos:
            if r.name == name:
                log.debug(f"Repository {r.name} (url: {r.url}) already exists")
                return
        repo = KasRepo(name, url=url, commit=commit, branch=branch, layers=[])
        self._repos.append(repo)

    def add_local_repo(self, name: str, layers: list[str] | None = None):
        for r in self._repos:
            if r.name == name:
                log.debug(f"Local repository {r.name} already exists")
                return
        repo = KasRepo(name, layers=layers)
        self._repos.append(repo)

    def set_distro(self, distro: str) -> None:
        self._distro = distro

    def set_machine(self, machine: Machine) -> None:
        self._machine = machine

    def add_feature(self, feature: Feature) -> None:
        self._features.append(feature)

    def _build_header(self) -> list[str]:
        output = []
        output.append("header:")
        output.append(f"  version: {self._header.version}")

        includes = []
        if self._machine is not None:
            for include in getattr(self._machine, "includes", []):
                includes.append(include)

        for feature in self._features:
            for include in getattr(feature, "includes", []):
                includes.append(include)

            if self._machine is not None:
                feature_overrides = getattr(feature, "machine_overrides", {})
                feature_override_include = feature_overrides.get("includes", {})
                for include in feature_override_include.get(self._machine.name, []):
                    includes.append(include)

        if len(includes) > 0:
            output.append("  includes:")
            for include in includes:
                output.append(f"    - repo: {include.repo}")
                output.append(f"      file: {include.file}")
            output.append("")

        return output

    def _build_repos(self) -> list[str]:
        repos = []
        repos.extend(self._repos)

        if self._machine is not None:
            for repo in getattr(self._machine, "repos", []):
                repos.append(repo)

        for feature in self._features:
            for repo in getattr(feature, "repos", []):
                repos.append(repo)

            if self._machine is not None:
                feature_overrides = getattr(feature, "machine_overrides", {})
                feature_override_repo = feature_overrides.get("repos", {})
                for repo in feature_override_repo.get(self._machine.name, []):
                    repos.append(repo)

        output = []

        if len(repos) > 0:
            output.append("repos:")

            for r in repos:
                output.append(f"  {r.name}:")
                if r.url is not None:
                    output.append(f"    url: {r.url}")
                if r.commit is not None:
                    output.append(f"    commit: {r.commit}")
                if r.branch is not None:
                    output.append(f"    branch: {r.branch}")
                if len(r.layers) > 0:
                    output.append("    layers:")
                    for layer in r.layers:
                        output.append(f"      {layer}:")

            output.append("")

        return output

    def _build_local_conf(self) -> list[str]:
        fragments = []
        if self._machine is not None:
            for frag in getattr(self._machine, "local_conf", []):
                fragments.append(frag)

        for feature in self._features:
            for frag in getattr(feature, "local_conf", []):
                fragments.append(frag)

            # Add machine overrides
            if self._machine is not None:
                feature_overrides = getattr(feature, "machine_overrides", {})
                feature_override_local_conf = feature_overrides.get("local_conf", {})
                for frag in feature_override_local_conf.get(self._machine.name, []):
                    fragments.append(frag)

        seen_keys = {}
        for frag in fragments:
            if frag.key not in seen_keys:
                seen_keys[frag.key] = frag
            else:
                if seen_keys[frag.key].weight <= frag.weight:
                    seen_keys[frag.key] = frag

        effective_fragments = sorted(seen_keys.values(), key=lambda frag: frag.weight)

        # Split fragments into sections
        sections = {}
        for frag in effective_fragments:
            section = sections.setdefault(f"{frag.weight}_{frag.section}", [])
            section.append(frag)

        output = []
        if len(sections) > 0:
            output.append("local_conf_header:")
            for section in sections.keys():
                output.append(f"  {section}: |")
                for frag in sections[section]:
                    output.append(f'    {frag.key} = "{frag.value}"')

        return output

    def __str__(self) -> str:
        res = []
        res.extend(self._build_header())
        res.extend(self._build_repos())
        if self._distro is not None:
            res.append(f"distro: {self._distro}")
            res.append("")
        if self._machine is not None:
            res.append(f"machine: {self._machine.name}")
            res.append("")
        res.extend(self._build_local_conf())
        return "\n".join(res)
