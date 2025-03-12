from github import Github
from github.Issue import Issue as GithubIssue

from .issue import Issue, IssueComment, IssueEvent, IssueEventType, Project, SourceSystemType
from .project_processor import ProjectProcessor


def fetch_github_issues(
    processor: ProjectProcessor,
    client: Github,
    project: Project,
) -> None:
    repo = client.get_repo(f"{project.owner}/{project.name}")

    for github_issue in repo.get_issues(state="all"):
        processor.store_issue(Issue(
            project=project,
            id=github_issue.id,
            parent_id=0,
            assignee_username=(
                github_issue.assignee.login
                if github_issue.assignee is not None else
                ""
            ),
            title=github_issue.title,
            description=github_issue.body,
            labels=[label.name for label in github_issue.labels],
            created_at=github_issue.created_at,
        ))
        fetch_github_issue_events(
            processor,
            project,
            github_issue,
        )
        fetch_github_issue_comments(
            processor,
            project,
            github_issue,
        )


def fetch_github_issue_events(
    processor: ProjectProcessor,
    project: Project,
    github_issue: GithubIssue,
) -> None:
    assignee_username = (
        github_issue.assignee.login
        if github_issue.assignee is not None else
        ""
    )

    # Store created event
    processor.store_issue_event(IssueEvent(
        project=project,
        id=github_issue.id,
        parent_id=0,
        type=IssueEventType.CREATED,
        assignee_username=assignee_username,
        timestamp=github_issue.created_at,
    ))

    if github_issue.closed_at:
        # Store closed event
        processor.store_issue_event(IssueEvent(
            project=project,
            id=github_issue.id,
            parent_id=0,
            type=IssueEventType.CLOSED,
            assignee_username=assignee_username,
            timestamp=github_issue.closed_at,
        ))


def fetch_github_issue_comments(
    processor: ProjectProcessor,
    project: Project,
    github_issue: GithubIssue,
):
    assignee_username = (
        github_issue.assignee.login
        if github_issue.assignee is not None else
        ""
    )

    for comment in github_issue.get_comments():
        processor.store_issue_comment(IssueComment(
            project=project,
            issue_id=github_issue.id,
            id=comment.id,
            username=comment.user.login,
            body=comment.body,
            created_at=comment.created_at,
        ))

        # Store a comment event
        processor.store_issue_event(IssueEvent(
            project=project,
            id=github_issue.id,
            parent_id=0,
            type=IssueEventType.COMMENT_ADDED,
            assignee_username=assignee_username,
            timestamp=comment.created_at,
        ))


def load_github_project_issues(
    processor: ProjectProcessor,
    access_token: str,
    owner: str,
    repo: str,
):
    client = Github(access_token)
    project = Project(
        source_system=SourceSystemType.GITHUB,
        owner=owner,
        name=repo,
    )

    fetch_github_issues(processor, client, project)
