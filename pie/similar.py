import argparse
from typing import NamedTuple

from pie.clickhouse import find_similar_issues, get_client

from .config import load_configuration


class Arguments(NamedTuple):
    config_path: str
    max_title_distance: float
    max_description_distance: float


def parse_arguments() -> Arguments:
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        "pie.similar",
        description='Find similar issues loaded in from previous processing'
    )

    # Add arguments to the parser
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        help='Path to TOML config file',
        default="config.toml",
    )
    parser.add_argument(
        '-t',
        '--title-distance',
        type=float,
        default=0.2,
        help='Maximum title distance'
    )
    parser.add_argument(
        '-d',
        '--description-distance',
        type=float,
        default=0.2,
        help='Maximum description distance'
    )

    # Parse the arguments and store them in a Namespace object
    args = parser.parse_args()

    return Arguments(
        config_path=args.config,
        max_title_distance=args.title_distance,
        max_description_distance=args.description_distance,
    )


def main() -> None:
    args = parse_arguments()
    config = load_configuration(args.config_path)
    client = get_client(
        host=config.clickhouse.host,
        port=config.clickhouse.port,
        username=config.clickhouse.username,
        password=config.clickhouse.password,
        database=config.clickhouse.database,
    )

    for result in find_similar_issues(
        client,
        max_title_distance=args.max_title_distance,
        max_description_distance=args.max_description_distance,
    ):
        title_distance = result.title_distance
        description_distance = result.description_distance

        print(
            result.issue1_id,
            '->',
            result.issue2_id,
            f'({title_distance:0.2f}, {description_distance:0.2f})',
        )
        print('Title 1:', result[2])
        print('Title 2:', result[3])
        print()


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
