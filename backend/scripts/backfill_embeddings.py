
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models import Chunk
from app.services.embedding_service import embed_text


def backfill_embeddings() -> None:
    db = SessionLocal()

    try:
        chunks = db.scalars(
            select(Chunk)
            .where(Chunk.embedding.is_(None))
            .order_by(Chunk.id)
        ).all()

        print(f"Chunks without embedding: {len(chunks)}")

        for index, chunk in enumerate(chunks, start=1):
            print(
                f"Embedding chunk "
                f"{chunk.id} "
                f"({index}/{len(chunks)})..."
            )

            embedding = embed_text(
                chunk.chunk_text
            )

            if len(embedding) != 384:
                raise ValueError(
                    f"Invalid embedding dimension "
                    f"for chunk {chunk.id}: "
                    f"{len(embedding)}"
                )

            chunk.embedding = embedding

        db.commit()

        print(
            f"Successfully embedded "
            f"{len(chunks)} chunks."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()