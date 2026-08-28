
    
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models import Chunk, Document
from app.schemas.document import (
    ChunkDetailResponse,
    DocumentDetailResponse,
    DocumentProcessResponse,
    DocumentResponse,
)
from app.services.indexing_service import (
    DocumentIndexingError,
    process_document,
)


router = APIRouter(
    prefix="/documents",
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    chunk_count_subquery = (
        select(
            func.count(Chunk.id)
        )
        .where(
            Chunk.document_id
            == Document.id
        )
        .correlate(Document)
        .scalar_subquery()
    )

    statement = (
        select(
            Document,
            chunk_count_subquery.label(
                "chunk_count"
            ),
        )
        .order_by(
            Document.created_at.desc()
        )
    )

    rows = db.execute(
        statement
    ).all()

    documents: list[
        DocumentResponse
    ] = []

    for document, chunk_count in rows:
        response = (
            DocumentResponse
            .model_validate(
                document
            )
            .model_copy(
                update={
                    "chunk_count":
                        int(
                            chunk_count
                            or 0
                        )
                }
            )
        )

        documents.append(
            response
        )

    return documents


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
)
def get_document_details(
    document_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Document not found.",
        )

    chunks = db.scalars(
        select(Chunk)
        .where(
            Chunk.document_id
            == document_id
        )
        .order_by(
            Chunk.chunk_index.asc()
        )
    ).all()

    chunk_responses = [
        ChunkDetailResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            chunk_text=chunk.chunk_text,
            token_count=chunk.token_count,
            vector_id=chunk.vector_id,
            has_embedding=(
                chunk.embedding is not None
            ),
            created_at=chunk.created_at,
        )
        for chunk in chunks
    ]

    embedding_count = sum(
        1
        for chunk in chunks
        if chunk.embedding is not None
    )

    return DocumentDetailResponse(
        id=document.id,
        title=document.title,
        filename=document.filename,
        file_type=document.file_type,
        file_path=document.file_path,
        file_size=document.file_size,
        indexing_status=(
            document.indexing_status
        ),
        chunk_count=len(
            chunks
        ),
        embedding_count=(
            embedding_count
        ),
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunks=chunk_responses,
    )


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    file: UploadFile = File(...),
):
    original_filename = Path(
        file.filename or ""
    ).name

    if not original_filename:
        raise HTTPException(status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "File name is required."
            ),
        )

    extension = Path(
        original_filename
    ).suffix.lower()

    if (
        extension
        not in ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Only PDF and DOCX files "
                "are supported."
            ),
        )

    upload_directory = Path(
        settings.UPLOAD_DIR
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = (
        f"{uuid4()}{extension}"
    )

    destination = (
        upload_directory
        / stored_filename
    )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Uploaded file is empty."
            ),
        )

    destination.write_bytes(
        content
    )

    document = Document(
        title=Path(
            original_filename
        ).stem,
        filename=original_filename,
        file_type=(
            extension
            .removeprefix(".")
            .upper()
        ),
        file_path=str(
            destination
        ),
        file_size=len(
            content
        ),
        indexing_status="pending",
    )

    try:
        db.add(
            document
        )

        db.commit()

        db.refresh(
            document
        )

    except Exception:
        db.rollback()

        if destination.exists():
            destination.unlink()

        raise

    finally:
        await file.close()

    response = (
        DocumentResponse
        .model_validate(
            document
        )
        .model_copy(
            update={
                "chunk_count": 0
            }
        )
    )

    return response


@router.post(
    "/{document_id}/process",
    response_model=(
        DocumentProcessResponse
    ),
)
def process_uploaded_document(
    document_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Document not found."
            ),
        )

    try:
        chunk_count = (
            process_document(
                db=db,
                document=document,
            )
        )

    except (
        DocumentIndexingError
    ) as exc:
        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Document processing "
                "failed."
            ),
        ) from exc

    return (
        DocumentProcessResponse(
            document_id=document.id,
            indexing_status=(
                document.indexing_status
            ),
            chunk_count=(
                chunk_count
            ),
        )
    )


@router.delete(
    "/{document_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_document(
    document_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> None:
    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Document not found."
            ),
        )

    stored_file_path = Path(
        document.file_path
    )

    try:
        db.delete(
            document
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Document deletion "
                "failed."
            ),
        ) from exc

    try:
        stored_file_path.unlink(
            missing_ok=True
        )

    except OSError:
        pass