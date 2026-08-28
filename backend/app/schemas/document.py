
    
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_path: str
    file_size: int | None
    indexing_status: str
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DocumentProcessResponse(BaseModel):
    document_id: int
    indexing_status: str
    chunk_count: int


class ChunkDetailResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    chunk_text: str
    token_count: int
    vector_id: str | None
    has_embedding: bool
    created_at: datetime


class DocumentDetailResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_path: str
    file_size: int | None
    indexing_status: str
    chunk_count: int
    embedding_count: int
    created_at: datetime
    updated_at: datetime
    chunks: list[ChunkDetailResponse]