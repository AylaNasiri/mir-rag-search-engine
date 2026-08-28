
from collections import Counter, defaultdict
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    LexicalPosting,
    LexicalTerm,
)
from app.retrieval.tokenizer import tokenize
from app.retrieval.vsm import (
    VSMSearchResult,
    calculate_idf,
    search_vsm,
)


class PRFSearchError(Exception):
    pass


@dataclass(slots=True)
class PRFSearchDiagnostics:
    applied: bool
    original_query: str
    expanded_query: str
    feedback_chunk_ids: tuple[int, ...]
    expansion_terms: tuple[str, ...]
    alpha: float
    beta: float


def search_vsm_with_prf(
    db: Session,
    query: str,
    limit: int = 10,
    feedback_k: int = 3,
    expansion_term_limit: int = 5,
    alpha: float = 1.0,
    beta: float = 0.75,
) -> tuple[
    list[VSMSearchResult],
    PRFSearchDiagnostics,
]:
    if limit <= 0:
        raise PRFSearchError(
            "Search limit must be greater than zero."
        )

    if feedback_k <= 0:
        raise PRFSearchError(
            "feedback_k must be greater than zero."
        )

    if expansion_term_limit <= 0:
        raise PRFSearchError(
            "expansion_term_limit must be greater than zero."
        )

    if alpha < 0:
        raise PRFSearchError(
            "alpha cannot be negative."
        )

    if beta < 0:
        raise PRFSearchError(
            "beta cannot be negative."
        )

    normalized_query = query.strip()

    if not normalized_query:
        return (
            [],
            PRFSearchDiagnostics(
                applied=False,
                original_query=query,
                expanded_query=query,
                feedback_chunk_ids=(),
                expansion_terms=(),
                alpha=alpha,
                beta=beta,
            ),
        )

    original_tokens = tokenize(
        normalized_query
    )

    if not original_tokens:
        return (
            [],
            PRFSearchDiagnostics(
                applied=False,
                original_query=normalized_query,
                expanded_query=normalized_query,
                feedback_chunk_ids=(),
                expansion_terms=(),
                alpha=alpha,
                beta=beta,
            ),
        )

    # -------------------------------------------------
    # FIRST RETRIEVAL
    # -------------------------------------------------
    #
    # The initial retrieval deliberately disables
    # Index Elimination.
    #
    # PRF should build its feedback set from the
    # complete VSM candidate space rather than from
    # an already reduced candidate set.
    # -------------------------------------------------

    initial_results = search_vsm(
        db=db,
        query=normalized_query,
        limit=max(
            limit,
            feedback_k,
        ),
        use_index_elimination=False,
    )

    if not initial_results:
        return (
            [],
            PRFSearchDiagnostics(
                applied=False,
                original_query=normalized_query,
                expanded_query=normalized_query,
                feedback_chunk_ids=(),
                expansion_terms=(),
                alpha=alpha,
                beta=beta,
            ),
        )

    feedback_results = (
        initial_results[:feedback_k]
    )

    feedback_chunk_ids = tuple(
        result.chunk_id
        for result in feedback_results
    )

    # Number of chunks represented in
    # the lexical index.
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
            initial_results[:limit],
            PRFSearchDiagnostics(
                applied=False,
                original_query=normalized_query,
                expanded_query=normalized_query,
                feedback_chunk_ids=(
                    feedback_chunk_ids
                ),
                expansion_terms=(),alpha=alpha,
                beta=beta,
            ),
        )

    # -------------------------------------------------
    # LOAD FEEDBACK TERMS
    # -------------------------------------------------

    feedback_postings = db.execute(
        select(
            LexicalPosting.chunk_id,
            LexicalPosting.term_id,
            LexicalPosting.term_frequency,
            LexicalTerm.term,
        )
        .join(
            LexicalTerm,
            LexicalTerm.id
            == LexicalPosting.term_id,
        )
        .where(
            LexicalPosting.chunk_id.in_(
                feedback_chunk_ids
            )
        )
    ).all()

    if not feedback_postings:
        return (
            initial_results[:limit],
            PRFSearchDiagnostics(
                applied=False,
                original_query=normalized_query,
                expanded_query=normalized_query,
                feedback_chunk_ids=(
                    feedback_chunk_ids
                ),
                expansion_terms=(),
                alpha=alpha,
                beta=beta,
            ),
        )

    feedback_term_ids = {
        term_id
        for (
            _,
            term_id,
            _,
            _,
        ) in feedback_postings
    }

    feedback_df_rows = db.execute(
        select(
            LexicalPosting.term_id,
            func.count(
                LexicalPosting.id
            ),
        )
        .where(
            LexicalPosting.term_id.in_(
                feedback_term_ids
            )
        )
        .group_by(
            LexicalPosting.term_id
        )
    ).all()

    feedback_df = {
        term_id: int(df)
        for term_id, df
        in feedback_df_rows
    }

    # -------------------------------------------------
    # PSEUDO-RELEVANT CENTROID
    # -------------------------------------------------
    #
    # Every feedback chunk contributes its TF-IDF
    # term vector.
    #
    # The average of those vectors is the
    # pseudo-relevant centroid.
    # -------------------------------------------------

    centroid_weights: dict[
        str,
        float,
    ] = defaultdict(float)

    feedback_count = len(
        feedback_chunk_ids
    )

    for (
        _,
        term_id,
        term_frequency,
        term_text,
    ) in feedback_postings:
        idf = calculate_idf(
            total_chunks=total_chunks,
            document_frequency=(
                feedback_df.get(
                    term_id,
                    0,
                )
            ),
        )

        term_weight = (
            term_frequency
            * idf
        )

        centroid_weights[
            term_text
        ] += (
            term_weight
            / feedback_count
        )

    # -------------------------------------------------
    # ORIGINAL QUERY VECTOR
    # -------------------------------------------------

    original_tf = Counter(
        original_tokens
    )

    original_terms = db.scalars(
        select(
            LexicalTerm
        ).where(
            LexicalTerm.term.in_(
                list(
                    original_tf.keys()
                )
            )
        )
    ).all()

    original_term_ids = [
        term.id
        for term
        in original_terms
    ]

    original_df: dict[
        int,
        int,
    ] = {}

    if original_term_ids:
        original_df_rows = db.execute(
            select(
                LexicalPosting.term_id,
                func.count(
                    LexicalPosting.id
                ),
            )
            .where(
                LexicalPosting.term_id.in_(
                    original_term_ids
                )
            )
            .group_by(
                LexicalPosting.term_id
            )
        ).all()

        original_df = {
            term_id: int(df)
            for term_id, df
            in original_df_rows
        }

    # -------------------------------------------------
    # POSITIVE ROCCHIO UPDATE
    #
    # q_new = alpha * q_original#       + beta  * relevant_centroid
    #
    # No explicit negative feedback set exists
    # in pseudo relevance feedback, so gamma
    # is intentionally omitted here.
    # -------------------------------------------------

    rocchio_weights: dict[
        str,
        float,
    ] = defaultdict(float)

    for term in original_terms:
        idf = calculate_idf(
            total_chunks=total_chunks,
            document_frequency=(
                original_df.get(
                    term.id,
                    0,
                )
            ),
        )

        original_weight = (
            original_tf[
                term.term
            ]
            * idf
        )

        rocchio_weights[
            term.term
        ] += (
            alpha
            * original_weight
        )

    for (
        term_text,
        centroid_weight,
    ) in centroid_weights.items():
        rocchio_weights[
            term_text
        ] += (
            beta
            * centroid_weight
        )

    original_token_set = set(
        original_tokens
    )

    expansion_candidates = [
        (
            term,
            weight,
        )
        for (
            term,
            weight,
        ) in rocchio_weights.items()
        if (
            term
            not in original_token_set
            and weight > 0
        )
    ]

    expansion_candidates.sort(
        key=lambda item: (
            -item[1],
            item[0],
        )
    )

    expansion_terms = tuple(
        term
        for term, _
        in expansion_candidates[
            :expansion_term_limit
        ]
    )

    if not expansion_terms:
        return (
            initial_results[:limit],
            PRFSearchDiagnostics(
                applied=False,
                original_query=normalized_query,
                expanded_query=normalized_query,
                feedback_chunk_ids=(
                    feedback_chunk_ids
                ),
                expansion_terms=(),
                alpha=alpha,
                beta=beta,
            ),
        )

    expanded_query = " ".join(
        [
            normalized_query,
            *expansion_terms,
        ]
    )

    # -------------------------------------------------
    # SECOND RETRIEVAL
    # -------------------------------------------------
    #
    # The final VSM search uses the expanded query
    # and our previously implemented Index
    # Elimination optimization.
    # -------------------------------------------------

    final_results = search_vsm(
        db=db,
        query=expanded_query,
        limit=limit,
        use_index_elimination=True,
    )

    return (
        final_results,
        PRFSearchDiagnostics(
            applied=True,
            original_query=normalized_query,
            expanded_query=expanded_query,
            feedback_chunk_ids=(
                feedback_chunk_ids
            ),
            expansion_terms=(
                expansion_terms
            ),
            alpha=alpha,
            beta=beta,
        ),
    )