from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


# Auth Models
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Document Models
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str
    message: str


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime
    user_id: str


class DocumentList(BaseModel):
    documents: List[DocumentMetadata]
    total: int


# RAG Models
class SourceCitation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    chunk_text: str
    relevance_score: float


class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None
    conversation_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    conversation_id: str
    query_time_ms: float


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]
    created_at: datetime
    updated_at: datetime
