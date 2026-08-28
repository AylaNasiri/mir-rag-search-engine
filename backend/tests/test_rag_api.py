
import pytest
from fastapi.testclient import TestClient

from app.api.routes import rag as rag_route
from app.db.database import get_db
from app.main import app
from app.services.rag_service import (
    RAGResult,
    RAGServiceError,
    RAGSource,
)


def override_get_db():
    yield object()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_rag_ask_success(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_result = RAGResult(
        query="What is semantic search?",
        answer=(
            "Semantic search retrieves information "
            "based on meaning."
        ),
        sources=[
            RAGSource(
                chunk_id=3,
                document_id=3,
                document_title="01_semantic_search_rag",
                filename="01_semantic_search_rag.pdf",
                chunk_index=0,
                score=0.032786,
            )
        ],
    )

    monkeypatch.setattr(
        rag_route,
        "answer_question",
        lambda db, query, limit: fake_result,
    )

    response = client.post(
        "/api/v1/rag/ask",
        json={
            "query": "What is semantic search?",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == (
        "What is semantic search?"
    )

    assert data["answer"] == (
        "Semantic search retrieves information "
        "based on meaning."
    )

    assert len(data["sources"]) == 1

    source = data["sources"][0]

    assert source["chunk_id"] == 3
    assert source["document_id"] == 3
    assert source["document_title"] == (
        "01_semantic_search_rag"
    )
    assert source["filename"] == (
        "01_semantic_search_rag.pdf"
    )
    assert source["chunk_index"] == 0


def test_rag_ask_blank_query(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/rag/ask",
        json={
            "query": "   ",
            "limit": 3,
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Question cannot be empty."
    )


def test_rag_ask_invalid_limit(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/rag/ask",
        json={
            "query": "What is semantic search?",
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_rag_ask_service_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_service_error(
        db,
        query,
        limit,
    ):
        raise RAGServiceError(
            "Test failure"
        )

    monkeypatch.setattr(
        rag_route,
        "answer_question",
        raise_service_error,
    )

    response = client.post(
        "/api/v1/rag/ask",
        json={
            "query": "What is semantic search?",
            "limit": 3,
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Failed to generate RAG answer."
    )