from typing import NamedTuple

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from .issue import Issue, IssueComment, IssueEvent, Project


def get_client(
    host: str,
    port: int,
    username: str,
    password: str,
    database: str,
) -> Client:
    client = clickhouse_connect.get_client(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
    )

    if not client.ping():
        raise RuntimeError("Failed to connect to ClickHouse")

    return client


def insert_issue(
    client: Client,
    issue: Issue,
    title_vector: list[float],
    description_vector: list[float],
) -> None:
    client.insert(
        "issues",
        data=[
            (
                int(issue.project.source_system),
                issue.project.owner,
                issue.project.name,
                issue.id,
                issue.parent_id,
                issue.assignee_username,
                issue.title,
                title_vector,
                issue.description,
                description_vector,
                issue.labels,
                issue.created_at,
            ),
        ],
        column_names=[
            "source_system",
            "project_owner",
            "project_name",
            "id",
            "parent_id",
            "assignee_username",
            "title",
            "title_vector",
            "description",
            "description_vector",
            "labels",
            "created_at",
        ],
    )


def issue_exists(
    client: Client,
    project: Project,
    id: int,
) -> bool:
    result = client.query(
        """
        SELECT 1
        FROM issues
        WHERE source_system = %s
        AND project_owner = %s
        AND project_name = %s
        AND id = %s
        LIMIT 1
        """,
        (project.source_system, project.owner, project.name, id)
    )

    return len(result.result_rows) > 0


def insert_issue_comment(
    client: Client,
    issue_comment: IssueComment,
    body_vector: list[float],
) -> None:
    client.insert(
        "issue_comments",
        data=[
            (
                int(issue_comment.project.source_system),
                issue_comment.project.owner,
                issue_comment.project.name,
                issue_comment.issue_id,
                issue_comment.id,
                issue_comment.username,
                issue_comment.body,
                body_vector,
                issue_comment.created_at,
            ),
        ],
        column_names=[
            "source_system",
            "project_owner",
            "project_name",
            "issue_id",
            "id",
            "username",
            "body",
            "body_vector",
            "created_at",
        ],
    )


def issue_comment_exists(
    client: Client,
    project: Project,
    issue_id: int,
    id: int,
) -> bool:
    result = client.query(
        """
        SELECT 1
        FROM issue_comments
        WHERE source_system = %s
        AND project_owner = %s
        AND project_name = %s
        AND issue_id = %s
        AND id = %s
        LIMIT 1
        """,
        (project.source_system, project.owner, project.name, issue_id, id)
    )

    return len(result.result_rows) > 0


def insert_issue_event(
    client: Client,
    issue_event: IssueEvent,
) -> None:
    client.insert(
        "issue_events",
        data=[
            (
                int(issue_event.project.source_system),
                issue_event.project.owner,
                issue_event.project.name,
                issue_event.id,
                issue_event.parent_id,
                int(issue_event.type),
                issue_event.assignee_username,
                issue_event.timestamp,
            ),
        ],
        column_names=[
            "source_system",
            "project_owner",
            "project_name",
            "id",
            "parent_id",
            "type",
            "assignee_username",
            "timestamp",
        ],
    )


def issue_event_exists(
    client: Client,
    project: Project,
    issue_id: int,
    related_object_id: int,
) -> bool:
    result = client.query(
        """
        SELECT 1
        FROM issue_events
        WHERE source_system = %s
        AND project_owner = %s
        AND project_name = %s
        AND id = %s
        AND related_object_id = %s
        LIMIT 1
        """,
        (
            project.source_system,
            project.owner,
            project.name,
            issue_id,
            related_object_id,
        )
    )

    return len(result.result_rows) > 0


class SimilarIssueMatch(NamedTuple):
    issue1_id: int
    issue2_id: int
    issue1_title: str
    issue2_title: str
    title_distance: float
    description_distance: float


def find_similar_issues(
    client: Client,
    max_title_distance: float,
    max_description_distance: float,
) -> list[SimilarIssueMatch]:
    result = client.query(
        """
        SELECT
            issue_1.id,
            issue_2.id,
            issue_1.title,
            issue_2.title,
            cosineDistance(
                issue_1.title_vector,
                issue_2.title_vector
            ) AS title_distance,
            cosineDistance(
                issue_1.description_vector,
                issue_2.description_vector
            ) AS description_distance
        FROM issues AS issue_1
        LEFT JOIN issues AS issue_2
        ON issue_1.source_system = issue_2.source_system
        AND issue_1.project_owner = issue_2.project_owner
        AND issue_1.project_name = issue_2.project_name
        LEFT JOIN issue_events AS ie_1
        ON ie_1.source_system = issue_1.source_system
        AND ie_1.project_owner = issue_1.project_owner
        AND ie_1.project_name = issue_1.project_name
        AND ie_1.id = issue_1.id
        AND ie_1.type = 'CLOSED'
        LEFT JOIN issue_events AS ie_2
        ON ie_2.source_system = issue_2.source_system
        AND ie_2.project_owner = issue_2.project_owner
        AND ie_2.project_name = issue_2.project_name
        AND ie_2.id = issue_2.id
        AND ie_2.type = 'CLOSED'
        WHERE issue_1.id != issue_2.id
        AND cosineDistance(
            issue_1.title_vector,
            issue_2.title_vector
        ) <= %s
        AND cosineDistance(
            issue_1.description_vector,
            issue_2.description_vector
        ) <= %s
        AND ie_1.id = 0
        AND ie_2.id = 0
        """,
        (
            max_title_distance,
            max_description_distance,
        )
    )

    return [SimilarIssueMatch(*row) for row in result.result_rows]
