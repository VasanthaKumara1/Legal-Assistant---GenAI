"""
Database models for the AI Legal Assistant application.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.config.settings import settings

Base = declarative_base()


class Document(Base):
    """Document model for storing uploaded documents and their metadata."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # OCR and Processing Status
    ocr_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    original_text = Column(Text, nullable=True)
    
    # AI Simplification Status  
    ai_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    simplified_text = Column(Text, nullable=True)
    
    # Processing metadata
    processing_time = Column(Float, nullable=True)  # in seconds
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.ocr_status}')>"


class ProcessingLog(Base):
    """Log model for tracking processing events and errors."""
    
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)  # Foreign key to documents
    process_type = Column(String(50), nullable=False)  # ocr, ai_simplification
    status = Column(String(50), nullable=False)  # started, completed, failed
    message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, document_id={self.document_id}, type='{self.process_type}', status='{self.status}')>"


# Database engine and session setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()