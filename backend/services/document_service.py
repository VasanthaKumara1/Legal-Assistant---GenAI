"""
Document processing service that coordinates OCR and AI services.
"""
import time
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

from backend.models.database import Document, ProcessingLog
from backend.services.ocr_service import ocr_service
from backend.services.ai_service import ai_service


class DocumentProcessingService:
    """Service for coordinating document processing pipeline."""
    
    async def process_document(
        self, 
        document_id: int, 
        db: Session,
        process_ocr: bool = True,
        process_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Process a document through the OCR and AI pipeline.
        
        Args:
            document_id: ID of the document to process
            db: Database session
            process_ocr: Whether to run OCR extraction
            process_ai: Whether to run AI simplification
            
        Returns:
            Dictionary with processing results
        """
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        results = {
            "document_id": document_id,
            "ocr_success": False,
            "ai_success": False,
            "ocr_text": None,
            "simplified_text": None,
            "total_processing_time": 0,
            "tokens_used": 0
        }
        
        start_time = time.time()
        
        try:
            # Process OCR if requested and not already completed
            if process_ocr and document.ocr_status != "completed":
                logger.info(f"Starting OCR processing for document {document_id}")
                ocr_success = await self._process_ocr(document, db)
                results["ocr_success"] = ocr_success
                
                if ocr_success:
                    results["ocr_text"] = document.original_text
            
            # Process AI simplification if requested and OCR is completed
            if process_ai and document.ocr_status == "completed" and document.original_text:
                if document.ai_status != "completed":
                    logger.info(f"Starting AI processing for document {document_id}")
                    ai_success = await self._process_ai(document, db)
                    results["ai_success"] = ai_success
                    
                    if ai_success:
                        results["simplified_text"] = document.simplified_text
                        results["tokens_used"] = document.tokens_used or 0
            
            # Update total processing time
            total_time = time.time() - start_time
            results["total_processing_time"] = total_time
            
            if document.processing_time is None:
                document.processing_time = total_time
            else:
                document.processing_time += total_time
            
            db.commit()
            
            logger.info(f"Document {document_id} processing completed in {total_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Document processing failed for {document_id}: {str(e)}")
            db.rollback()
            raise e
    
    async def _process_ocr(self, document: Document, db: Session) -> bool:
        """Process OCR for a document."""
        try:
            # Log start of OCR processing
            self._log_processing_event(
                document.id, "ocr", "started", "OCR processing started", db
            )
            
            # Update document status
            document.ocr_status = "processing"
            db.commit()
            
            # Extract text using OCR service
            extracted_text, success = await ocr_service.extract_text(
                document.file_path, 
                document.mime_type
            )
            
            if success and extracted_text:
                # Update document with extracted text
                document.original_text = extracted_text
                document.ocr_status = "completed"
                
                # Log successful completion
                self._log_processing_event(
                    document.id, "ocr", "completed", 
                    f"OCR completed successfully. Extracted {len(extracted_text)} characters.", 
                    db
                )
                
                db.commit()
                logger.info(f"OCR completed for document {document.id}")
                return True
            else:
                # OCR failed
                document.ocr_status = "failed"
                
                # Log failure
                self._log_processing_event(
                    document.id, "ocr", "failed", 
                    "OCR extraction failed or no text extracted", 
                    db
                )
                
                db.commit()
                logger.error(f"OCR failed for document {document.id}")
                return False
                
        except Exception as e:
            document.ocr_status = "failed"
            
            # Log error
            self._log_processing_event(
                document.id, "ocr", "failed", 
                f"OCR processing error: {str(e)}", 
                db, error_details=str(e)
            )
            
            db.commit()
            logger.error(f"OCR processing error for document {document.id}: {str(e)}")
            return False
    
    async def _process_ai(self, document: Document, db: Session) -> bool:
        """Process AI simplification for a document."""
        try:
            # Log start of AI processing
            self._log_processing_event(
                document.id, "ai_simplification", "started", 
                "AI simplification started", db
            )
            
            # Update document status
            document.ai_status = "processing"
            db.commit()
            
            # Simplify text using AI service
            simplified_text, tokens_used, processing_time = await ai_service.simplify_legal_text(
                document.original_text
            )
            
            if simplified_text:
                # Update document with simplified text
                document.simplified_text = simplified_text
                document.tokens_used = tokens_used
                document.model_used = ai_service.settings.openai_model
                document.ai_status = "completed"
                
                # Log successful completion
                self._log_processing_event(
                    document.id, "ai_simplification", "completed",
                    f"AI simplification completed. Used {tokens_used} tokens in {processing_time:.2f}s.",
                    db, processing_time=processing_time
                )
                
                db.commit()
                logger.info(f"AI simplification completed for document {document.id}")
                return True
            else:
                # AI processing failed
                document.ai_status = "failed"
                
                # Log failure
                self._log_processing_event(
                    document.id, "ai_simplification", "failed",
                    "AI simplification failed or no output generated",
                    db
                )
                
                db.commit()
                logger.error(f"AI simplification failed for document {document.id}")
                return False
                
        except Exception as e:
            document.ai_status = "failed"
            
            # Log error
            self._log_processing_event(
                document.id, "ai_simplification", "failed",
                f"AI processing error: {str(e)}",
                db, error_details=str(e)
            )
            
            db.commit()
            logger.error(f"AI processing error for document {document.id}: {str(e)}")
            return False
    
    def _log_processing_event(
        self, 
        document_id: int, 
        process_type: str, 
        status: str, 
        message: str, 
        db: Session,
        error_details: Optional[str] = None,
        processing_time: Optional[float] = None
    ):
        """Log a processing event to the database."""
        log_entry = ProcessingLog(
            document_id=document_id,
            process_type=process_type,
            status=status,
            message=message,
            error_details=error_details,
            processing_time=processing_time
        )
        
        db.add(log_entry)
        db.commit()
    
    async def get_processing_status(self, document_id: int, db: Session) -> Dict[str, Any]:
        """Get the current processing status of a document."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        return {
            "document_id": document_id,
            "filename": document.filename,
            "ocr_status": document.ocr_status,
            "ai_status": document.ai_status,
            "processing_time": document.processing_time,
            "tokens_used": document.tokens_used,
            "model_used": document.model_used
        }


# Global document processing service instance
document_processor = DocumentProcessingService()