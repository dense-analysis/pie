package pie

import (
	"context"
	"fmt"

	"github.com/google/go-github/v59/github"
	"github.com/sa-/slicefunk"
	"golang.org/x/oauth2"
)

func LoadGitHubProjectIssues(
	ctx context.Context,
	processor *ProjectProcessor,
	accessToken string,
	owner string,
	repo string,
) error {
	ts := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: accessToken},
	)
	tc := oauth2.NewClient(ctx, ts)
	client := github.NewClient(tc)
	project := Project{
		SourceSystem: GitHub,
		Owner:        owner,
		Name:         repo,
	}

	// Fetch issues
	if err := fetchGitHubIssues(ctx, processor, client, project); err != nil {
		return fmt.Errorf("Error fetching issues: %w", err)
	}

	return nil
}

func getGitHubIssueAssigneee(gitHubIssue *github.Issue) string {
	if gitHubIssue.Assignee != nil {
		return *gitHubIssue.Assignee.Login
	}

	return ""
}

// fetchGitHubIssues retrieves issues with as much detail as possible.
func fetchGitHubIssues(
	ctx context.Context,
	processor *ProjectProcessor,
	client *github.Client,
	project Project,
) error {
	opts := &github.IssueListByRepoOptions{
		State:       "all",
		ListOptions: github.ListOptions{PerPage: 100},
	}

	for {
		issues, resp, err := client.Issues.ListByRepo(ctx, project.Owner, project.Name, opts)

		if err != nil {
			return err
		}

		for _, gitHubIssue := range issues {
			if err := processor.StoreIssue(Issue{
				Project:          project,
				ID:               *gitHubIssue.ID,
				ParentID:         0,
				AssigneeUsername: getGitHubIssueAssigneee(gitHubIssue),
				Title:            gitHubIssue.GetTitle(),
				Description:      gitHubIssue.GetBody(),
				Labels: slicefunk.Map(gitHubIssue.Labels, func(label *github.Label) string {
					return *label.Name
				}),
				CreatedAt: gitHubIssue.CreatedAt.Time,
			}); err != nil {
				return err
			}

			if err := fetchGitHubIssueEvents(
				ctx,
				processor,
				client,
				project,
				gitHubIssue,
			); err != nil {
				return fmt.Errorf("Error fetching issue events: %w", err)
			}

			if err := fetchGitHubIssueComments(
				ctx,
				processor,
				client,
				project,
				gitHubIssue,
			); err != nil {
				return fmt.Errorf("Error fetching issue comments: %w", err)
			}
		}

		if resp.NextPage == 0 {
			break
		}

		opts.Page = resp.NextPage
	}

	return nil
}

// fetchGitHubIssueEvents fetches events for an issue to store.
func fetchGitHubIssueEvents(
	ctx context.Context,
	processor *ProjectProcessor,
	client *github.Client,
	project Project,
	gitHubIssue *github.Issue,
) error {
	// Store a created event for the issue.
	if err := processor.StoreIssueEvent(IssueEvent{
		Project:          project,
		ID:               *gitHubIssue.ID,
		ParentID:         0,
		Type:             IssueEventCreated,
		AssigneeUsername: getGitHubIssueAssigneee(gitHubIssue),
		Timestamp:        gitHubIssue.CreatedAt.Time,
	}); err != nil {
		return err
	}

	if gitHubIssue.ClosedAt != nil {
		// Store a closed event for the issue.
		if err := processor.StoreIssueEvent(IssueEvent{
			Project:          project,
			ID:               *gitHubIssue.ID,
			ParentID:         0,
			Type:             IssueEventClosed,
			AssigneeUsername: getGitHubIssueAssigneee(gitHubIssue),
			Timestamp:        gitHubIssue.ClosedAt.Time,
		}); err != nil {
			return err
		}
	}

	return nil
}

// fetchGitHubIssueComments retrieves all comments for a given issue.
func fetchGitHubIssueComments(
	ctx context.Context,
	processor *ProjectProcessor,
	client *github.Client,
	project Project,
	gitHubIssue *github.Issue,
) error {
	opts := &github.IssueListCommentsOptions{
		ListOptions: github.ListOptions{PerPage: 100},
	}

	for {
		comments, resp, err := client.Issues.ListComments(ctx, project.Owner, project.Name, *gitHubIssue.Number, opts)

		if err != nil {
			return err
		}

		for _, comment := range comments {
			if err := processor.StoreIssueComment(IssueComment{
				Project:   project,
				ID:        *comment.ID,
				Username:  *comment.User.Login,
				Body:      *comment.Body,
				CreatedAt: comment.CreatedAt.Time,
			}); err != nil {
				return err
			}

			if err := processor.StoreIssueEvent(IssueEvent{
				Project:          project,
				ID:               *gitHubIssue.ID,
				ParentID:         0,
				Type:             IssueEventCommentAdded,
				AssigneeUsername: getGitHubIssueAssigneee(gitHubIssue),
				Timestamp:        comment.CreatedAt.Time,
			}); err != nil {
				return err
			}
		}

		if resp.NextPage == 0 {
			break
		}
		opts.Page = resp.NextPage
	}

	return nil
}
