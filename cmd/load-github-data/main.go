package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/BurntSushi/toml"
	pie "github.com/dense-analysis/pie/internal"
)

// Repo struct to hold the repo name and two strings
type ConfigGitHubRepo struct {
	Owner string
	Name  string
}

// Config struct to hold the toml file data
type Config struct {
	GitHubToken string             `toml:"github_token"`
	GitHubRepos []ConfigGitHubRepo `toml:"github_repos"`
}

func main() {
	data, err := os.ReadFile("config.toml")

	if err != nil {
		log.Fatal(err)
	}

	var config Config

	if _, err := toml.Decode(string(data), &config); err != nil {
		log.Fatal(err)
	}

	if err != nil {
		log.Fatal("Error loading .env file")
	}

	if len(config.GitHubToken) == 0 {
		log.Fatal("Error loading GitHubToken")
	}

	var processor pie.ProjectProcessor

	ctx := context.Background()

	for _, repo := range config.GitHubRepos {
		pie.LoadGitHubProjectIssues(
			ctx,
			&processor,
			config.GitHubToken,
			repo.Owner,
			repo.Name,
		)
	}

	for _, issue := range processor.Issues {
		fmt.Printf("Issue: %v\n", issue)
	}

	for _, comment := range processor.IssueComments {
		fmt.Printf("comment: %v\n", comment)
	}

	for _, event := range processor.IssueEvents {
		fmt.Printf("event: %v\n", event)
	}
}
