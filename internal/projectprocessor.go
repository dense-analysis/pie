package pie

// ProjectProcessor is a processor for loading issue data into Storage.
type ProjectProcessor struct {
	Issues        []Issue
	IssueComments []IssueComment
	IssueEvents   []IssueEvent
}

func (p *ProjectProcessor) StoreIssue(issue Issue) error {
	p.Issues = append(p.Issues, issue)

	return nil
}

func (p *ProjectProcessor) StoreIssueComment(issueComment IssueComment) error {
	p.IssueComments = append(p.IssueComments, issueComment)

	return nil
}

func (p *ProjectProcessor) StoreIssueEvent(issueEvent IssueEvent) error {
	p.IssueEvents = append(p.IssueEvents, issueEvent)

	return nil
}
