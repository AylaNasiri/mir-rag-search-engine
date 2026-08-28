
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document
from app.services.generation_service import (
    GenerationError,
    generate_answer,
)
from app.services.rag_context_service import (
    RAGContextError,
    build_rag_context,
)
from app.services.rag_guard_service import (
    RAGGuardError,
    is_query_relevant,
)
from app.services.rag_prompt_service import (
    build_rag_prompt,
)


class RAGServiceError(Exception):
    pass


@dataclass(slots=True)
class RAGSource:
    chunk_id: int
    document_id: int
    document_title: str
    filename: str
    chunk_index: int
    score: float


@dataclass(slots=True)
class RAGResult:
    query: str
    answer: str
    sources: list[RAGSource]


def answer_question(
    db: Session,
    query: str,
    limit: int = 4,
) -> RAGResult:
    try:
        # 1. Reject questions that are not sufficiently
        # related to the indexed document corpus.
        relevant = is_query_relevant(
            db=db,
            query=query,
        )

        if not relevant:
            return RAGResult(
                query=query,
                answer=(
                    "I could not find enough information "
                    "in the provided documents."
                ),
                sources=[],
            )

        # 2. Retrieve relevant chunks using hybrid search
        rag_context = build_rag_context(
            db=db,
            query=query,
            limit=limit,
        )

        if not rag_context.results:
            return RAGResult(
                query=query,
                answer=(
                    "I could not find enough information "
                    "in the provided documents."
                ),
                sources=[],
            )

        # 3. Build grounded RAG prompt
        prompt = build_rag_prompt(
            query=query,
            context=rag_context.context,
        )

        # 4. Generate answer
        answer = generate_answer(
            prompt=prompt,
        )

        # 5. Collect document metadata
        document_ids = {
            result.document_id
            for result in rag_context.results
        }

        documents = db.scalars(
            select(Document).where(
                Document.id.in_(document_ids)
            )
        ).all()

        documents_by_id = {
            document.id: document
            for document in documents
        }

        # 6. Build enriched source list
        sources: list[RAGSource] = []

        for result in rag_context.results:
            document = documents_by_id.get(
                result.document_id
            )

            if document is None:
                continue

            sources.append(
                RAGSource(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    document_title=document.title,
                    filename=document.filename,
                    chunk_index=result.chunk_index,
                    score=result.score,
                )
            )

        return RAGResult(
            query=query,
            answer=answer,
            sources=sources,
        )

    except (
        RAGGuardError,
        RAGContextError,
        GenerationError,
    ) as exc:
        raise RAGServiceError(
            "Failed to answer question."
        ) from exc