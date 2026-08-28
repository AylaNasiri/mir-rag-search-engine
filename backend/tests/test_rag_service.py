
import pytest

from app.services import rag_service


def test_irrelevant_query_stops_before_rag_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_service,
        "is_query_relevant",
        lambda db, query: False,
    )

    def should_not_be_called(*args, **kwargs):
        raise AssertionError(
            "RAG pipeline should not run "
            "for an irrelevant query."
        )

    monkeypatch.setattr(
        rag_service,
        "build_rag_context",
        should_not_be_called,
    )

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        should_not_be_called,
    )

    result = rag_service.answer_question(
        db=object(),
        query="What is the capital of Japan?",
        limit=3,
    )

    assert result.query == (
        "What is the capital of Japan?"
    )

    assert result.answer == (
        "I could not find enough information "
        "in the provided documents."
    )

    assert result.sources == []