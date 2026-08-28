
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Document
from app.retrieval.bm25 import (
    BM25SearchError,
    search_bm25,
)
from app.retrieval.hybrid import (
    HybridSearchError,
    search_hybrid,
)
from app.retrieval.prf import (
    PRFSearchError,
    search_vsm_with_prf,
)
from app.retrieval.semantic import (
    SemanticSearchError,
    search_semantic,
)
from app.retrieval.vsm import (
    VSMSearchError,
    search_vsm,
)
from app.schemas.search import (
    PRFResponse,
    SearchResponse,
    SearchResultResponse,
)


router = APIRouter(
    prefix="/search",
)


@router.get(
    "",
    response_model=SearchResponse,
)
def search(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=500,
            description="Search query",
        ),
    ],
    mode: Annotated[
        str,
        Query(
            description=(
                "Retrieval mode: "
                "vsm, bm25, semantic, or hybrid"
            ),
        ),
    ] = "vsm",
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=50,
            description=(
                "Maximum number of results"
            ),
        ),
    ] = 10,
    prf: Annotated[
        bool,
        Query(
            description=(
                "Enable Pseudo Relevance "
                "Feedback for VSM"
            ),
        ),
    ] = False,
):
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Search query cannot be empty."
            ),
        )

    normalized_mode = (
        mode.strip().lower()
    )

    if normalized_mode not in {
        "vsm",
        "bm25",
        "semantic",
        "hybrid",
    }:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                f"Unsupported search mode: "
                f"{mode}"
            ),
        )

    if (
        prf
        and normalized_mode != "vsm"
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Pseudo Relevance Feedback "
                "is only available for VSM."
            ),
        )

    prf_response: (
        PRFResponse
        | None
    ) = None

    try:
        if normalized_mode == "vsm":
            if prf:
                (
                    search_results,
                    prf_diagnostics,
                ) = search_vsm_with_prf(
                    db=db,
                    query=query,
                    limit=limit,
                )

                prf_response = (
                    PRFResponse(
                        enabled=True,
                        applied=(
                            prf_diagnostics
                            .applied
                        ),
                        original_query=(
                            prf_diagnostics
                            .original_query
                        ),
                        expanded_query=(
                            prf_diagnostics
                            .expanded_query
                        ),
                        feedback_chunk_ids=(
                            list(
                                prf_diagnostics
                                .feedback_chunk_ids
                            )
                        ),
                        expansion_terms=(
                            list(
                                prf_diagnostics
                                .expansion_terms
                            )
                        ),
                        alpha=(prf_diagnostics
                            .alpha
                        ),
                        beta=(
                            prf_diagnostics
                            .beta
                        ),
                    )
                )

            else:
                search_results = (
                    search_vsm(
                        db=db,
                        query=query,
                        limit=limit,
                    )
                )

                prf_response = (
                    PRFResponse(
                        enabled=False,
                        applied=False,
                        original_query=query,
                        expanded_query=query,
                        feedback_chunk_ids=[],
                        expansion_terms=[],
                        alpha=1.0,
                        beta=0.75,
                    )
                )

        elif normalized_mode == "bm25":
            search_results = (
                search_bm25(
                    db=db,
                    query=query,
                    limit=limit,
                )
            )

        elif normalized_mode == "semantic":
            search_results = (
                search_semantic(
                    db=db,
                    query=query,
                    limit=limit,
                )
            )

        else:
            search_results = (
                search_hybrid(
                    db=db,
                    query=query,
                    limit=limit,
                )
            )

    except (
        VSMSearchError,
        PRFSearchError,
        BM25SearchError,
        SemanticSearchError,
        HybridSearchError,
    ) as exc:
        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Search failed.",
        ) from exc

    document_ids = {
        result.document_id
        for result in search_results
    }

    documents = []

    if document_ids:
        documents = db.scalars(
            select(
                Document
            ).where(
                Document.id.in_(
                    document_ids
                )
            )
        ).all()

    documents_by_id = {
        document.id: document
        for document in documents
    }

    response_results: list[
        SearchResultResponse
    ] = []

    for result in search_results:
        document = (
            documents_by_id.get(
                result.document_id
            )
        )

        if document is None:
            continue

        response_results.append(
            SearchResultResponse(
                chunk_id=(
                    result.chunk_id
                ),
                document_id=(
                    result.document_id
                ),
                document_title=(
                    document.title
                ),
                filename=(
                    document.filename
                ),
                chunk_index=(
                    result.chunk_index
                ),
                score=result.score,
                chunk_text=(
                    result.chunk_text
                ),
            )
        )

    return SearchResponse(
        query=query,
        mode=normalized_mode,
        total=len(
            response_results
        ),
        results=response_results,
        prf=prf_response,
    )