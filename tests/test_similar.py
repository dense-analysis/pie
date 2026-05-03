import sys

from pytest import MonkeyPatch

from pie.similar import Arguments, parse_arguments


def test_parse_arguments_uses_defaults(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["pie.similar"])

    assert parse_arguments() == Arguments(
        config_path="config.toml",
        max_title_distance=0.2,
        max_description_distance=0.2,
    )
