"""
Document upload and management endpoints.
"""

import os
import uuid
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse

from app.models.pydantic_models import DocumentResponse, DocumentUpload
from app.services.document_service import DocumentAnalysisService
from app.core.config import settings

router = APIRouter()
document_service = DocumentAnalysisService()


@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    language: str = Form("en")
):
    """
    Upload a legal document for analysis.
    
    Supported file types: PDF, DOCX, TXT
    Max file size: 10MB
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Validate file size
        contents = await file.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # Extract text content
        text_content = await extract_text_from_file(file_path, file_extension)
        
        # Create document record (in a real app, this would save to database)
        document_data = {
            "id": hash(file_id) % 1000000,  # Simple ID generation for demo
            "title": title or file.filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_type": file_extension,
            "content": text_content,
            "document_type": document_type,
            "industry": industry,
            "file_size": len(contents),
            "language": language,
            "upload_date": "2024-01-01T00:00:00"  # Would use actual timestamp
        }
        
        # Start analysis
        analysis_result = await document_service.analyze_document(
            text_content, 
            document_type
        )
        
        return {
            "message": "Document uploaded successfully",
            "document": document_data,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list")
async def list_documents():
    """List all uploaded documents."""
    # In a real app, this would query the database
    return {
        "documents": [],
        "total": 0,
        "message": "Document listing feature - connect to database"
    }


@router.get("/{document_id}")
async def get_document(document_id: int):
    """Get document details by ID."""
    # In a real app, this would query the database
    return {
        "message": f"Document {document_id} details - connect to database"
    }


@router.delete("/{document_id}")
async def delete_document(document_id: int):
    """Delete a document by ID."""
    # In a real app, this would delete from database and filesystem
    return {
        "message": f"Document {document_id} deleted - connect to database"
    }


async def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """Extract text content from uploaded file."""
    try:
        if file_extension == ".txt":
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        
        elif file_extension == ".pdf":
            # Note: This is a simplified PDF extraction
            # In production, use more robust libraries like pymupdf or pdfplumber
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        elif file_extension == ".docx":
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from file: {str(e)}"
        )