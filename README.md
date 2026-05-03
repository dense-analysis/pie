# PIE - Project Intelligence Engine

PIE is a tool for loading project data, such as GitHub issues, and making
it possible to analyse projects for finding duplicate issues, determining
where how much time is being spent on a project, producing new estimates, and
more.

## Development

To set up the project, do the following.

```sh
pyenv install
python -m pip install uv
uv sync
```

This repo currently targets `Python 3.15.0a8`; `pyenv install` will pick that
up from `.python-version`.

Because Python 3.15 is still alpha, some packages build from source during
`uv sync`. Ensure a working C toolchain and `libffi` headers are installed on
your machine. The Docker image installs these automatically.

You can check the project for errors like so:

```sh
# Run the linter and autofix warnings/errors.
uv run ruff check --fix
# Run the type checker to spot typing issues.
uv run pyright
# Run unit and integration tests.
uv run pytest
```

To add dependencies, use one of the following commands:

```sh
uv add some_package
uv add --dev some_package
```

## Running PIE

You will need the following to run PIE.

1. A running ClickHouse instance.
2. The schema from `schema.sql` loaded into ClickHouse.
3. Access tokens for services PIE connects to.

You will need to configure `config.toml` as such.

```toml
github_token = "ghp_YOUR_PAT_VALUE_HERE"

[clickhouse]

# Use your values for ClickHouse here.
# The following will work with a local instance of ClickHouse.
host = "localhost"
port = 8123
username = "default"
password = ""
database = "default"

# List out as many GitHub repos to load as you want.
[[github_repos]]

owner = "dense-analysis"
name = "ale"
```

## Computing Similar Issues

To output similar issues, run `python -m pie.similar`. Add `--help` to see the
available tuning arguments.

## Docker

Build the images manually like so:

```sh
docker build -t pie:base --target=base .
docker build -t pie:dev --target=dev .
docker build -t pie:prod --target=prod --build-arg RELEASE_VERSION=0.1.0 .
```

The production image uses `al3xos/python-distroless:3.14.4-debian13`, then
copies in the `3.15.0a8` runtime from the slim builder image because no
distroless alpha tag is published.
