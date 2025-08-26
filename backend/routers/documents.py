"""
API router for document upload and processing endpoints.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from backend.models.database import Document, get_db, create_tables
from backend.models.schemas import (
    DocumentUploadResponse, 
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    DocumentContentResponse,
    ErrorResponse
)
from backend.services.document_service import document_processor
from backend.utils.file_utils import validate_file, save_uploaded_file, get_file_mime_type, get_file_size
from backend.config.settings import settings

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize database tables
create_tables()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.
    
    - **file**: Document file (PDF, DOCX, images, or text)
    - Returns document metadata and upload confirmation
    """
    try:
        # Validate file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Save file to disk
        file_path, unique_filename = save_uploaded_file(file, settings.upload_directory)
        
        # Get file metadata
        mime_type = get_file_mime_type(file_path)
        file_size = get_file_size(file_path)
        
        # Create database record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            upload_timestamp=datetime.utcnow()
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Document uploaded: {file.filename} -> {unique_filename} (ID: {document.id})")
        
        return DocumentUploadResponse(
            id=document.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_size,
            mime_type=mime_type,
            upload_timestamp=document.upload_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Document upload failed")


@router.post("/{document_id}/process", response_model=DocumentProcessingResponse)
async def process_document(
    document_id: int,
    request: DocumentProcessingRequest,
    db: Session = Depends(get_db)
):
    """
    Process a document through OCR and/or AI simplification.
    
    - **document_id**: ID of the uploaded document
    - **process_ocr**: Whether to extract text using OCR
    - **process_ai**: Whether to simplify text using AI
    """
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document
        results = await document_processor.process_document(
            document_id=document_id,
            db=db,
            process_ocr=request.process_ocr,
            process_ai=request.process_ai
        )
        
        # Refresh document to get updated status
        db.refresh(document)
        
        message = "Processing completed"
        if request.process_ocr and not results["ocr_success"]:
            message = "OCR processing failed"
        elif request.process_ai and not results["ai_success"]:
            message = "AI processing failed"
        
        return DocumentProcessingResponse(
            document_id=document_id,
            ocr_status=document.ocr_status,
            ai_status=document.ai_status,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/content", response_model=DocumentContentResponse)
async def get_document_content(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the original and simplified content of a document.
    
    - **document_id**: ID of the document
    - Returns original and simplified text content
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentContentResponse(
            document_id=document.id,
            filename=document.original_filename,
            original_text=document.original_text,
            simplified_text=document.simplified_text,
            ocr_status=document.ocr_status,
            ai_status=document.ai_status,
            processing_time=document.processing_time,
            tokens_used=document.tokens_used,
            model_used=document.model_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document content")


@router.get("/{document_id}/status")
async def get_document_status(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the processing status of a document.
    
    - **document_id**: ID of the document
    - Returns current processing status
    """
    try:
        status = await document_processor.get_processing_status(document_id, db)
        return status
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get document status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document status")


@router.get("/", response_model=List[DocumentContentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents.
    
    - **skip**: Number of documents to skip (for pagination)
    - **limit**: Maximum number of documents to return
    """
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        
        return [
            DocumentContentResponse(
                document_id=doc.id,
                filename=doc.original_filename,
                original_text=doc.original_text,
                simplified_text=doc.simplified_text,
                ocr_status=doc.ocr_status,
                ai_status=doc.ai_status,
                processing_time=doc.processing_time,
                tokens_used=doc.tokens_used,
                model_used=doc.model_used
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")