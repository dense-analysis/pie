import datetime
from enum import IntEnum
from typing import NamedTuple


class SourceSystemType(IntEnum):
    """
    Source system type.
    """
    GITHUB = 0
    JIRA = 1


class IssueEventType(IntEnum):
    """
    Issue event type.
    """
    CREATED = 0
    UPDATED = 1
    CLOSED = 2
    COMMENT_ADDED = 3
    REOPENED = 4
    ASSIGNED = 5
    RESOLVED = 6


class Project(NamedTuple):
    """
    Represents a project.
    """
    # The source system for a project.
    source_system: SourceSystemType
    # The organisation or domain for a project.
    owner: str
    # The project name for a project.
    name: str


class IssueComment(NamedTuple):
    """
    Represents an issue comment.
    """
    # The project for the issue comment.
    project: Project
    # The ID of the issue.
    issue_id: int
    # The numerical id for the comment.
    id: int
    # The name of the user that posted the comment.
    username: str
    # The body of a comment.
    body: str
    # The time a comment was created.
    created_at: datetime.datetime


class Issue(NamedTuple):
    """
    Represents an issue.
    """
    # The project for the issue.
    project: Project
    # The numerical id for the issue.
    id: int
    # The parent id for the issue, which is 0 when the issue has no parent.
    parent_id: int
    # The username for the assignee of the issue.
    assignee_username: str
    # The title for the issue.
    title: str
    # The description for the issue.
    description: str
    # An array of labels for the issue.
    labels: list[str]
    # The time the issue was created.
    created_at: datetime.datetime


class IssueEvent(NamedTuple):
    """
    Represents an issue event.
    """
    # The project for the issue.
    project: Project
    # The numerical id for the issue.
    id: int
    # The numerical ID for a related object, such as comment.
    related_object_id: int
    # The id for the parent of an issue, which is 0 when the issue has no parent.
    parent_id: int
    # The type of the IssueEvent.
    type: IssueEventType
    # The username for the assignee for the issue.
    assignee_username: str
    # The timestamp for the issue event.
    timestamp: datetime.datetime
