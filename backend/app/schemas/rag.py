
from pydantic import BaseModel, Field


class RAGAskRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=500,
        description="Question to answer using RAG",
    )

    limit: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Maximum number of retrieved chunks",
    )


class RAGSourceResponse(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    filename: str
    chunk_index: int
    score: float


class RAGAskResponse(BaseModel):
    query: str
    answer: str
    sources: list[RAGSourceResponse]