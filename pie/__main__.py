import tomllib
from typing import NamedTuple

from pie.github import load_github_project_issues
from pie.project_processor import ProjectProcessor


class ConfigurationGithubRepo(NamedTuple):
    owner: str
    name: str

class Configuration(NamedTuple):
    github_token: str
    github_repos: tuple[ConfigurationGithubRepo, ...]


def load_configuration(filename: str) -> Configuration:
    with open('config.toml', 'rb') as f:
        toml_data = tomllib.load(f)

    return Configuration(
        github_token=toml_data.get("github_token", ""),
        github_repos=tuple(
            ConfigurationGithubRepo(
                owner=repo_data.get("owner", ""),
                name=repo_data.get("name", ""),
            )
            for repo_data in
            toml_data.get("github_repos", [])
        ),
    )


def main() -> None:
    config = load_configuration("config.toml")
    processor = ProjectProcessor()

    for github_repo in config.github_repos:
        load_github_project_issues(
            processor,
            config.github_token,
            github_repo.owner,
            github_repo.name,
        )


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
