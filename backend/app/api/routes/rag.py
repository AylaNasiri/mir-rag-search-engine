
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.rag import (
    RAGAskRequest,
    RAGAskResponse,
    RAGSourceResponse,
)
from app.services.rag_service import (
    RAGServiceError,
    answer_question,
)


router = APIRouter(
    prefix="/rag",
)


@router.post(
    "/ask",
    response_model=RAGAskResponse,
)
def ask_rag(
    payload: RAGAskRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    query = payload.query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    try:
        result = answer_question(
            db=db,
            query=query,
            limit=payload.limit,
        )

    except RAGServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate RAG answer.",
        ) from exc

    return RAGAskResponse(
        query=result.query,
        answer=result.answer,
        sources=[
            RAGSourceResponse(
                chunk_id=source.chunk_id,
                document_id=source.document_id,
                document_title=source.document_title,
                filename=source.filename,
                chunk_index=source.chunk_index,
                score=source.score,
            )
            for source in result.sources
        ],
    )