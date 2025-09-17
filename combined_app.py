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

# Interactive Web UI
@app.get("/ui")
async def interactive_ui(request: Request):
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legal Assistant GenAI - Interactive UI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; margin-bottom: 40px; padding: 40px 0; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; }
            .feature-panel { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            .feature-panel h3 { color: #4a5568; margin-bottom: 20px; font-size: 1.5em; }
            .input-group { margin-bottom: 20px; }
            .input-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #2d3748; }
            .input-group textarea, .input-group input { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
            .input-group textarea:focus, .input-group input:focus { outline: none; border-color: #667eea; }
            .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: transform 0.2s; }
            .btn:hover { transform: translateY(-2px); }
            .result-box { margin-top: 20px; padding: 15px; background: #f7fafc; border-radius: 8px; border-left: 4px solid #667eea; }
            .api-links { text-align: center; margin-top: 30px; }
            .api-links a { color: white; text-decoration: none; margin: 0 15px; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 25px; transition: background 0.3s; }
            .api-links a:hover { background: rgba(255,255,255,0.3); }
            @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚖️ Legal Assistant GenAI</h1>
                <p>AI-Powered Legal Document Analysis & Simplification</p>
            </div>
            
            <div class="main-content">
                <div class="feature-panel">
                    <h3>🔍 Text Simplification</h3>
                    <div class="input-group">
                        <label>Legal Text to Simplify:</label>
                        <textarea id="simplifyText" rows="4" placeholder="Enter complex legal text here..."></textarea>
                    </div>
                    <button class="btn" onclick="simplifyText()">Simplify Text</button>
                    <div id="simplifyResult" class="result-box" style="display:none;"></div>
                </div>
                
                <div class="feature-panel">
                    <h3>📚 Legal Terms Lookup</h3>
                    <div class="input-group">
                        <label>Legal Terms (comma-separated):</label>
                        <input id="termsInput" type="text" placeholder="liability, indemnification, warranty">
                    </div>
                    <button class="btn" onclick="lookupTerms()">Lookup Terms</button>
                    <div id="termsResult" class="result-box" style="display:none;"></div>
                </div>
                
                <div class="feature-panel">
                    <h3>⚠️ Risk Assessment</h3>
                    <div class="input-group">
                        <label>Document Text for Risk Analysis:</label>
                        <textarea id="riskText" rows="4" placeholder="Enter document text to analyze for risks..."></textarea>
                    </div>
                    <button class="btn" onclick="assessRisk()">Assess Risk</button>
                    <div id="riskResult" class="result-box" style="display:none;"></div>
                </div>
                
                <div class="feature-panel">
                    <h3>📄 Document Upload</h3>
                    <div class="input-group">
                        <label>Upload Document:</label>
                        <input id="fileInput" type="file" accept=".pdf,.doc,.docx,.txt">
                    </div>
                    <button class="btn" onclick="uploadDocument()">Upload Document</button>
                    <div id="uploadResult" class="result-box" style="display:none;"></div>
                </div>
            </div>
            
            <div class="api-links">
                <a href="/docs" target="_blank">📖 API Documentation</a>
                <a href="/health" target="_blank">🏥 Health Check</a>
                <a href="/" target="_blank">🏠 API Info</a>
            </div>
        </div>
        
        <script>
            const API_BASE = window.location.origin;
            
            async function simplifyText() {
                const text = document.getElementById('simplifyText').value;
                if (!text.trim()) return alert('Please enter some text to simplify');
                
                try {
                    const response = await fetch(`${API_BASE}/api/simplify`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const result = await response.json();
                    document.getElementById('simplifyResult').style.display = 'block';
                    document.getElementById('simplifyResult').innerHTML = `
                        <h4>Simplified Text:</h4>
                        <p><strong>Original:</strong> ${result.original_text}</p>
                        <p><strong>Simplified:</strong> ${result.simplified_text}</p>
                        <p><strong>Complexity Level:</strong> ${result.complexity_level}</p>
                        <p><strong>Key Points:</strong> ${result.key_points.join(', ')}</p>
                        <p><strong>Red Flags:</strong> ${result.red_flags.join(', ')}</p>
                    `;
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function lookupTerms() {
                const terms = document.getElementById('termsInput').value.split(',').map(t => t.trim());
                if (!terms.length || !terms[0]) return alert('Please enter some terms to lookup');
                
                try {
                    const response = await fetch(`${API_BASE}/api/terms`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ terms: terms })
                    });
                    const result = await response.json();
                    document.getElementById('termsResult').style.display = 'block';
                    document.getElementById('termsResult').innerHTML = `
                        <h4>Term Definitions:</h4>
                        ${result.definitions.map(def => `
                            <div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px;">
                                <strong>${def.term}:</strong><br>
                                <em>Definition:</em> ${def.definition}<br>
                                <em>Simple explanation:</em> ${def.simple_explanation}
                            </div>
                        `).join('')}
                    `;
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function assessRisk() {
                const text = document.getElementById('riskText').value;
                if (!text.trim()) return alert('Please enter document text for risk assessment');
                
                try {
                    const response = await fetch(`${API_BASE}/api/risk`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ document_text: text })
                    });
                    const result = await response.json();
                    document.getElementById('riskResult').style.display = 'block';
                    document.getElementById('riskResult').innerHTML = `
                        <h4>Risk Assessment:</h4>
                        <p><strong>Risk Level:</strong> <span style="color: ${result.risk_level === 'high' ? 'red' : result.risk_level === 'medium' ? 'orange' : 'green'}">${result.risk_level.toUpperCase()}</span></p>
                        <p><strong>Risk Score:</strong> ${result.risk_score}/100</p>
                        <p><strong>Risk Factors:</strong></p>
                        <ul>${result.risk_factors.map(factor => `<li>${factor}</li>`).join('')}</ul>
                        <p><strong>Recommendations:</strong></p>
                        <ul>${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                    `;
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function uploadDocument() {
                const fileInput = document.getElementById('fileInput');
                if (!fileInput.files[0]) return alert('Please select a file to upload');
                
                try {
                    const response = await fetch(`${API_BASE}/api/upload`, {
                        method: 'POST'
                    });
                    const result = await response.json();
                    document.getElementById('uploadResult').style.display = 'block';
                    document.getElementById('uploadResult').innerHTML = `
                        <h4>Upload Status:</h4>
                        <p><strong>Status:</strong> ${result.success ? 'Success' : 'Failed'}</p>
                        <p><strong>File ID:</strong> ${result.file_id}</p>
                        <p><strong>Message:</strong> ${result.message}</p>
                        <p><strong>Processing Status:</strong> ${result.processing_status}</p>
                    `;
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """)

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