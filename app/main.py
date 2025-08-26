"""
Legal Assistant - GenAI
A focused AI solution for demystifying and simplifying complex legal documents.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings

app = FastAPI(
    title="Legal Document Demystification AI",
    description="Transform complex legal documents into clear, accessible guidance",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def read_root(request: Request):
    """Main page for the legal document demystification tool."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Legal Document Demystification AI"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "legal-assistant-genai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )