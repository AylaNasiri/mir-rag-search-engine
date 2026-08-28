
    
from pydantic import BaseModel


class SearchResultResponse(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    filename: str
    chunk_index: int
    score: float
    chunk_text: str


class PRFResponse(BaseModel):
    enabled: bool
    applied: bool
    original_query: str
    expanded_query: str
    feedback_chunk_ids: list[int]
    expansion_terms: list[str]
    alpha: float
    beta: float


class SearchResponse(BaseModel):
    query: str
    mode: str
    total: int
    results: list[SearchResultResponse]
    prf: PRFResponse | None = None