from pathlib import Path

from pie.config import load_configuration


def test_load_configuration_reads_requested_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
github_token = "token"

[clickhouse]
host = "localhost"
port = 8123
username = "default"
password = ""
database = "issues"

[[github_repos]]
owner = "dense-analysis"
name = "pie"
""".strip(),
        encoding="utf-8",
    )

    config = load_configuration(str(config_path))
    repo = config.github_repos[0]

    assert config.github_token == "token"
    assert config.clickhouse.host == "localhost"
    assert config.clickhouse.database == "issues"
    assert repo.owner == "dense-analysis"
    assert repo.name == "pie"
