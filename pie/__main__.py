import logging
import sys
import tomllib
from typing import NamedTuple

from pie.github import load_github_project_issues
from pie.project_processor import ProjectProcessor


class ConfigurationGithubRepo(NamedTuple):
    owner: str
    name: str


class ConfigurationClickhouseSettings(NamedTuple):
    host: str
    port: int
    username: str
    password: str
    database: str


class Configuration(NamedTuple):
    github_token: str
    github_repos: tuple[ConfigurationGithubRepo, ...]
    clickhouse: ConfigurationClickhouseSettings


def load_configuration(filename: str) -> Configuration:
    with open('config.toml', 'rb') as f:
        toml_data = tomllib.load(f)

    clickhouse_data = toml_data.get("clickhouse", {})

    return Configuration(
        clickhouse=ConfigurationClickhouseSettings(
            host=clickhouse_data.get("host", ""),
            port=clickhouse_data.get("port", 8123),
            username=clickhouse_data.get("username", ""),
            password=clickhouse_data.get("password", ""),
            database=clickhouse_data.get("database", ""),
        ),
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
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    config = load_configuration("config.toml")
    processor = ProjectProcessor(
        clickhouse_host=config.clickhouse.host,
        clickhouse_port=config.clickhouse.port,
        clickhouse_username=config.clickhouse.username,
        clickhouse_password=config.clickhouse.password,
        clickhouse_database=config.clickhouse.database,
    )

    for github_repo in config.github_repos:
        load_github_project_issues(
            processor,
            config.github_token,
            github_repo.owner,
            github_repo.name,
        )


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
