from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    DOCUMENT = "document"
    YOUTUBE = "youtube"
    WEB = "web"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class IngestionRequest(BaseModel):
    source_type: SourceType
    content: Optional[str] = None
    url: Optional[str] = None
    file_metadata: Optional[Dict[str, Any]] = None

class DocumentIngestionRequest(BaseModel):
    file_type: DocumentType
    filename: str
    file_size: int
    file_metadata: Optional[Dict[str, Any]] = None

class YouTubeIngestionRequest(BaseModel):
    url: str
    video_id: Optional[str] = None

class WebIngestionRequest(BaseModel):
    url: str
    title: Optional[str] = None

class ChunkMetadata(BaseModel):
    chunk_index: int
    source_type: SourceType
    source_id: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    document_type: Optional[DocumentType] = None
    filename: Optional[str] = None
    page_number: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    word_count: Optional[int] = None
    char_count: Optional[int] = None

class TextChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: ChunkMetadata

class IngestionResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_created: int = 0
    source_type: SourceType
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class IngestionStats(BaseModel):
    total_documents: int
    total_chunks: int
    documents_by_type: Dict[str, int]
    chunks_by_source: Dict[str, int]
    last_ingestion: Optional[datetime] = None

class ValidationError(BaseModel):
    field: str
    message: str
    value: Any

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[List[ValidationError]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
