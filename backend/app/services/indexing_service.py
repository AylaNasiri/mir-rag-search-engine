

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Chunk, Document
from app.retrieval.inverted_index import index_chunk
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_text
from app.services.parser_service import extract_text


class DocumentIndexingError(Exception):
    pass


def process_document(
    db: Session,
    document: Document,
) -> int:

    document.indexing_status = "processing"
    db.commit()

    try:
        # 1. Extract text from PDF/DOCX
        text = extract_text(
            document.file_path
        )

        # 2. Split extracted text into chunks
        chunk_contents = chunk_text(
            text
        )

        # 3. Remove old chunks.
        # Existing lexical postings are also removed
        # because of ON DELETE CASCADE.
        db.execute(
            delete(Chunk).where(
                Chunk.document_id == document.id
            )
        )

        # 4. Create, embed, and lexically index new chunks
        for index, chunk_content in enumerate(
            chunk_contents
        ):
            embedding = embed_text(
                chunk_content
            )

            if (
                len(embedding)
                != settings.EMBEDDING_DIMENSION
            ):
                raise ValueError(
                    "Invalid embedding dimension for "
                    f"document {document.id}, "
                    f"chunk {index}: "
                    f"{len(embedding)}"
                )

            chunk = Chunk(
                document_id=document.id,
                chunk_index=index,
                chunk_text=chunk_content,
                embedding=embedding,
                vector_id=None,
            )

            db.add(chunk)

            # We need the database-generated chunk ID
            # before creating lexical postings.
            db.flush()

            index_chunk(
                db=db,
                chunk=chunk,
            )

        # 5. Lexical and semantic indexing completed
        document.indexing_status = "indexed"

        db.commit()
        db.refresh(document)

        return len(chunk_contents)

    except Exception as exc:
        db.rollback()

        failed_document = db.get(
            Document,
            document.id,
        )

        if failed_document is not None:
            failed_document.indexing_status = "failed"
            db.commit()

        raise DocumentIndexingError(
            f"Failed to process document {document.id}"
        ) from exc