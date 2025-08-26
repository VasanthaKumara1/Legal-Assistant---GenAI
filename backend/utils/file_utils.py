"""
Utility functions for file handling and validation.
"""
import os
import uuid
import magic
from typing import Tuple, Optional
from fastapi import UploadFile
from backend.config.settings import settings


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file for size, type, and extension.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if file.size and file.size > settings.max_file_size:
        return False, f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
    
    # Check file extension
    if file.filename:
        file_extension = os.path.splitext(file.filename.lower())[1]
        if file_extension not in settings.allowed_extensions:
            return False, f"File type {file_extension} not allowed. Allowed types: {', '.join(settings.allowed_extensions)}"
    
    return True, None


def get_file_mime_type(file_path: str) -> str:
    """
    Get the MIME type of a file using python-magic.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception:
        # Fallback to guessing from extension
        extension = os.path.splitext(file_path.lower())[1]
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        return mime_map.get(extension, 'application/octet-stream')


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving the original extension.
    
    Args:
        original_filename: Original filename
        
    Returns:
        Unique filename
    """
    name, extension = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{extension}"


def save_uploaded_file(file: UploadFile, upload_dir: str) -> Tuple[str, str]:
    """
    Save uploaded file to disk and return file paths.
    
    Args:
        file: FastAPI UploadFile object
        upload_dir: Directory to save the file
        
    Returns:
        Tuple of (file_path, unique_filename)
    """
    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    # Reset file position for potential reuse
    file.file.seek(0)
    
    return file_path, unique_filename


def cleanup_file(file_path: str) -> bool:
    """
    Remove a file from disk.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        return False