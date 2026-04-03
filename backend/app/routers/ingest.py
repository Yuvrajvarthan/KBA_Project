from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import tempfile
import time
import logging
from pathlib import Path

from app.models.ingestion import (
    IngestionResponse, YouTubeIngestionRequest, WebIngestionRequest,
    IngestionStats, ErrorResponse, DocumentType
)
from app.services.document_parser import DocumentParser
from app.services.youtube_transcript import YouTubeTranscriptService
from app.services.web_scraper import WebScraper
from app.utils.text_processor import TextProcessor
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Temporary storage for demonstration (in production, this would be in a database)
ingested_documents = {}
ingestion_stats = {
    "total_documents": 0,
    "total_chunks": 0,
    "documents_by_type": {"pdf": 0, "docx": 0, "txt": 0, "youtube": 0, "web": 0},
    "chunks_by_source": {"document": 0, "youtube": 0, "web": 0}
}

def validate_file(file: UploadFile) -> DocumentType:
    """Validate uploaded file and return its type"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(file.filename).suffix.lower().lstrip('.')
    
    if file_extension not in settings.get_allowed_file_types_list():
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_extension}' not allowed. Allowed types: {', '.join(settings.get_allowed_file_types_list())}"
        )
    
    return DocumentType(file_extension)

async def process_and_store_text(text: str, source_type: str, source_id: str, metadata: dict) -> int:
    """Process text, create chunks, and store them (placeholder for now)"""
    if not text.strip():
        return 0
    
    # Clean and validate text
    cleaned_text = TextProcessor.clean_text(text)
    quality_check = TextProcessor.validate_text_quality(cleaned_text)
    
    if not quality_check["is_valid"]:
        logger.warning(f"Text quality issues for {source_id}: {quality_check['issues']}")
        # Still process but with warning
    
    # Create chunks
    chunks = TextProcessor.chunk_text(
        cleaned_text, 
        chunk_size=settings.chunk_size, 
        overlap=settings.chunk_overlap
    )
    
    # Store chunks (placeholder - in Stage 3 we'll store in ChromaDB)
    chunk_count = 0
    for i, chunk_text in enumerate(chunks):
        chunk_metadata = {
            "chunk_index": i,
            "source_type": source_type,
            "source_id": source_id,
            "source_title": metadata.get("title", ""),
            "word_count": len(chunk_text.split()),
            "char_count": len(chunk_text),
            **metadata
        }
        
        # TODO: Store in ChromaDB in Stage 3
        # For now, just count the chunks
        chunk_count += 1
    
    return chunk_count

@router.post("/ingest/document", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Upload and ingest document files (PDF, DOCX, TXT)"""
    start_time = time.time()
    
    try:
        # Validate file
        file_type = validate_file(file)
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type.value}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Parse document based on type
            if file_type == DocumentType.PDF:
                result = await DocumentParser.parse_pdf(temp_file_path)
            elif file_type == DocumentType.DOCX:
                result = await DocumentParser.parse_docx(temp_file_path)
            elif file_type == DocumentType.TXT:
                result = await DocumentParser.parse_txt(temp_file_path)
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse {file_type.value} file: {result.get('error', 'Unknown error')}"
                )
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Prepare metadata
            metadata = {
                "filename": file.filename,
                "file_type": file_type.value,
                "file_size": len(file_content),
                "document_type": file_type.value,
                **result["metadata"]
            }
            
            # Process and store text
            chunk_count = await process_and_store_text(
                result["text"], 
                "document", 
                document_id, 
                metadata
            )
            
            # Update stats
            ingestion_stats["total_documents"] += 1
            ingestion_stats["total_chunks"] += chunk_count
            ingestion_stats["documents_by_type"][file_type.value] += 1
            ingestion_stats["chunks_by_source"]["document"] += chunk_count
            
            # Store document info
            ingested_documents[document_id] = {
                "source_type": "document",
                "metadata": metadata,
                "chunks": chunk_count,
                "ingested_at": time.time()
            }
            
            processing_time = time.time() - start_time
            
            return IngestionResponse(
                success=True,
                message=f"Successfully ingested {file_type.value} file",
                document_id=document_id,
                chunks_created=chunk_count,
                source_type="document",
                processing_time=processing_time,
                metadata=metadata
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/ingest/youtube", response_model=IngestionResponse)
async def ingest_youtube(request: YouTubeIngestionRequest):
    """Ingest YouTube video transcript"""
    start_time = time.time()
    
    try:
        # Get transcript
        result = await YouTubeTranscriptService.get_transcript(request.url)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get YouTube transcript: {result.get('error', 'Unknown error')}"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            "url": request.url,
            "source_type": "youtube",
            **result["metadata"]
        }
        
        # Process and store text
        chunk_count = await process_and_store_text(
            result["text"], 
            "youtube", 
            document_id, 
            metadata
        )
        
        # Update stats
        ingestion_stats["total_documents"] += 1
        ingestion_stats["total_chunks"] += chunk_count
        ingestion_stats["documents_by_type"]["youtube"] += 1
        ingestion_stats["chunks_by_source"]["youtube"] += chunk_count
        
        # Store document info
        ingested_documents[document_id] = {
            "source_type": "youtube",
            "metadata": metadata,
            "chunks": chunk_count,
            "ingested_at": time.time()
        }
        
        processing_time = time.time() - start_time
        
        return IngestionResponse(
            success=True,
            message="Successfully ingested YouTube transcript",
            document_id=document_id,
            chunks_created=chunk_count,
            source_type="youtube",
            processing_time=processing_time,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting YouTube transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/ingest/web", response_model=IngestionResponse)
async def ingest_web(request: WebIngestionRequest):
    """Ingest website content"""
    start_time = time.time()
    
    try:
        # Scrape website
        result = await WebScraper.scrape_website(request.url)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to scrape website: {result.get('error', 'Unknown error')}"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            "url": request.url,
            "source_type": "web",
            **result["metadata"]
        }
        
        # Process and store text
        chunk_count = await process_and_store_text(
            result["text"], 
            "web", 
            document_id, 
            metadata
        )
        
        # Update stats
        ingestion_stats["total_documents"] += 1
        ingestion_stats["total_chunks"] += chunk_count
        ingestion_stats["documents_by_type"]["web"] += 1
        ingestion_stats["chunks_by_source"]["web"] += chunk_count
        
        # Store document info
        ingested_documents[document_id] = {
            "source_type": "web",
            "metadata": metadata,
            "chunks": chunk_count,
            "ingested_at": time.time()
        }
        
        processing_time = time.time() - start_time
        
        return IngestionResponse(
            success=True,
            message="Successfully ingested website content",
            document_id=document_id,
            chunks_created=chunk_count,
            source_type="web",
            processing_time=processing_time,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting website content: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/ingest/stats", response_model=IngestionStats)
async def get_ingest_stats():
    """Get ingestion statistics"""
    return IngestionStats(
        total_documents=ingestion_stats["total_documents"],
        total_chunks=ingestion_stats["total_chunks"],
        documents_by_type=ingestion_stats["documents_by_type"],
        chunks_by_source=ingestion_stats["chunks_by_source"]
    )
