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
    layers: list[KasLayer] = field(default_factory=list)


class KasFile:
    """Class for kas files."""
    def __init__(self):
        self._header: KasHeader | None = None
        self._repos: list[KasRepo] = []
        self._distro: str | None = None
        self._machine: Machine | None = None
        self._features: list[Feature] | None = []
        self._local_conf: list[KasFragment] = []
        self._wks: list[KasFragment] = []

    def add_include(self, repo: str, file: str) -> None:
        if self._header is None:
            self._header = KasHeader()
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
        for inc in machine.includes:
            self.add_include(inc.repo, inc.file)
        for frag in machine.local_conf:
            self._local_conf.append(KasFragment(section=frag.section,
                                                weight=frag.weight,
                                                text=frag.text))
        for frag in machine.wks_file:
            self._wks.append(KasFragment(section=frag.section,
                                         weight=frag.weight,
                                         text=frag.text))

    def add_feature(self, feature: Feature) -> None:
        self._features.append(feature)
        for inc in feature.includes:
            self.add_include(inc.repo, inc.file)
        for frag in feature.local_conf:
            self._local_conf.append(KasFragment(section=frag.section,
                                                weight=frag.weight,
                                                text=frag.text))
        machine_overrides = feature.machine_overrides
        machine_includes = machine_overrides.get('includes', {})
        for inc in machine_includes.get(self._machine.name, []):
            self.add_include(inc.repo, inc.file)
        machine_local_conf = machine_overrides.get('local_conf', {})
        for frag in machine_local_conf.get(self._machine.name, []):
            self._local_conf.append(KasFragment(section=frag.section,
                                                weight=frag.weight,
                                                text=frag.text))
        machine_wks_file = machine_overrides.get('wks_file', {})
        if machine_wks_file.get(self._machine.name) is not None:
            self._wks = []
            for frag in machine_wks_file.get(self._machine.name):
                self._wks.append(KasFragment(section=frag.section,
                                             weight=frag.weight,
                                             text=frag.text))

    def __str__(self) -> str:
        res = []
        if self._header is not None:
            res.append("header:")
            res.append(f"  version: {self._header.version}")
            if len(self._header.includes) > 0:
                res.append("  includes:")
                for i in self._header.includes:
                    res.append(f"    - repo: {i.repo}")
                    res.append(f"      file: {i.file}")
            res.append("")
        if len(self._local_conf) > 0 or len(self._wks) > 0:
            res.append("local_conf_header:")
            for frag in self._local_conf:
                res.append(f"  {frag.weight}_{frag.section}: |")
                for line in frag.text:
                    res.append(f"    {line}")
            for frag in self._wks:
                res.append(f"  {frag.weight}_{frag.section}: |")
                for line in frag.text:
                    res.append(f"    {line}")
            res.append("")
        if self._distro is not None:
            res.append(f"distro: {self._distro}")
            res.append("")
        if self._machine is not None:
            res.append(f"machine: {self._machine.name}")
            res.append("")
        if len(self._repos) > 0:
            res.append("repos:")
            for r in self._repos:
                res.append(f"  {r.name}:")
                if r.url is not None:
                    res.append(f"    url: {r.url}")
                if r.commit is not None:
                    res.append(f"    commit: {r.commit}")
                if r.branch is not None:
                    res.append(f"    branch: {r.branch}")
                if len(r.layers) > 0:
                    res.append("    layers:")
                    for layer in r.layers:
                        res.append(f"      {layer}:")
        return "\n".join(res)
