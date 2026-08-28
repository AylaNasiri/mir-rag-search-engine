from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Chunk, LexicalPosting, LexicalTerm
from app.retrieval.tokenizer import tokenize


class BM25SearchError(Exception):
    pass


@dataclass(slots=True)
class BM25SearchResult:
    chunk_id: int
    document_id: int
    chunk_index: int
    score: float
    chunk_text: str


def calculate_bm25_idf(
    total_chunks: int,
    document_frequency: int,
) -> float:
    return log(
        1
        + (
            total_chunks
            - document_frequency
            + 0.5
        )
        / (
            document_frequency
            + 0.5
        )
    )


def search_bm25(
    db: Session,
    query: str,
    limit: int = 10,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[BM25SearchResult]:

    if limit <= 0:
        raise BM25SearchError(
            "Search limit must be greater than zero."
        )

    if k1 <= 0:
        raise BM25SearchError(
            "k1 must be greater than zero."
        )

    if not 0 <= b <= 1:
        raise BM25SearchError(
            "b must be between 0 and 1."
        )

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    query_tf = Counter(query_tokens)

    indexed_chunk_ids = db.scalars(
        select(
            LexicalPosting.chunk_id
        ).distinct()
    ).all()

    if not indexed_chunk_ids:
        return []

    total_chunks = len(indexed_chunk_ids)

    average_chunk_length = db.scalar(
        select(
            func.avg(Chunk.token_count)
        ).where(
            Chunk.id.in_(
                indexed_chunk_ids
            )
        )
    )

    if not average_chunk_length:
        return []

    avgdl = float(average_chunk_length)

    query_terms = db.scalars(
        select(LexicalTerm).where(
            LexicalTerm.term.in_(
                list(query_tf.keys())
            )
        )
    ).all()

    if not query_terms:
        return []

    query_term_ids = [
        term.id
        for term in query_terms
    ]

    term_by_id = {
        term.id: term
        for term in query_terms
    }

    df_rows = db.execute(
        select(
            LexicalPosting.term_id,
            func.count(
                LexicalPosting.id
            ),
        )
        .where(
            LexicalPosting.term_id.in_(
                query_term_ids
            )
        )
        .group_by(
            LexicalPosting.term_id
        )
    ).all()

    document_frequency = {
        term_id: int(df)
        for term_id, df in df_rows
    }

    matching_postings = db.execute(
        select(
            LexicalPosting.chunk_id,
            LexicalPosting.term_id,
            LexicalPosting.term_frequency,
        ).where(
            LexicalPosting.term_id.in_(
                query_term_ids
            )
        )
    ).all()

    if not matching_postings:
        return []

    candidate_chunk_ids = {
        chunk_id
        for chunk_id, _, _ in matching_postings
    }

    chunks = db.scalars(
        select(Chunk).where(
            Chunk.id.in_(
                candidate_chunk_ids
            )
        )
    ).all()

    chunk_by_id = {
        chunk.id: chunk
        for chunk in chunks
    }

    scores: dict[int, float] = defaultdict(float)

    for (
        chunk_id,
        term_id,
        term_frequency,
    ) in matching_postings:

        chunk = chunk_by_id.get(
            chunk_id
        )

        if chunk is None:
            continue

        document_length = chunk.token_count

        df = document_frequency.get(
            term_id,
            0,
        )

        idf = calculate_bm25_idf(
            total_chunks=total_chunks,
            document_frequency=df,
        )

        denominator = (
            term_frequency
            + k1
            * (
                1
                - b
                + b
                * (
                    document_length
                    / avgdl)
            )
        )

        tf_component = (
            term_frequency
            * (k1 + 1)
        ) / denominator

        term = term_by_id[
            term_id
        ]

        query_frequency = query_tf[
            term.term
        ]

        scores[chunk_id] += (
            idf
            * tf_component
            * query_frequency
        )

    results: list[BM25SearchResult] = []

    for chunk_id, score in scores.items():

        chunk = chunk_by_id.get(
            chunk_id
        )

        if chunk is None:
            continue

        results.append(
            BM25SearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                score=score,
                chunk_text=chunk.chunk_text,
            )
        )

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results[:limit]