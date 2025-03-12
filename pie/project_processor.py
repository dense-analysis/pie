import logging

import nltk
import numpy
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

from .clickhouse import (get_client, insert_issue, insert_issue_comment,
                         insert_issue_event, issue_comment_exists,
                         issue_exists)
from .issue import Issue, IssueComment, IssueEvent

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

EMPTY_VECTOR = [0.0] * 768


class ProjectProcessor:
    def __init__(
        self,
        clickhouse_host: str,
        clickhouse_port: int,
        clickhouse_username: str,
        clickhouse_password: str,
        clickhouse_database: str,
    ):
        # Set up nltk
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)

        # Load pre-trained BERT model
        self.model = SentenceTransformer("all-mpnet-base-v2")

        self.clickhouse_client = get_client(
            host=clickhouse_host,
            port=clickhouse_port,
            username=clickhouse_username,
            password=clickhouse_password,
            database=clickhouse_database,
        )

    def store_issue(self, issue: Issue) -> bool:
        """
        Store an issue in the database.

        Return ``True`` if the issue is stored, and ``False`` if it already
        exists.
        """
        if not issue_exists(
            self.clickhouse_client,
            issue.project,
            issue.id,
        ):
            logging.info("Adding issue: %d", issue.id)

            title_tensor = self.model.encode(
                issue.title,
                show_progress_bar=False,
            )
            title_vector: list[float] = title_tensor.tolist()

            if issue.description.strip():
                description_tensor = numpy.mean(
                    self.model.encode(
                        sent_tokenize(issue.description),
                        show_progress_bar=False,
                    ),
                    axis=0,
                )
                description_vector: list[float] = description_tensor.tolist()
            else:
                description_vector = EMPTY_VECTOR

            insert_issue(
                self.clickhouse_client,
                issue,
                title_vector,
                description_vector,
            )

            return True

        return False

    def store_issue_comment(self, issue_comment: IssueComment) -> bool:
        """
        Store an issue comment in the database.

        Return ``True`` if the comment is stored, and ``False`` if it already
        exists.
        """
        if not issue_comment_exists(
            self.clickhouse_client,
            issue_comment.project,
            issue_comment.issue_id,
            issue_comment.id,
        ):
            logging.info("Adding issue comment: %d", issue_comment.id)

            body_tensor = numpy.mean(
                self.model.encode(
                    sent_tokenize(issue_comment.body),
                    show_progress_bar=False,
                ),
                axis=0,
            )
            body_vector: list[float] = body_tensor.tolist()

            insert_issue_comment(
                self.clickhouse_client,
                issue_comment,
                body_vector,
            )

            return True

        return False

    def store_issue_event(self, issue_event: IssueEvent) -> None:
        logging.info(
            "Adding issue event: (%d, %s)",
            issue_event.id,
            issue_event.type.name,
        )

        insert_issue_event(
            self.clickhouse_client,
            issue_event,
        )
