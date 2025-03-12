from .issue import Issue, IssueComment, IssueEvent


class ProjectProcessor:
    def __init__(self):
        self.issues: list[Issue] = []
        self.issue_comments: list[IssueComment] = []
        self.issue_events: list[IssueEvent] = []

    def store_issue(self, issue: Issue) -> None:
        self.issues.append(issue)

    def store_issue_comment(self, issue_comment: IssueComment) -> None:
        self.issue_comments.append(issue_comment)

    def store_issue_event(self, issue_event: IssueEvent) -> None:
        self.issue_events.append(issue_event)
