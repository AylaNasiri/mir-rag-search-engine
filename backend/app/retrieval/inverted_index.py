

from collections import Counter

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Chunk, LexicalPosting, LexicalTerm
from app.retrieval.tokenizer import tokenize


class LexicalIndexingError(Exception):
    pass


def index_chunk(
    db: Session,
    chunk: Chunk,
) -> int:
    tokens = tokenize(chunk.chunk_text)

    chunk.token_count = len(tokens)

    db.execute(
        delete(LexicalPosting).where(
            LexicalPosting.chunk_id == chunk.id
        )
    )

    term_frequencies = Counter(tokens)

    for term_text, frequency in term_frequencies.items():
        term = db.scalar(
            select(LexicalTerm).where(
                LexicalTerm.term == term_text
            )
        )

        if term is None:
            term = LexicalTerm(
                term=term_text,
            )

            db.add(term)
            db.flush()

        posting = LexicalPosting(
            term_id=term.id,
            chunk_id=chunk.id,
            term_frequency=frequency,
        )

        db.add(posting)

    return len(term_frequencies)


def index_document(
    db: Session,
    document_id: int,
) -> tuple[int, int]:
    chunks = db.scalars(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
    ).all()

    if not chunks:
        raise LexicalIndexingError(
            f"No chunks found for document {document_id}."
        )

    total_terms = 0

    try:
        for chunk in chunks:
            total_terms += index_chunk(
                db=db,
                chunk=chunk,
            )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise LexicalIndexingError(
            f"Failed to build lexical index for document {document_id}."
        ) from exc

    return len(chunks), total_terms