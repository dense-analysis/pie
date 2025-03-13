# PIE - Project Intelligence Engine

PIE is a tool for loading project data, such as GitHub issues, and making
it possible to analyse projects for finding duplicate issues, determining
where how much time is being spent on a project, producing new estimates, and
more.

## Installation Instructions

To set up the project, do the following.

```sh
python3.13 -m venv .venv
source .venv/bin/activate
poetry install
```

## Running PIE

You will need the following to run PIE.

1. A running instance of ClickHouse to connect to.
2. The schema from `schema.sql` loaded into the ClickHouse database.
3. A suitable GPU for running Sentence Transformers.
4. Access tokens for services you connect PIE to.

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

To output instances of similar issues, run `python -m pie.similar`. Add
`--help` to see a description of arguments for tuning the similarity. At the
moment this script outputs the most basic information and does not make it
dead simple to look into issues across multiple projects.
