import tomllib
from typing import NamedTuple


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
