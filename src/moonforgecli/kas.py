# SPDX-FileCopyrightText: 2026  Igalia S.L.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field

from .machines import Fragment, Machine


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

    def add_include(self, repo: str, file: str) -> None:
        if self._header is None:
            self._header = KasHeader()
        self._header.includes.append(KasInclude(repo, file))

    def add_repo(self, name: str, url: str, commit: str | None = None, branch: str = None) -> None:
        repo = KasRepo(name, url=url, commit=commit, branch=branch, layers=[])
        self._repos.append(repo)

    def add_local_repo(self, name: str, layers: list[str] | None = None):
        repo = KasRepo(name, layers=layers)
        self._repos.append(repo)

    def set_distro(self, distro: str) -> None:
        self._distro = distro

    def set_machine(self, machine: Machine) -> None:
        self._machine = machine
        for inc in self._machine.includes:
            self.add_include(inc.repo, inc.file)

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
        if self._distro is not None:
            res.append(f"distro: {self._distro}")
            res.append("")
        if self._machine is not None:
            res.append(f"machine: {self._machine.name}")
            if self._machine.local_conf is not None:
                res.append("")
                res.append("local_conf_header:")
                for f in self._machine.local_conf:
                    res.append(f"  {f.weight}_{f.section}: |")
                    for t in f.text:
                        res.append(f"    {t}")
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
