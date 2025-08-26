"""
Database models for the Legal Assistant application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Document(Base):
    """Legal document model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(100))  # contract, lease, etc.
    industry = Column(String(100))  # consumer, business, etc.
    upload_date = Column(DateTime, default=func.now())
    file_size = Column(Integer)
    language = Column(String(5), default="en")
    
    # Relationships
    sections = relationship("DocumentSection", back_populates="document")
    explanations = relationship("Explanation", back_populates="document")
    user_sessions = relationship("UserSession", back_populates="document")


class DocumentSection(Base):
    """Document sections for structured analysis."""
    __tablename__ = "document_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    section_type = Column(String(100))  # terms, obligations, rights, etc.
    title = Column(String(255))
    content = Column(Text, nullable=False)
    start_position = Column(Integer)
    end_position = Column(Integer)
    importance_level = Column(String(20))  # critical, high, medium, low
    risk_level = Column(String(20))  # high, medium, low
    
    # Relationships
    document = relationship("Document", back_populates="sections")
    explanations = relationship("SectionExplanation", back_populates="section")


class Explanation(Base):
    """Simplified explanations for documents."""
    __tablename__ = "explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    complexity_level = Column(String(20))  # elementary, high_school, college, expert
    simplified_content = Column(Text, nullable=False)
    key_points = Column(JSON)  # List of key points
    rights_obligations = Column(JSON)  # Structured rights and obligations
    deadlines = Column(JSON)  # Important dates and deadlines
    red_flags = Column(JSON)  # Potential issues to watch out for
    confidence_score = Column(Float, default=0.0)
    created_date = Column(DateTime, default=func.now())
    model_used = Column(String(50))
    language = Column(String(5), default="en")
    
    # Relationships
    document = relationship("Document", back_populates="explanations")


class SectionExplanation(Base):
    """Detailed explanations for specific document sections."""
    __tablename__ = "section_explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("document_sections.id"))
    complexity_level = Column(String(20))
    simplified_text = Column(Text, nullable=False)
    what_it_means = Column(Text)  # "What does this mean for me?"
    impact_analysis = Column(Text)
    related_terms = Column(JSON)  # Related legal terms and definitions
    confidence_score = Column(Float, default=0.0)
    created_date = Column(DateTime, default=func.now())
    
    # Relationships
    section = relationship("DocumentSection", back_populates="explanations")


class LegalTerm(Base):
    """Legal terms dictionary."""
    __tablename__ = "legal_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(255), nullable=False, unique=True)
    definition = Column(Text, nullable=False)
    simple_definition = Column(Text, nullable=False)
    context = Column(String(100))  # contract, employment, real_estate, etc.
    examples = Column(JSON)
    related_terms = Column(JSON)
    usage_count = Column(Integer, default=0)
    created_date = Column(DateTime, default=func.now())


class UserSession(Base):
    """User sessions for tracking document interactions."""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    preferred_complexity = Column(String(20), default="high_school")
    preferred_language = Column(String(5), default="en")
    bookmarks = Column(JSON)  # Bookmarked sections
    notes = Column(JSON)  # User notes
    progress = Column(Float, default=0.0)  # Reading progress %
    created_date = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="user_sessions")


class AnalysisJob(Base):
    """Background analysis jobs."""
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    job_type = Column(String(50))  # parsing, simplification, translation
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    result = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_date = Column(DateTime, default=func.now())