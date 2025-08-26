"""
OCR service for extracting text from various document formats.
"""
import os
import tempfile
from typing import Optional, Tuple
from PIL import Image
import pytesseract
import pdf2image
from docx import Document as DocxDocument
import PyPDF2
from loguru import logger
from backend.config.settings import settings


class OCRService:
    """Service for optical character recognition on various document formats."""
    
    def __init__(self):
        """Initialize OCR service."""
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    
    async def extract_text(self, file_path: str, mime_type: str) -> Tuple[str, bool]:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the file
            
        Returns:
            Tuple of (extracted_text, success)
        """
        try:
            logger.info(f"Starting OCR extraction for {file_path} with type {mime_type}")
            
            if mime_type == "application/pdf":
                return await self._extract_from_pdf(file_path)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                             "application/msword"]:
                return await self._extract_from_docx(file_path)
            elif mime_type.startswith("image/"):
                return await self._extract_from_image(file_path)
            elif mime_type == "text/plain":
                return await self._extract_from_text(file_path)
            else:
                logger.error(f"Unsupported file type: {mime_type}")
                return "", False
                
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {str(e)}")
            return "", False
    
    async def _extract_from_pdf(self, file_path: str) -> Tuple[str, bool]:
        """Extract text from PDF file."""
        try:
            # First try to extract text directly (for text-based PDFs)
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # If we got meaningful text, return it
                if text.strip() and len(text.strip()) > 50:
                    logger.info(f"Extracted text directly from PDF: {len(text)} characters")
                    return text.strip(), True
            
            # If direct extraction failed, use OCR on images
            logger.info("Direct PDF text extraction failed, trying OCR on images")
            return await self._extract_from_pdf_images(file_path)
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            return "", False
    
    async def _extract_from_pdf_images(self, file_path: str) -> Tuple[str, bool]:
        """Extract text from PDF by converting to images and using OCR."""
        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(file_path)
            full_text = ""
            
            for i, image in enumerate(images):
                logger.info(f"Processing PDF page {i+1}/{len(images)}")
                text = pytesseract.image_to_string(image, lang=settings.ocr_language)
                full_text += text + "\n"
            
            logger.info(f"OCR extracted {len(full_text)} characters from PDF")
            return full_text.strip(), True
            
        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {str(e)}")
            return "", False
    
    async def _extract_from_docx(self, file_path: str) -> Tuple[str, bool]:
        """Extract text from DOCX file."""
        try:
            doc = DocxDocument(file_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            
            text = "\n".join(full_text)
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text.strip(), True
            
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            return "", False
    
    async def _extract_from_image(self, file_path: str) -> Tuple[str, bool]:
        """Extract text from image file using OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang=settings.ocr_language)
            
            logger.info(f"OCR extracted {len(text)} characters from image")
            return text.strip(), True
            
        except Exception as e:
            logger.error(f"Image OCR extraction failed: {str(e)}")
            return "", False
    
    async def _extract_from_text(self, file_path: str) -> Tuple[str, bool]:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"Read {len(text)} characters from text file")
            return text.strip(), True
            
        except Exception as e:
            logger.error(f"Text file reading failed: {str(e)}")
            return "", False


# Global OCR service instance
ocr_service = OCRService()