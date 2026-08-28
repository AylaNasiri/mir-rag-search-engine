
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.retrieval.bm25 import search_bm25
from app.retrieval.semantic import search_semantic


class HybridSearchError(Exception):
    pass


@dataclass(slots=True)
class HybridSearchResult:
    chunk_id: int
    document_id: int
    chunk_index: int
    score: float
    chunk_text: str


def search_hybrid(
    db: Session,
    query: str,
    limit: int = 10,
) -> list[HybridSearchResult]:
    try:
        candidate_limit = max(
            limit * 3,
            20,
        )

        bm25_results = search_bm25(
            db=db,
            query=query,
            limit=candidate_limit,
        )

        semantic_results = search_semantic(
            db=db,
            query=query,
            limit=candidate_limit,
        )

        rrf_k = 60

        scores: dict[int, float] = {}
        results_by_chunk: dict[int, object] = {}

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):
            scores[result.chunk_id] = (
                scores.get(result.chunk_id, 0.0)
                + 1.0 / (rrf_k + rank)
            )

            results_by_chunk[result.chunk_id] = result

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            scores[result.chunk_id] = (
                scores.get(result.chunk_id, 0.0)
                + 1.0 / (rrf_k + rank)
            )

            results_by_chunk[result.chunk_id] = result

        ranked_chunk_ids = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )[:limit]

        results: list[HybridSearchResult] = []

        for chunk_id in ranked_chunk_ids:
            result = results_by_chunk[chunk_id]

            results.append(
                HybridSearchResult(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    chunk_index=result.chunk_index,
                    score=scores[chunk_id],
                    chunk_text=result.chunk_text,
                )
            )

        return results

    except Exception as exc:
        raise HybridSearchError(
            "Hybrid search failed."
        ) from exc