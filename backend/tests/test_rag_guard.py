
from types import SimpleNamespace

import pytest

from app.services import rag_guard_service


def test_relevant_query_returns_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_guard_service,
        "search_semantic",
        lambda db, query, limit: [
            SimpleNamespace(score=0.5968)
        ],
    )

    monkeypatch.setattr(
        rag_guard_service,
        "get_min_semantic_score",
        lambda: 0.25,
    )

    result = rag_guard_service.is_query_relevant(
        db=object(),
        query="What is semantic search?",
    )

    assert result is True


def test_irrelevant_query_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_guard_service,
        "search_semantic",
        lambda db, query, limit: [
            SimpleNamespace(score=0.1007)
        ],
    )

    monkeypatch.setattr(
        rag_guard_service,
        "get_min_semantic_score",
        lambda: 0.25,
    )

    result = rag_guard_service.is_query_relevant(
        db=object(),
        query="What is the capital of Japan?",
    )

    assert result is False


def test_no_semantic_results_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        rag_guard_service,
        "search_semantic",
        lambda db, query, limit: [],
    )

    result = rag_guard_service.is_query_relevant(
        db=object(),
        query="Completely unrelated question",
    )

    assert result is False


def test_threshold_can_be_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "RAG_MIN_SEMANTIC_SCORE",
        "0.40",
    )

    assert (
        rag_guard_service.get_min_semantic_score()
        == 0.40
    )


def test_invalid_threshold_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "RAG_MIN_SEMANTIC_SCORE",
        "invalid",
    )

    with pytest.raises(
        rag_guard_service.RAGGuardError
    ):
        rag_guard_service.get_min_semantic_score()