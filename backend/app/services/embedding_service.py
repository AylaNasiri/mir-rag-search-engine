
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingError(Exception):
    pass


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        settings.EMBEDDING_MODEL_NAME
    )


def embed_text(
    text: str,
) -> list[float]:
    normalized_text = text.strip()

    if not normalized_text:
        raise EmbeddingError(
            "Text cannot be empty."
        )

    try:
        model = get_embedding_model()

        vector = model.encode(
            normalized_text,
            normalize_embeddings=True,
        )

    except Exception as exc:
        raise EmbeddingError(
            "Failed to generate embedding."
        ) from exc

    embedding = vector.tolist()

    if len(embedding) != settings.EMBEDDING_DIMENSION:
        raise EmbeddingError(
            "Unexpected embedding dimension."
        )

    return embedding


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    normalized_texts = [
        text.strip()
        for text in texts
    ]

    if not normalized_texts:
        return []

    if any(
        not text
        for text in normalized_texts
    ):
        raise EmbeddingError(
            "Texts cannot contain empty values."
        )

    try:
        model = get_embedding_model()

        vectors = model.encode(
            normalized_texts,
            normalize_embeddings=True,
        )

    except Exception as exc:
        raise EmbeddingError(
            "Failed to generate embeddings."
        ) from exc

    embeddings = [
        vector.tolist()
        for vector in vectors
    ]

    if any(
        len(embedding)
        != settings.EMBEDDING_DIMENSION
        for embedding in embeddings
    ):
        raise EmbeddingError(
            "Unexpected embedding dimension."
        )

    return embeddings