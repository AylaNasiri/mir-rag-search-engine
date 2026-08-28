
import os

from sqlalchemy.orm import Session

from app.retrieval.semantic import search_semantic


class RAGGuardError(Exception):
    pass


DEFAULT_MIN_SEMANTIC_SCORE = 0.25


def get_min_semantic_score() -> float:
    raw_value = os.getenv(
        "RAG_MIN_SEMANTIC_SCORE",
        str(DEFAULT_MIN_SEMANTIC_SCORE),
    )

    try:
        return float(raw_value)
    except ValueError as exc:
        raise RAGGuardError(
            "Invalid RAG_MIN_SEMANTIC_SCORE value."
        ) from exc


def is_query_relevant(
    db: Session,
    query: str,
) -> bool:
    try:
        results = search_semantic(
            db=db,
            query=query,
            limit=1,
        )
    except Exception as exc:
        raise RAGGuardError(
            "Failed to evaluate query relevance."
        ) from exc

    if not results:
        return False

    best_score = results[0].score
    minimum_score = get_min_semantic_score()

    return best_score >= minimum_score