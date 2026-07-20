# SPDX-FileCopyrightText: 2026 Igalia S.L.
# SPDX-License-Identifier: MIT

import os

from pathlib import Path

from . import log, term, utils
from .project import Project


HELP_MSG = "Show repository information"

HELP_DESCRIPTION = """The repository command operates on repositories used by a Moonforge project.

Repositories are identified by a name, and can either be local or remote.

Repositories are included in the generated KAS files, and can be used to point to additional definitions and layers.

Repositories are downloaded and included at build time.
"""  # noqa: E501

REPO_YML = """header:
  version: 16

repos:
  {name}:
    url: {url}
    commit: {commit}
    branch: {branch}
"""  # noqa: E501


def write_repo_file(project: Project, add: str | None = None, remove: str | None = None) -> None:
    project_name = utils.sanitize_project_name(project.name)
    kas_path = project.path / "kas"
    if add is not None:
        name = add
        action = "add"
    elif remove is not None:
        name = remove
        action = "remove"
    else:
        return
    repo_path = kas_path / "include" / "repo"
    repo_file_name = f"{name}.yml"
    if action == "add":
        log.info(f"Adding repository {name}")
        repo = project.repos[name]
        with open(repo_path / repo_file_name, "w", encoding="utf-8") as f:
            f.write(REPO_YML.format(name=name,
                                    url=repo["url"],
                                    commit=repo["commit"],
                                    branch=repo["branch"]))
    elif action == "remove":
        log.info(f"Removing repository {name}")
        repo_file = repo_path / repo_file_name
        try:
            repo_file.unlink(missing_ok=True)
        except Exception as err:
            log.error(f"Unable to remove repository file {repo_file_name}: {err}")
    log.info(f"Updating image base file for {project_name}")
    with open(kas_path / f"{project_name}-image-base-{project.machine.name}.yml", "w", encoding="utf-8") as f:
        f.write(project.to_kas())


def write_project(project: Project) -> None:
    meta_path = project.path / ".moonforge"
    os.makedirs(meta_path, exist_ok=True)
    with open(meta_path / "project.toml", "w", encoding="utf-8") as f:
        f.write(project.to_toml())


def add_args(parser) -> None:
    parser.add_argument("action", choices=["add", "remove", "list"], help="action to perform")
    parser.add_argument("name", nargs="?", help="the name of the remote")
    parser.add_argument("-u", "--url", dest="url", help="the URL of the repository")
    parser.add_argument("-t", "--branch", dest="branch", default="main", help="the branch of the repository")
    parser.add_argument("-c", "--commit", dest="commit", help="the commit of the repository")
    parser.add_argument("--required", action="store_true", help="whether the repository is required")


def run(options) -> int:
    project_path = os.getcwd()
    path = Path(project_path)
    if path.exists() and not path.is_dir():
        log.error(f"Project path {path} exists and is not a directory.")
    project = Project.from_toml(path)
    match options.action:
        case "list":
            repos = {}
            max_name_len = 0
            for name in project.repos:
                max_name_len = len(name) if len(name) > max_name_len else max_name_len
                repos[name] = project.repos[name]
            res = [term.heading(text="Repositories:")]
            for name in repos:
                repo = repos[name]
                pad = " ".ljust(max_name_len - len(name) + 1)
                extra_pad = " ".ljust(max_name_len + 1)
                res.append(f"- {term.option(name)}:{pad}{repo['url']}")
                res.append(f"  {extra_pad} {term.bold("commit:")} {repo['commit']}")
                res.append(f"  {extra_pad} {term.bold("branch:")} {repo['branch']}")
                if repo["required"]:
                    res.append(f"  {extra_pad} {term.bold("required:")} {term.green("yes")}")
            print("\n".join(res))
        case "add":
            if not options.name:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("repository")
                print(f"{heading} {command} {option} add <name>")
                return 1
            if options.url is not None:
                if options.commit is None:
                    log.error("Remote repositories need a commit SHA")
                if options.name in project.repos:
                    log.error(f"Repository {options.name} is already included")
                project.add_repo(options.name,
                                 url=options.url,
                                 commit=options.commit,
                                 branch=options.branch,
                                 required=options.required)
            write_repo_file(project, add=options.name)
            write_project(project)
        case "remove":
            if not options.name:
                heading = term.heading("usage:")
                command = term.command("moonforge")
                option = term.option("repository")
                print(f"{heading} {command} {option} remove <name>")
                return 1
            if options.name not in project.repos:
                log.error(f"Repository {options.name} not found")
            project.remove_repo(options.name)
            write_repo_file(project, remove=options.name)
            write_project(project)
    return 0
