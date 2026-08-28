
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.retrieval.hybrid import (
    HybridSearchResult,
    search_hybrid,
)


class RAGContextError(Exception):
    pass


@dataclass(slots=True)
class RAGContext:
    query: str
    context: str
    results: list[HybridSearchResult]


def build_rag_context(
    db: Session,
    query: str,
    limit: int = 4,
    max_characters: int = 8000,
) -> RAGContext:
    try:
        search_results = search_hybrid(
            db=db,
            query=query,
            limit=limit,
        )

        context_parts: list[str] = []
        current_length = 0
        included_results: list[HybridSearchResult] = []

        for rank, result in enumerate(
            search_results,
            start=1,
        ):
            section = (
                f"[Source {rank}]\n"
                f"Document ID: {result.document_id}\n"
                f"Chunk ID: {result.chunk_id}\n"
                f"Chunk Index: {result.chunk_index}\n"
                f"Text:\n{result.chunk_text}\n"
            )

            if (
                current_length + len(section)
                > max_characters
            ):
                break

            context_parts.append(section)
            included_results.append(result)

            current_length += len(section)

        context = "\n".join(context_parts)

        return RAGContext(
            query=query,
            context=context,
            results=included_results,
        )

    except Exception as exc:
        raise RAGContextError(
            "Failed to build RAG context."
        ) from exc