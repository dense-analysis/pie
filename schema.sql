CREATE TABLE issues (
    source_system Enum8('GITHUB' = 0, 'JIRA' = 1),
    project_owner LowCardinality(String),
    project_name LowCardinality(String),
    id UInt64,
    parent_id UInt64,
    assignee_username LowCardinality(String),
    title String,
    title_vector Array(Float32),
    description String,
    description_vector Array(Float32),
    labels Array(String),
    created_at DateTime64
)
ENGINE = MergeTree()
ORDER BY (source_system, project_owner, project_name, id)
PARTITION BY source_system;

CREATE TABLE issue_comments (
    source_system Enum8('GITHUB' = 0, 'JIRA' = 1),
    project_owner LowCardinality(String),
    project_name LowCardinality(String),
    issue_id UInt64,
    id UInt64,
    username LowCardinality(String),
    body String,
    body_vector Array(Float32),
    created_at DateTime64
)
ENGINE = MergeTree()
ORDER BY (source_system, project_owner, project_name, issue_id, id)
PARTITION BY source_system;

CREATE TABLE issue_events (
    source_system Enum8('GITHUB' = 0, 'JIRA' = 1),
    project_owner LowCardinality(String),
    project_name LowCardinality(String),
    id UInt64,
    parent_id UInt64,
    type Enum8(
        'CREATED' = 0,
        'UPDATED' = 1,
        'CLOSED' = 2,
        'COMMENT_ADDED' = 3,
        'REOPENED' = 4,
        'ASSIGNED' = 5,
        'RESOLVED' = 6
    ),
    assignee_username LowCardinality(String),
    timestamp DateTime64
)
ENGINE = MergeTree();
ORDER BY (source_system, project_owner, project_name, id, timestamp)
PARTITION BY source_system;
