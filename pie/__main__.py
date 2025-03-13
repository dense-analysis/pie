import logging
import sys

from pie.github import load_github_project_issues
from pie.project_processor import ProjectProcessor

from .config import load_configuration


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
