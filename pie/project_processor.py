import hashlib
import logging
import math
import re

from .clickhouse import (
    get_client,
    insert_issue,
    insert_issue_comment,
    insert_issue_event,
    issue_comment_exists,
    issue_event_exists,
    issue_exists,
)
from .issue import Issue, IssueComment, IssueEvent

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

VECTOR_SIZE = 768
EMPTY_VECTOR = [0.0] * VECTOR_SIZE


def _split_sentences(text: str) -> list[str]:
    return [
        sentence
        for sentence in re.split(r"[.!?]+\s+", text.strip())
        if sentence
    ]


def _normalise_vector(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if math.isclose(magnitude, 0.0, abs_tol=1e-12):
        return EMPTY_VECTOR.copy()

    return [value / magnitude for value in vector]


def encode_text(text: str) -> list[float]:
    # Python 3.15 alpha lacks wheels for the previous ML stack, so use a
    # deterministic hashed token vector to keep similarity scoring working.
    vector = [0.0] * VECTOR_SIZE

    for token in re.findall(r"[A-Za-z0-9_']+", text.lower()):
        token_hash = hashlib.blake2b(
            token.encode("utf-8"),
            digest_size=8,
        ).digest()
        index = int.from_bytes(token_hash[:4], "big") % VECTOR_SIZE
        direction = 1.0 if token_hash[4] % 2 == 0 else -1.0
        vector[index] += direction

    return _normalise_vector(vector)


def encode_document(text: str) -> list[float]:
    sentences = _split_sentences(text)
    if not sentences:
        return EMPTY_VECTOR.copy()

    sentence_vectors = [encode_text(sentence) for sentence in sentences]
    combined_vector = [0.0] * VECTOR_SIZE

    for sentence_vector in sentence_vectors:
        for index, value in enumerate(sentence_vector):
            combined_vector[index] += value

    return _normalise_vector(combined_vector)


class ProjectProcessor:
    def __init__(
        self,
        clickhouse_host: str,
        clickhouse_port: int,
        clickhouse_username: str,
        clickhouse_password: str,
        clickhouse_database: str,
    ) -> None:
        self.clickhouse_client = get_client(
            host=clickhouse_host,
            port=clickhouse_port,
            username=clickhouse_username,
            password=clickhouse_password,
            database=clickhouse_database,
        )

    def store_issue(self, issue: Issue) -> None:
        """
        Store an issue in the database.
        """
        if not issue_exists(
            self.clickhouse_client,
            issue.project,
            issue.id,
        ):
            logging.info("Adding issue: %d", issue.id)

            title_vector = encode_text(issue.title)

            if issue.description.strip():
                description_vector = encode_document(issue.description)
            else:
                description_vector = EMPTY_VECTOR.copy()

            insert_issue(
                self.clickhouse_client,
                issue,
                title_vector,
                description_vector,
            )

    def store_issue_comment(self, issue_comment: IssueComment) -> None:
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

            body_vector = encode_document(issue_comment.body)

            insert_issue_comment(
                self.clickhouse_client,
                issue_comment,
                body_vector,
            )

    def store_issue_event(self, issue_event: IssueEvent) -> None:
        if not issue_event_exists(
            self.clickhouse_client,
            issue_event.project,
            issue_event.id,
            issue_event.related_object_id,
        ):
            logging.info(
                "Adding issue event: (%d, %s, %d)",
                issue_event.id,
                issue_event.type.name,
                issue_event.related_object_id,
            )

            insert_issue_event(
                self.clickhouse_client,
                issue_event,
            )
