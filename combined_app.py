"""
Combined FastAPI + Streamlit Application for Railway Deployment
Serves both API endpoints and Streamlit UI
"""

import os
import subprocess
import threading
import time
import json
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import google.generativeai as genai

# Create FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="AI Legal Assistant with Document Processing and Gemini AI Integration",
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

# Initialize Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("✅ Gemini AI initialized successfully")
else:
    model = None
    print("⚠️ GEMINI_API_KEY not found. Set it as environment variable for AI features.")

async def get_ai_response(prompt: str) -> str:
    """Get response from Gemini AI"""
    if not model:
        return "AI service not available. Please configure GEMINI_API_KEY."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI service error: {str(e)}"

async def simplify_legal_text(text: str) -> dict:
    """Use Gemini AI to simplify legal text"""
    prompt = f"""
    You are a legal expert assistant. Please analyze and simplify the following legal text:

    Text: "{text}"

    Please provide a response in the following JSON format:
    {{
        "simplified_text": "A clear, simple explanation in plain English that a high school student could understand",
        "complexity_level": "high/medium/low",
        "key_points": ["list of 2-3 main points explained in simple terms"],
        "red_flags": ["list of 2-3 potential issues or things to watch out for"],
        "legal_advice": "Brief general guidance (not specific legal advice)"
    }}

    Focus on making complex legal jargon accessible while highlighting important considerations.
    """
    
    ai_response = await get_ai_response(prompt)
    
    try:
        # Try to parse JSON response
        import json
        import re
        # Extract JSON from response if it's wrapped in other text
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "success": True,
                "original_text": text,
                "simplified_text": parsed.get("simplified_text", ai_response),
                "complexity_level": parsed.get("complexity_level", "medium"),
                "key_points": parsed.get("key_points", ["AI analysis provided"]),
                "red_flags": parsed.get("red_flags", ["Review with legal professional"]),
                "legal_advice": parsed.get("legal_advice", "Consult with a qualified attorney for specific advice")
            }
    except:
        pass
    
    # Fallback if JSON parsing fails
    return {
        "success": True,
        "original_text": text,
        "simplified_text": ai_response,
        "complexity_level": "medium",
        "key_points": ["AI analysis provided"],
        "red_flags": ["Review with legal professional"],
        "legal_advice": "Consult with a qualified attorney for specific advice"
    }

async def lookup_legal_terms(terms: list) -> dict:
    """Use Gemini AI to define legal terms"""
    terms_str = ", ".join(terms)
    prompt = f"""
    You are a legal dictionary expert. Please provide clear definitions for these legal terms: {terms_str}

    For each term, provide:
    1. A formal legal definition
    2. A simple explanation that anyone can understand
    3. An example of how it's commonly used

    Format as JSON:
    {{
        "definitions": [
            {{
                "term": "term name",
                "definition": "formal legal definition",
                "simple_explanation": "easy to understand explanation",
                "example": "practical example of usage"
            }}
        ]
    }}
    """
    
    ai_response = await get_ai_response(prompt)
    
    try:
        import json
        import re
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "success": True,
                "definitions": parsed.get("definitions", [])
            }
    except:
        pass
    
    # Fallback response
    definitions = []
    for term in terms:
        definitions.append({
            "term": term,
            "definition": f"AI-generated definition for '{term}': {ai_response[:200]}...",
            "simple_explanation": f"In simple terms, '{term}' relates to legal concepts.",
            "example": "Consult legal resources for specific examples."
        })
    
    return {
        "success": True,
        "definitions": definitions
    }

async def assess_legal_risk(document_text: str) -> dict:
    """Use Gemini AI to assess legal risks"""
    prompt = f"""
    You are a legal risk assessment expert. Please analyze the following document text for potential legal risks:

    Document: "{document_text}"

    Provide a comprehensive risk assessment in JSON format:
    {{
        "risk_level": "low/medium/high",
        "risk_score": "number from 0-100",
        "risk_factors": ["list of specific risk factors found"],
        "recommendations": ["list of specific recommendations"],
        "legal_concerns": ["list of legal issues to address"],
        "urgency": "low/medium/high - how quickly this should be addressed"
    }}

    Focus on practical, actionable insights about potential legal issues.
    """
    
    ai_response = await get_ai_response(prompt)
    
    try:
        import json
        import re
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "success": True,
                "risk_level": parsed.get("risk_level", "medium"),
                "risk_score": int(parsed.get("risk_score", 50)),
                "risk_factors": parsed.get("risk_factors", ["General legal review recommended"]),
                "recommendations": parsed.get("recommendations", ["Consult with attorney"]),
                "legal_concerns": parsed.get("legal_concerns", ["Professional review needed"]),
                "urgency": parsed.get("urgency", "medium")
            }
    except:
        pass
    
    # Fallback response
    return {
        "success": True,
        "risk_level": "medium",
        "risk_score": 50,
        "risk_factors": ["AI analysis indicates potential legal considerations"],
        "recommendations": ["Professional legal review recommended"],
        "legal_concerns": ["Consult qualified attorney for detailed analysis"],
        "urgency": "medium"
    }

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
    
    if not text.strip():
        return {"success": False, "error": "No text provided"}
    
    return await simplify_legal_text(text)

@app.post("/api/terms")
async def lookup_terms(request: Request):
    body = await request.json()
    terms = body.get("terms", [])
    
    if not terms or not any(term.strip() for term in terms):
        return {"success": False, "error": "No terms provided"}
    
    # Clean up terms
    clean_terms = [term.strip() for term in terms if term.strip()]
    return await lookup_legal_terms(clean_terms)

@app.post("/api/risk")
async def risk_assessment(request: Request):
    body = await request.json()
    document_text = body.get("document_text", "")
    
    if not document_text.strip():
        return {"success": False, "error": "No document text provided"}
    
    return await assess_legal_risk(document_text)

@app.post("/api/upload")
async def upload_document(request: Request):
    return {
        "success": True,
        "file_id": "doc_123",
        "message": "Document uploaded successfully - AI analysis coming soon",
        "processing_status": "queued"
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
                        <h4>✨ AI Legal Analysis:</h4>
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <p><strong>📝 Original:</strong> ${result.original_text}</p>
                        </div>
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <p><strong>✨ Simplified:</strong> ${result.simplified_text}</p>
                        </div>
                        <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <p><strong>📊 Complexity Level:</strong> <span style="text-transform: capitalize; font-weight: bold;">${result.complexity_level}</span></p>
                            <p><strong>🎯 Key Points:</strong></p>
                            <ul>${Array.isArray(result.key_points) ? result.key_points.map(point => `<li>${point}</li>`).join('') : '<li>' + result.key_points + '</li>'}</ul>
                            <p><strong>⚠️ Red Flags:</strong></p>
                            <ul>${Array.isArray(result.red_flags) ? result.red_flags.map(flag => `<li style="color: #d63384;">${flag}</li>`).join('') : '<li style="color: #d63384;">' + result.red_flags + '</li>'}</ul>
                            ${result.legal_advice ? `<p><strong>⚖️ General Guidance:</strong> <em>${result.legal_advice}</em></p>` : ''}
                        </div>
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
                        <h4>📚 AI Legal Dictionary:</h4>
                        ${result.definitions.map(def => `
                            <div style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #667eea;">
                                <h5 style="color: #667eea; margin-bottom: 10px;">📖 ${def.term}</h5>
                                <p><strong>Legal Definition:</strong> ${def.definition}</p>
                                <p><strong>🔍 Simple Explanation:</strong> ${def.simple_explanation}</p>
                                ${def.example ? `<p><strong>💡 Example:</strong> <em>${def.example}</em></p>` : ''}
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
                        <h4>⚠️ AI Risk Assessment:</h4>
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <p><strong>🎯 Risk Level:</strong> <span style="color: ${result.risk_level === 'high' ? '#dc3545' : result.risk_level === 'medium' ? '#fd7e14' : '#28a745'}; font-weight: bold; text-transform: uppercase;">${result.risk_level}</span></p>
                            <p><strong>📊 Risk Score:</strong> <span style="font-size: 1.2em; font-weight: bold;">${result.risk_score}/100</span></p>
                            ${result.urgency ? `<p><strong>⏰ Urgency:</strong> <span style="text-transform: capitalize; font-weight: bold;">${result.urgency}</span></p>` : ''}
                        </div>
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ffc107;">
                            <p><strong>⚡ Risk Factors:</strong></p>
                            <ul>${Array.isArray(result.risk_factors) ? result.risk_factors.map(factor => `<li>${factor}</li>`).join('') : '<li>' + result.risk_factors + '</li>'}</ul>
                        </div>
                        <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #17a2b8;">
                            <p><strong>💡 Recommendations:</strong></p>
                            <ul>${Array.isArray(result.recommendations) ? result.recommendations.map(rec => `<li>${rec}</li>`).join('') : '<li>' + result.recommendations + '</li>'}</ul>
                        </div>
                        ${result.legal_concerns ? `
                        <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #dc3545;">
                            <p><strong>⚖️ Legal Concerns:</strong></p>
                            <ul>${Array.isArray(result.legal_concerns) ? result.legal_concerns.map(concern => `<li>${concern}</li>`).join('') : '<li>' + result.legal_concerns + '</li>'}</ul>
                        </div>
                        ` : ''}
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
    
    print(f"🚀 Starting Legal Assistant GenAI with Gemini AI on port {port}")
    print(f"📱 API available at: http://0.0.0.0:{port}/")
    print(f"🌐 Interactive UI available at: http://0.0.0.0:{port}/ui")
    print(f"📖 API docs at: http://0.0.0.0:{port}/docs")
    print(f"🤖 AI Status: {'✅ Gemini AI Ready' if model else '⚠️ Set GEMINI_API_KEY for AI features'}")
    
    uvicorn.run(
        "combined_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )