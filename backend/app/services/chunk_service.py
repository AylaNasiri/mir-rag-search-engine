
from app.core.config import settings


class ChunkingError(Exception):
    pass


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:

    chunk_size = chunk_size or settings.CHUNK_SIZE_WORDS
    overlap = (
        overlap
        if overlap is not None
        else settings.CHUNK_OVERLAP_WORDS
    )

    if not text.strip():
        raise ChunkingError(
            "Cannot chunk empty text."
        )

    if chunk_size <= 0:
        raise ChunkingError(
            "Chunk size must be greater than zero."
        )

    if overlap < 0:
        raise ChunkingError(
            "Chunk overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ChunkingError(
            "Chunk overlap must be smaller than chunk size."
        )

    words = text.split()

    chunks: list[str] = []

    start = 0

    step = chunk_size - overlap

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        if not chunk_words:
            break

        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        start += step

    return chunks