
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk
from app.services.embedding_service import embed_text


class SemanticSearchError(Exception):
    pass


@dataclass(slots=True)
class SemanticSearchResult:
    chunk_id: int
    document_id: int
    chunk_index: int
    score: float
    chunk_text: str


def search_semantic(
    db: Session,
    query: str,
    limit: int = 10,
) -> list[SemanticSearchResult]:
    try:
        query_embedding = embed_text(query)

        distance = Chunk.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        statement = (
            select(
                Chunk,
                distance,
            )
            .where(
                Chunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )

        rows = db.execute(statement).all()

        results: list[SemanticSearchResult] = []

        for chunk, cosine_distance in rows:
            score = 1.0 - float(cosine_distance)

            results.append(
                SemanticSearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    score=score,
                    chunk_text=chunk.chunk_text,
                )
            )

        return results

    except Exception as exc:
        raise SemanticSearchError(
            "Semantic search failed."
        ) from exc