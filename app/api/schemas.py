from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    retrieval_mode: str
    context_used: str


class DocumentOut(BaseModel):
    id: int
    filename: str
    title: str | None
    source_url: str | None
    num_pages: int | None
    status: str

    class Config:
        from_attributes = True
