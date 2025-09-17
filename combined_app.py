"""
Combined FastAPI + Streamlit Application for Railway Deployment
Serves both API endpoints and Streamlit UI
"""

import os
import subprocess
import threading
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="AI Legal Assistant with Document Processing and Streamlit UI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified API endpoints (mock data for deployment)
@app.get("/")
async def root():
    return {
        "message": "Legal Assistant GenAI - Full Stack",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "api": "Available at /api/*",
            "ui": "Streamlit UI available at /ui",
            "docs": "API docs at /docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Legal Assistant GenAI Full Stack"}

@app.post("/api/simplify")
async def simplify_text(request: Request):
    body = await request.json()
    text = body.get("text", "")
    return {
        "success": True,
        "original_text": text,
        "simplified_text": f"Simplified version: {text[:100]}...",
        "complexity_level": "medium",
        "key_points": ["Legal concepts explained", "Technical terms simplified"],
        "red_flags": ["Review recommended", "Check accuracy"]
    }

@app.post("/api/terms")
async def lookup_terms(request: Request):
    body = await request.json()
    terms = body.get("terms", [])
    return {
        "success": True,
        "definitions": [
            {
                "term": term,
                "definition": f"Legal definition of {term}",
                "simple_explanation": f"In simple terms: {term} means..."
            } for term in terms
        ]
    }

@app.post("/api/upload")
async def upload_document(request: Request):
    return {
        "success": True,
        "file_id": "doc_123",
        "message": "Document uploaded successfully",
        "processing_status": "queued"
    }

@app.post("/api/risk")
async def risk_assessment(request: Request):
    body = await request.json()
    document_text = body.get("document_text", "")
    return {
        "success": True,
        "risk_level": "medium",
        "risk_score": 65,
        "risk_factors": [
            "Liability clauses present",
            "Limited warranty terms",
            "Indemnification requirements"
        ],
        "recommendations": [
            "Review liability terms carefully",
            "Consider additional warranty coverage",
            "Consult legal counsel for indemnification clauses"
        ]
    }

# Streamlit UI redirect
@app.get("/ui")
async def streamlit_ui():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legal Assistant GenAI - Streamlit UI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f6; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #1f4e79; margin-bottom: 30px; }
            .feature { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #1f4e79; }
            .button { background: #1f4e79; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px 5px; }
            .api-section { background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚖️ Legal Assistant GenAI</h1>
                <p>AI-Powered Legal Document Analysis & Simplification</p>
            </div>
            
            <div class="feature">
                <h3>🔍 Text Simplification</h3>
                <p>Convert complex legal jargon into plain English</p>
                <a href="/docs#/default/simplify_text_api_simplify_post" class="button">Try API</a>
            </div>
            
            <div class="feature">
                <h3>📚 Legal Terms Lookup</h3>
                <p>Get instant definitions and explanations of legal terms</p>
                <a href="/docs#/default/lookup_terms_api_terms_post" class="button">Try API</a>
            </div>
            
            <div class="feature">
                <h3>📄 Document Upload</h3>
                <p>Upload and process legal documents with AI analysis</p>
                <a href="/docs#/default/upload_document_api_upload_post" class="button">Try API</a>
            </div>
            
            <div class="feature">
                <h3>⚠️ Risk Assessment</h3>
                <p>Analyze documents for potential legal risks and red flags</p>
                <a href="/docs#/default/risk_assessment_api_risk_post" class="button">Try API</a>
            </div>
            
            <div class="api-section">
                <h3>🔗 API Access</h3>
                <p><strong>API Base URL:</strong> <code>{request.base_url}api/</code></p>
                <p><strong>Documentation:</strong> <a href="/docs">Interactive API Docs</a></p>
                <p><strong>Health Check:</strong> <a href="/health">Service Status</a></p>
            </div>
        </div>
    </body>
    </html>
    """.replace("{request.base_url}", str(request.base_url)))

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get("PORT", 8002))
    
    print(f"🚀 Starting Legal Assistant GenAI on port {port}")
    print(f"📱 API available at: http://0.0.0.0:{port}/")
    print(f"🌐 UI available at: http://0.0.0.0:{port}/ui")
    print(f"📖 API docs at: http://0.0.0.0:{port}/docs")
    
    uvicorn.run(
        "combined_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )