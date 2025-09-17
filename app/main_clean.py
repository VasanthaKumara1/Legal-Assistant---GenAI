"""
Legal Assistant - GenAI
A focused AI solution for demystifying and simplifying complex legal documents.
"""

import os
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import uuid

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Create a minimal working app first
app = FastAPI(
    title="Legal Document Demystification AI",
    description="Transform complex legal documents into clear, accessible guidance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Pydantic models
class TextSimplificationRequest(BaseModel):
    text: str
    reading_level: Optional[str] = "high_school"

class TextSimplificationResponse(BaseModel):
    original_text: str
    simplified_text: str
    reading_level: str
    success: bool

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Mock AI service (works without API key)
def simplify_text_mock(text: str, reading_level: str = "high_school") -> str:
    """Mock text simplification that doesn't require OpenAI API"""
    if not text:
        return "No text provided"
    
    # Simple text transformation for demo purposes
    simplified = text.replace("hereinafter", "from now on")
    simplified = simplified.replace("whereas", "since")
    simplified = simplified.replace("pursuant to", "according to")
    simplified = simplified.replace("aforementioned", "mentioned above")
    simplified = simplified.replace("notwithstanding", "despite")
    simplified = simplified.replace("shall", "will")
    simplified = simplified.replace("heretofore", "before this")
    simplified = simplified.replace("thereof", "of it")
    simplified = simplified.replace("therein", "in it")
    
    return f"[SIMPLIFIED for {reading_level} level]: {simplified}"

# Real AI service (requires OpenAI API key)
async def simplify_text_openai(text: str, reading_level: str = "high_school") -> str:
    """Real text simplification using OpenAI API"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        return simplify_text_mock(text, reading_level)
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        prompt = f"""
        Simplify the following legal text for a {reading_level} reading level.
        Make it clear, concise, and easy to understand while preserving the meaning.
        
        Original text:
        {text}
        
        Simplified text:
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return simplify_text_mock(text, reading_level)

@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "legal-assistant-genai",
        "version": "1.0.0",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.get("/api/info")
async def app_info():
    """Get application information"""
    return {
        "app_name": "Legal Document Demystification AI",
        "version": "1.0.0",
        "features": [
            "Document Upload",
            "Text Simplification", 
            "Health Check",
            "API Documentation"
        ],
        "documentation": "/docs"
    }

@app.post("/api/simplify", response_model=TextSimplificationResponse)
async def simplify_text(request: TextSimplificationRequest):
    """Simplify legal text to make it more understandable"""
    try:
        simplified = await simplify_text_openai(request.text, request.reading_level)
        
        return TextSimplificationResponse(
            original_text=request.text,
            simplified_text=simplified,
            reading_level=request.reading_level,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text simplification failed: {str(e)}")

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing"""
    try:
        # Validate file type
        allowed_types = [".pdf", ".txt", ".docx", ".doc"]
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Allowed types: {allowed_types}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        # Basic file info
        file_size = len(content)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_type": file_extension,
            "status": "uploaded",
            "message": "File uploaded successfully. Use /api/process/{file_id} to extract text."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/api/process/{file_id}")
async def process_document(file_id: str):
    """Process uploaded document and extract text"""
    try:
        # Find the file
        import glob
        file_pattern = os.path.join(upload_dir, f"{file_id}_*")
        matching_files = glob.glob(file_pattern)
        
        if not matching_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = matching_files[0]
        filename = os.path.basename(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Extract text based on file type
        if file_extension == ".txt":
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                text = await f.read()
        else:
            # For other file types, return a mock extraction message
            text = f"[MOCK EXTRACTION] This is extracted text from {filename}. In a real implementation, this would use PDF/Word extraction libraries."
        
        return {
            "file_id": file_id,
            "filename": filename,
            "extracted_text": text,
            "text_length": len(text),
            "status": "processed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_clean:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )