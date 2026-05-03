from pie.project_processor import (
    EMPTY_VECTOR,
    VECTOR_SIZE,
    encode_document,
    encode_text,
)


def test_encode_text_is_deterministic() -> None:
    assert encode_text("same text") == encode_text("same text")


def test_encode_document_returns_empty_vector_for_blank_text() -> None:
    assert encode_document("   ") == EMPTY_VECTOR


def test_encode_document_returns_expected_vector_size() -> None:
    assert (
        len(
            encode_document("One sentence. Another sentence."),
        )
        == VECTOR_SIZE
    )
