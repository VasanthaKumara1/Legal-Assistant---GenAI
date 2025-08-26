"""
Run the Legal Document Demystification AI application.

This module provides a simple way to start the FastAPI server
for the Legal Document Demystification AI application.

Usage:
    python run.py

The application will start on http://localhost:8000
"""

import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )