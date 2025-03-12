package pie

import "time"

type SourceSystemType int

const (
	GitHub SourceSystemType = iota
	Jira
)

type IssueEventType int

const (
	IssueEventCreated IssueEventType = iota
	IssueEventUpdated
	IssueEventClosed
	IssueEventCommentAdded
	IssueEventReopened
	IssueEventAssigned
	IssueEventResolved
)

type Project struct {
	// SourceSystem is the source system for a project.
	SourceSystem SourceSystemType
	// Owner is the organistion or domain for a project.
	Owner string
	// Name is the project name for a project
	Name string
}

type IssueComment struct {
	// Project is the project for the issue comment.
	Project Project
	// IssueID is the ID of the issue.
	IssueID int64
	// ID is the numberical id for the comment.
	ID int64
	// Username is the name of the user that posted the comment.
	Username string
	// Body is the body of a comment.
	Body string
	// CreatedAt is the time a comment was created.
	CreatedAt time.Time
}

type Issue struct {
	// Project is the project for the issue.
	Project Project
	// ID is the numerical id for the issue.
	ID int64
	// ParentID is the parent id for the issue, which is 0 when the issue has no parent.
	ParentID int64
	// Assignee is the username for the assignee the issue.
	AssigneeUsername string
	// Title is the title for an issue.
	Title string
	// Description is the description for an issue.
	Description string
	// Labels is an array of labels for an issue.
	Labels []string
	// CreatedAt is the time an issue was created.
	CreatedAt time.Time
}

type IssueEvent struct {
	// Project is the project for the issue.
	Project Project
	// ID is the numerical id for the issue.
	ID int64
	// ParentID is the id for the parent of an issue, which is 0 when the issue has no parent.
	ParentID int64
	// Type is the type of the IssueEvent.
	Type IssueEventType
	// Assignee is the username for the assignee for the issue.
	AssigneeUsername string
	// Timestamp is the timestamp for the issue event.
	Timestamp time.Time
}
