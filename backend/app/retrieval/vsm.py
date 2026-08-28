

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log, sqrt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Chunk,
    LexicalPosting,
    LexicalTerm,
)
from app.retrieval.tokenizer import tokenize


class VSMSearchError(Exception):
    pass


@dataclass(slots=True)
class VSMSearchResult:
    chunk_id: int
    document_id: int
    chunk_index: int
    score: float
    chunk_text: str


@dataclass(slots=True)
class VSMSearchDiagnostics:
    total_chunks: int
    query_term_count: int
    selected_term_count: int
    exact_candidate_count: int
    candidate_count: int
    index_elimination_enabled: bool
    selected_terms: tuple[str, ...]


def calculate_idf(
    total_chunks: int,
    document_frequency: int,
) -> float:
    return log(
        (total_chunks + 1)
        / (document_frequency + 1)
    ) + 1.0


def select_high_idf_terms(
    query_terms: list[LexicalTerm],
    query_idf: dict[int, float],
) -> list[LexicalTerm]:
    """
    Select high-IDF query terms for Index Elimination.

    Terms with IDF greater than or equal to the
    average query-term IDF are preferred.

    If every query term has an equal IDF, only
    the highest-ranked half is kept so that the
    optimization still has a meaningful candidate
    generation stage.
    """

    if len(query_terms) <= 1:
        return query_terms

    average_idf = (
        sum(
            query_idf[term.id]
            for term in query_terms
        )
        / len(query_terms)
    )

    selected_terms = [
        term
        for term in query_terms
        if query_idf[term.id]
        >= average_idf
    ]

    sorted_terms = sorted(
        query_terms,
        key=lambda term: (
            query_idf[term.id],
            term.term,
        ),
        reverse=True,
    )

    if not selected_terms:
        return [
            sorted_terms[0]
        ]

    if (
        len(selected_terms)
        == len(query_terms)
    ):
        keep_count = max(
            1,
            len(query_terms) // 2,
        )

        selected_terms = (
            sorted_terms[:keep_count]
        )

    return selected_terms


def _search_vsm(
    db: Session,
    query: str,
    limit: int,
    use_index_elimination: bool,
) -> tuple[
    list[VSMSearchResult],
    VSMSearchDiagnostics,
]:
    if limit <= 0:
        raise VSMSearchError(
            "Search limit must be greater than zero."
        )

    query_tokens = tokenize(
        query
    )

    if not query_tokens:
        return (
            [],
            VSMSearchDiagnostics(
                total_chunks=0,
                query_term_count=0,
                selected_term_count=0,
                exact_candidate_count=0,
                candidate_count=0,
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=(),
            ),
        )

    query_tf = Counter(
        query_tokens
    )

    # Count chunks that actually have
    # lexical postings.
    total_chunks = db.scalar(
        select(
            func.count(
                func.distinct(
                    LexicalPosting.chunk_id
                )
            )
        )
    ) or 0

    if total_chunks == 0:
        return (
            [],
            VSMSearchDiagnostics(
                total_chunks=0,
                query_term_count=0,
                selected_term_count=0,
                exact_candidate_count=0,
                candidate_count=0,
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=(),
            ),
        )

    # Query vocabulary terms that exist
    # in the lexical index.
    query_terms = db.scalars(
        select(
            LexicalTerm
        ).where(
            LexicalTerm.term.in_(
                list(
                    query_tf.keys()
                )
            )
        )
    ).all()

    if not query_terms:
        return ([],
            VSMSearchDiagnostics(
                total_chunks=total_chunks,
                query_term_count=0,
                selected_term_count=0,
                exact_candidate_count=0,
                candidate_count=0,
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=(),
            ),
        )

    query_term_ids = [
        term.id
        for term in query_terms
    ]

    # Document frequency for each
    # query term.
    query_df_rows = db.execute(
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

    query_df = {
        term_id: int(df)
        for term_id, df
        in query_df_rows
    }

    query_weights: dict[
        int,
        float,
    ] = {}

    query_idf: dict[
        int,
        float,
    ] = {}

    for term in query_terms:
        idf = calculate_idf(
            total_chunks=total_chunks,
            document_frequency=(
                query_df.get(
                    term.id,
                    0,
                )
            ),
        )

        query_idf[
            term.id
        ] = idf

        query_weights[
            term.id
        ] = (
            query_tf[
                term.term
            ]
            * idf
        )

    query_norm = sqrt(
        sum(
            weight ** 2
            for weight
            in query_weights.values()
        )
    )

    if query_norm == 0:
        return (
            [],
            VSMSearchDiagnostics(
                total_chunks=total_chunks,
                query_term_count=(
                    len(query_terms)
                ),
                selected_term_count=0,
                exact_candidate_count=0,
                candidate_count=0,
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=(),
            ),
        )

    # First retrieve postings for ALL
    # query terms.
    #
    # This represents the exact VSM
    # candidate set and lets us measure
    # how much Index Elimination reduces
    # the candidate space.
    exact_matching_postings = (
        db.execute(
            select(
                LexicalPosting.chunk_id,
                LexicalPosting.term_id,
                LexicalPosting.term_frequency,
            ).where(
                LexicalPosting.term_id.in_(
                    query_term_ids
                )
            )
        )
        .all()
    )

    if not exact_matching_postings:
        return (
            [],
            VSMSearchDiagnostics(
                total_chunks=total_chunks,
                query_term_count=(
                    len(query_terms)
                ),
                selected_term_count=0,
                exact_candidate_count=0,
                candidate_count=0,
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=(),
            ),
        )

    exact_candidate_chunk_ids = {
        chunk_id
        for (
            chunk_id,
            _,
            _,
        ) in exact_matching_postings
    }

    # -------------------------------------------------
    # INEXACT TOP-K OPTIMIZATION:
    # INDEX ELIMINATION
    # -------------------------------------------------
    #
    # Instead of generating candidates using
    # every query term, use only the terms with
    # high IDF.
    #
    # Rare/informative query terms therefore
    # determine the candidate set.
    #
    # Once candidates are selected, normal
    # cosine TF-IDF scoring still uses ALL
    # query terms found inside those candidates.
    # -------------------------------------------------

    if use_index_elimination:
        selected_query_terms =(
            select_high_idf_terms(
                query_terms=(
                    list(
                        query_terms
                    )
                ),
                query_idf=query_idf,
            )
        )
    else:
        selected_query_terms = (
            list(
                query_terms
            )
        )

    selected_term_ids = {
        term.id
        for term
        in selected_query_terms
    }

    candidate_chunk_ids = {
        chunk_id
        for (
            chunk_id,
            term_id,
            _,
        ) in exact_matching_postings
        if (
            not use_index_elimination
            or term_id
            in selected_term_ids
        )
    }

    # Defensive fallback.
    #
    # Index Elimination should never
    # make a valid query completely
    # unsearchable.
    if not candidate_chunk_ids:
        candidate_chunk_ids = (
            exact_candidate_chunk_ids
        )

    # We now use all query terms for
    # the selected candidate chunks.
    matching_postings = [
        (
            chunk_id,
            term_id,
            term_frequency,
        )
        for (
            chunk_id,
            term_id,
            term_frequency,
        ) in exact_matching_postings
        if chunk_id
        in candidate_chunk_ids
    ]

    # Dot product between the query
    # vector and candidate chunks.
    dot_products: dict[
        int,
        float,
    ] = defaultdict(
        float
    )

    for (
        chunk_id,
        term_id,
        term_frequency,
    ) in matching_postings:
        chunk_weight = (
            term_frequency
            * query_idf[
                term_id
            ]
        )

        dot_products[
            chunk_id
        ] += (
            chunk_weight
            * query_weights[
                term_id
            ]
        )

    # Load every lexical term belonging
    # to candidate chunks because cosine
    # similarity needs the complete chunk
    # vector norm.
    all_postings = db.execute(
        select(
            LexicalPosting.chunk_id,
            LexicalPosting.term_id,
            LexicalPosting.term_frequency,
        ).where(
            LexicalPosting.chunk_id.in_(
                candidate_chunk_ids
            )
        )
    ).all()

    all_term_ids = {
        term_id
        for (
            _,
            term_id,
            _,
        ) in all_postings
    }

    if not all_term_ids:
        return (
            [],
            VSMSearchDiagnostics(
                total_chunks=total_chunks,
                query_term_count=(
                    len(query_terms)
                ),
                selected_term_count=(
                    len(
                        selected_query_terms
                    )
                ),
                exact_candidate_count=(
                    len(
                        exact_candidate_chunk_ids
                    )
                ),
                candidate_count=(
                    len(
                        candidate_chunk_ids
                    )
                ),
                index_elimination_enabled=(
                    use_index_elimination
                ),
                selected_terms=tuple(
                    term.term
                    for term
                    in selected_query_terms
                ),
            ),
        )

    all_df_rows = db.execute(
        select(
            LexicalPosting.term_id,
            func.count(
                LexicalPosting.id
            ),
        )
        .where(
            LexicalPosting.term_id.in_(
                all_term_ids
            )
        )
        .group_by(
            LexicalPosting.term_id
        )
    ).all()

    all_df = {
        term_id: int(df)
        for term_id, df
        in all_df_rows
    }

    chunk_norm_squared: dict[
        int,
        float,
    ] = defaultdict(
        float
    )

    for (
        chunk_id,
        term_id,
        term_frequency,
    ) in all_postings:
        idf = calculate_idf(
            total_chunks=total_chunks,
            document_frequency=(
                all_df[
                    term_id
                ]
            ),
        )

        weight = (
            term_frequency
            * idf
        )

        chunk_norm_squared[
            chunk_id
        ] += (
            weight ** 2
        )

    chunks = db.scalars(
        select(
            Chunk
        ).where(
            Chunk.id.in_(
                candidate_chunk_ids
            )
        )
    ).all()

    chunk_by_id = {
        chunk.id: chunk
        for chunk in chunks
    }

    results: list[
        VSMSearchResult
    ] = []

    for chunk_id in (
        candidate_chunk_ids
    ):
        chunk_norm = sqrt(
            chunk_norm_squared[
                chunk_id
            ]
        )

        if chunk_norm == 0:
            continue

        score = (
            dot_products[
                chunk_id
            ]
            / (
                query_norm
                * chunk_norm
            )
        )

        chunk = (
            chunk_by_id.get(
                chunk_id
            )
        )

        if chunk is None:
            continue

        results.append(
            VSMSearchResult(
                chunk_id=chunk.id,
                document_id=(
                    chunk.document_id
                ),
                chunk_index=(
                    chunk.chunk_index
                ),
                score=score,
                chunk_text=(
                    chunk.chunk_text
                ),
            )
        )

    results.sort(
        key=lambda result:
            result.score,
        reverse=True,
    )

    diagnostics = (
        VSMSearchDiagnostics(
            total_chunks=total_chunks,
            query_term_count=(
                len(query_terms)
            ),
            selected_term_count=(
                len(
                    selected_query_terms
                )
            ),
            exact_candidate_count=(
                len(
                    exact_candidate_chunk_ids
                )
            ),
            candidate_count=(
                len(
                    candidate_chunk_ids
                )
            ),
            index_elimination_enabled=(
                use_index_elimination
            ),
            selected_terms=tuple(
                term.term
                for term
                in selected_query_terms
            ),
        )
    )

    return (
        results[:limit],
        diagnostics,
    )


def search_vsm(
    db: Session,
    query: str,
    limit: int = 10,
    use_index_elimination: bool = True,
) -> list[VSMSearchResult]:
    results, _ = _search_vsm(
        db=db,
        query=query,
        limit=limit,
        use_index_elimination=(
            use_index_elimination
        ),
    )

    return results


def search_vsm_with_diagnostics(
    db: Session,
    query: str,
    limit: int = 10,
    use_index_elimination: bool = True,
) -> tuple[
    list[VSMSearchResult],
    VSMSearchDiagnostics,
]:
    return _search_vsm(
        db=db,
        query=query,
        limit=limit,
        use_index_elimination=(
            use_index_elimination
        ),
    )