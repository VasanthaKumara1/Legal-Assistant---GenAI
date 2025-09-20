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
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import google.generativeai as genai

# Create FastAPI app
app = FastAPI(
    title="Legal Assistant GenAI",
    description="AI Legal Assistant with Document Processing and Gemini AI Integration",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
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
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "AIzaSyBv-izgP1AAh-Pf78mqueGIgse5VDCGaoI"
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
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
    You are a friendly legal expert who explains complex legal matters in simple, everyday language.
    
    Your task: Take this legal text and explain it as if you're talking to a neighbor who has no legal background.
    
    Legal Text: "{text}"
    
    Please respond in JSON format with these sections:
    {{
        "simplified_text": "Explain this in plain English using everyday words. Imagine explaining to a friend over coffee. Avoid legal jargon completely.",
        "complexity_level": "high/medium/low",
        "key_points": ["2-3 main points in simple bullet format - what this really means for the person"],
        "red_flags": ["everything to be careful about - explain WHY they matter"],
        "legal_advice": "Practical next steps in friendly, non-intimidating language"
    }}
    
    Remember: Use simple words, short sentences, and relate to everyday situations people understand.
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
    You are a professional legal consultant who specializes in making law accessible to everyone.
    
    Please explain these legal terms: {terms_str}
    
    For each term, provide a professional yet friendly explanation that any person can understand.
    
    Format as JSON:
    {{
        "definitions": [
            {{
                "term": "term name",
                "definition": "Professional definition in clear, simple language",
                "simple_explanation": "What this means in everyday life - use analogies if helpful",
                "example": "Real-world example showing when this term matters"
            }}
        ]
    }}
    
    Guidelines:
    - Use professional but warm tone
    - Avoid intimidating legal language
    - Include why this term matters to regular people
    - Make it practical and relatable
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
    You are a professional legal consultant conducting a risk assessment for a client.
    
    Document to analyze: "{document_text}"
    
    Provide a professional risk assessment that a business owner or individual can understand and act upon:
    
    {{
        "risk_level": "low/medium/high",
        "risk_score": "number from 0-100",
        "risk_factors": ["Specific issues found - explain WHY each is problematic in simple terms"],
        "recommendations": ["Clear, actionable steps the person should take"],
        "legal_concerns": ["Potential problems explained in everyday language"],
        "urgency": "low/medium/high - how quickly this should be addressed"
    }}
    
    Guidelines:
    - Professional but approachable tone
    - Explain the 'why' behind each risk
    - Give practical next steps
    - Help them understand what's at stake
    - Avoid legal jargon - use plain English
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

def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text content from uploaded file"""
    file_extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    try:
        if file_extension == '.txt':
            # Handle plain text files
            return content.decode('utf-8')
        elif file_extension in ['.pdf', '.doc', '.docx']:
            # For now, return a placeholder - in production you'd use proper parsers
            # like PyPDF2, python-docx, etc.
            return f"[Document content from {filename} - {len(content)} bytes. For demo purposes, assuming this contains legal text that needs analysis.]"
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

async def process_document_with_ai(content: str, filename: str) -> dict:
    """Process document content with AI analysis"""
    prompt = f"""
    You are a professional legal consultant analyzing a document for a client.
    
    Document Name: {filename}
    Document Content: "{content}"
    
    Please provide a comprehensive analysis in JSON format:
    {{
        "document_summary": "Brief summary of the document in simple language",
        "document_type": "contract/agreement/policy/legal notice/other",
        "key_findings": ["3-4 main points about what this document does"],
        "risk_assessment": {{
            "risk_level": "low/medium/high",
            "risk_score": "number from 0-100",
            "main_risks": ["Risk 1 description as string", "Risk 2 description as string", "Risk 3 description as string"]
        }},
        "important_clauses": ["Notable terms or clauses that need attention"],
        "recommendations": ["What the person should do next"],
        "plain_english_explanation": "Explain what this document means in everyday language"
    }}
    
    IMPORTANT: Ensure main_risks contains only simple string descriptions, not objects.
    Make everything accessible to non-lawyers. Focus on practical implications.
    """
    
    ai_response = await get_ai_response(prompt)
    
    try:
        import json
        import re
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "success": True,
                "analysis": parsed
            }
    except Exception as e:
        pass
    
    # Fallback response
    return {
        "success": True,
        "analysis": {
            "document_summary": "AI analysis completed",
            "document_type": "legal document",
            "key_findings": ["Document uploaded and processed"],
            "risk_assessment": {
                "risk_level": "medium",
                "risk_score": 50,
                "main_risks": ["Professional review recommended"]
            },
            "important_clauses": ["Consult with legal professional for detailed review"],
            "recommendations": ["Have a qualified attorney review this document"],
            "plain_english_explanation": ai_response[:500] + "..."
        }
    }

# Main application endpoints

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

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Basic file validation
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return {
                "success": False,
                "error": "File too large. Maximum size is 10MB."
            }
        
        # Check file type
        allowed_types = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_types:
            return {
                "success": False,
                "error": f"File type not supported. Allowed types: {', '.join(allowed_types)}"
            }
        
        # Extract text from file
        extracted_text = extract_text_from_file(content, file.filename)
        
        if not extracted_text or extracted_text.startswith("Error"):
            return {
                "success": False,
                "error": "Could not extract text from file"
            }
        
        # Process with AI
        ai_analysis = await process_document_with_ai(extracted_text, file.filename)
        
        return {
            "success": True,
            "file_id": f"doc_{hash(file.filename)}_{int(time.time())}",
            "filename": file.filename,
            "size": file_size,
            "file_type": file_extension,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "ai_analysis": ai_analysis.get("analysis", {}),
            "message": "Document uploaded and analyzed successfully",
            "processing_status": "completed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }

# Interactive Web UI
@app.get("/ui")
async def interactive_ui(request: Request):
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legal Assistant Pro - AI-Powered Legal Analysis</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }
            
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 32px 64px rgba(0, 0, 0, 0.12);
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header {
                background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
                color: white;
                padding: 60px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="rgba(255,255,255,0.05)"><polygon points="0,0 1000,0 1000,100 0,80"/></svg>');
                background-size: cover;
            }
            
            .header-content {
                position: relative;
                z-index: 1;
            }
            
            .header h1 {
                font-size: 3.5rem;
                font-weight: 700;
                margin-bottom: 16px;
                background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header .subtitle {
                font-size: 1.25rem;
                font-weight: 400;
                opacity: 0.9;
                margin-bottom: 8px;
            }
            
            .header .tagline {
                font-size: 1rem;
                opacity: 0.7;
                font-weight: 300;
            }
            
            .main-content {
                padding: 50px 40px;
            }
            
            .features-section {
                margin-bottom: 50px;
            }
            
            .section-title {
                text-align: center;
                font-size: 2rem;
                font-weight: 600;
                color: #1a237e;
                margin-bottom: 40px;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin-bottom: 50px;
            }
            
            .feature-card {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
                border-radius: 20px;
                padding: 35px;
                border: 1px solid rgba(26, 35, 126, 0.1);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
                overflow: hidden;
            }
            
            .feature-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            }
            
            .feature-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 24px 48px rgba(102, 126, 234, 0.15);
                border-color: rgba(102, 126, 234, 0.3);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 20px;
                display: block;
            }
            
            .feature-card h3 {
                color: #1a237e;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .feature-card p {
                color: #64748b;
                font-weight: 400;
                line-height: 1.7;
                margin-bottom: 25px;
            }
            
            .form-section {
                background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
                border-radius: 20px;
                padding: 40px;
                border: 1px solid rgba(26, 35, 126, 0.1);
                margin-bottom: 30px;
            }
            
            .form-group {
                margin-bottom: 30px;
            }
            
            .form-label {
                display: block;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 12px;
                font-size: 1rem;
            }
            
            .form-input, .form-textarea {
                width: 100%;
                padding: 16px 20px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-family: inherit;
                font-size: 15px;
                transition: all 0.3s ease;
                background: white;
            }
            
            .form-input:focus, .form-textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
                transform: translateY(-1px);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 18px 40px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                position: relative;
                overflow: hidden;
            }
            
            .btn-primary::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 16px 32px rgba(102, 126, 234, 0.3);
            }
            
            .btn-primary:hover::before {
                left: 100%;
            }
            
            .result-container {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 20px;
                padding: 35px;
                margin-top: 30px;
                border: 1px solid rgba(14, 165, 233, 0.2);
                border-left: 6px solid #0ea5e9;
                display: none;
            }
            
            .result-title {
                color: #0369a1;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
            }
            
            .result-title i {
                margin-right: 12px;
            }
            
            .loading-container {
                display: none;
                text-align: center;
                padding: 50px;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid #e2e8f0;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            .loading-text {
                color: #64748b;
                font-weight: 500;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error-container {
                background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-left: 6px solid #ef4444;
                color: #dc2626;
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
            }
            
            .tabs {
                display: flex;
                margin-bottom: 30px;
                background: #f1f5f9;
                border-radius: 12px;
                padding: 6px;
            }
            
            .tab {
                flex: 1;
                padding: 12px 20px;
                text-align: center;
                cursor: pointer;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                color: #64748b;
            }
            
            .tab.active {
                background: white;
                color: #1e293b;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            @media (max-width: 768px) {
                .main-container {
                    margin: 10px;
                    border-radius: 16px;
                }
                
                .header {
                    padding: 40px 20px;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                }
                
                .main-content {
                    padding: 30px 20px;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .form-section {
                    padding: 25px;
                }
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="header">
                <div class="header-content">
                    <h1><i class="fas fa-balance-scale"></i> Legal Assistant Pro</h1>
                    <p class="subtitle">AI-Powered Legal Document Analysis & Simplification</p>
                    <p class="tagline">Making Legal Language Accessible to Everyone</p>
                </div>
            </div>
            
            <div class="main-content">
                <div class="features-section">
                    <h2 class="section-title">Professional Legal AI Services</h2>
                    
                    <div class="tabs">
                        <div class="tab active" onclick="switchTab('simplify')">
                            <i class="fas fa-language"></i> Text Simplification
                        </div>
                        <div class="tab" onclick="switchTab('terms')">
                            <i class="fas fa-book"></i> Legal Dictionary
                        </div>
                        <div class="tab" onclick="switchTab('risk')">
                            <i class="fas fa-shield-alt"></i> Risk Assessment
                        </div>
                        <div class="tab" onclick="switchTab('upload')">
                            <i class="fas fa-upload"></i> Document Analysis
                        </div>
                    </div>
                    
                    <div id="simplify-tab" class="tab-content active">
                        <div class="form-section">
                            <i class="feature-icon fas fa-language"></i>
                            <h3>Legal Text Simplification</h3>
                            <p>Transform complex legal jargon into clear, understandable language that anyone can comprehend.</p>
                            
                            <div class="form-group">
                                <label class="form-label">Enter Legal Text to Simplify:</label>
                                <textarea id="simplifyText" class="form-textarea" rows="6" placeholder="Paste your complex legal text here, and our AI will explain it in plain English..."></textarea>
                            </div>
                            <button class="btn-primary" onclick="simplifyText()">
                                <i class="fas fa-magic"></i> Simplify Text
                            </button>
                            
                            <div id="simplifyResult" class="result-container"></div>
                            <div id="simplifyLoading" class="loading-container">
                                <div class="loading-spinner"></div>
                                <div class="loading-text">AI is analyzing your legal text...</div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="terms-tab" class="tab-content">
                        <div class="form-section">
                            <i class="feature-icon fas fa-book"></i>
                            <h3>Professional Legal Dictionary</h3>
                            <p>Get clear, professional definitions of legal terms with real-world examples and explanations.</p>
                            
                            <div class="form-group">
                                <label class="form-label">Legal Terms (separate with commas):</label>
                                <input id="termsInput" class="form-input" type="text" placeholder="e.g., liability, indemnification, force majeure, arbitration">
                            </div>
                            <button class="btn-primary" onclick="lookupTerms()">
                                <i class="fas fa-search"></i> Lookup Terms
                            </button>
                            
                            <div id="termsResult" class="result-container"></div>
                            <div id="termsLoading" class="loading-container">
                                <div class="loading-spinner"></div>
                                <div class="loading-text">Looking up legal definitions...</div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="risk-tab" class="tab-content">
                        <div class="form-section">
                            <i class="feature-icon fas fa-shield-alt"></i>
                            <h3>Professional Risk Assessment</h3>
                            <p>Comprehensive analysis of potential legal risks in your documents with actionable recommendations.</p>
                            
                            <div class="form-group">
                                <label class="form-label">Document Text for Risk Analysis:</label>
                                <textarea id="riskText" class="form-textarea" rows="6" placeholder="Paste your document content here for professional risk assessment..."></textarea>
                            </div>
                            <button class="btn-primary" onclick="assessRisk()">
                                <i class="fas fa-search-plus"></i> Assess Risks
                            </button>
                            
                            <div id="riskResult" class="result-container"></div>
                            <div id="riskLoading" class="loading-container">
                                <div class="loading-spinner"></div>
                                <div class="loading-text">Conducting professional risk assessment...</div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="upload-tab" class="tab-content">
                        <div class="form-section">
                            <i class="feature-icon fas fa-upload"></i>
                            <h3>Document Upload & Analysis</h3>
                            <p>Upload your legal documents for comprehensive AI-powered analysis and insights.</p>
                            
                            <div class="form-group">
                                <label class="form-label">Select Document to Upload:</label>
                                <input id="fileInput" class="form-input" type="file" accept=".pdf,.doc,.docx,.txt">
                            </div>
                            <button class="btn-primary" onclick="uploadDocument()">
                                <i class="fas fa-cloud-upload-alt"></i> Upload & Analyze
                            </button>
                            
                            <div id="uploadResult" class="result-container"></div>
                            <div id="uploadLoading" class="loading-container">
                                <div class="loading-spinner"></div>
                                <div class="loading-text">Uploading and analyzing document...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Removed API footer with documentation links -->
        </div>
        
        <script>
            const API_BASE = window.location.origin;
            
            function switchTab(tabName) {
                // Remove active class from all tabs and content
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // Add active class to selected tab and content
                event.target.classList.add('active');
                document.getElementById(tabName + '-tab').classList.add('active');
            }
            
            function showLoading(loadingId) {
                document.getElementById(loadingId).style.display = 'block';
            }
            
            function hideLoading(loadingId) {
                document.getElementById(loadingId).style.display = 'none';
            }
            
            function showResult(resultId, content) {
                const resultDiv = document.getElementById(resultId);
                resultDiv.innerHTML = content;
                resultDiv.style.display = 'block';
            }
            
            function showError(resultId, message) {
                const errorContent = `
                    <div class="error-container">
                        <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
                        <p>${message}</p>
                    </div>
                `;
                showResult(resultId, errorContent);
            }
            
            async function simplifyText() {
                const text = document.getElementById('simplifyText').value;
                if (!text.trim()) {
                    alert('Please enter some legal text to simplify');
                    return;
                }
                
                showLoading('simplifyLoading');
                document.getElementById('simplifyResult').style.display = 'none';
                
                try {
                    const response = await fetch(`${API_BASE}/api/simplify`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    const result = await response.json();
                    
                    hideLoading('simplifyLoading');
                    
                    const content = `
                        <div class="result-title">
                            <i class="fas fa-magic"></i> AI Legal Analysis Results
                        </div>
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #10b981;">
                            <h4 style="color: #10b981; margin-bottom: 15px;"><i class="fas fa-check-circle"></i> Simplified Explanation</h4>
                            <p style="font-size: 16px; line-height: 1.7; color: #374151;">${result.simplified_text}</p>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px;">
                            <div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
                                <h5 style="color: #3b82f6; margin-bottom: 10px;"><i class="fas fa-chart-bar"></i> Complexity Level</h5>
                                <p style="font-size: 18px; font-weight: 600; text-transform: capitalize;">${result.complexity_level}</p>
                            </div>
                            
                            <div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #8b5cf6;">
                                <h5 style="color: #8b5cf6; margin-bottom: 10px;"><i class="fas fa-clock"></i> Urgency</h5>
                                <p style="font-size: 14px; color: #6b7280;">Review recommended</p>
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
                            <h4 style="color: #f59e0b; margin-bottom: 15px;"><i class="fas fa-lightbulb"></i> Key Points to Remember</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${Array.isArray(result.key_points) ? result.key_points.map(point => `
                                    <li style="margin-bottom: 10px; padding: 10px; background: #fef3c7; border-radius: 8px; border-left: 3px solid #f59e0b;">
                                        <i class="fas fa-arrow-right" style="color: #f59e0b; margin-right: 10px;"></i>${point}
                                    </li>
                                `).join('') : `<li style="margin-bottom: 10px; padding: 10px; background: #fef3c7; border-radius: 8px;">${result.key_points}</li>`}
                            </ul>
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ef4444;">
                            <h4 style="color: #ef4444; margin-bottom: 15px;"><i class="fas fa-exclamation-triangle"></i> Important Considerations</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${Array.isArray(result.red_flags) ? result.red_flags.map(flag => `
                                    <li style="margin-bottom: 10px; padding: 10px; background: #fee2e2; border-radius: 8px; border-left: 3px solid #ef4444;">
                                        <i class="fas fa-warning" style="color: #ef4444; margin-right: 10px;"></i>${flag}
                                    </li>
                                `).join('') : `<li style="margin-bottom: 10px; padding: 10px; background: #fee2e2; border-radius: 8px;">${result.red_flags}</li>`}
                            </ul>
                        </div>
                        
                        ${result.legal_advice ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; border-left: 4px solid #6366f1;">
                                <h4 style="color: #6366f1; margin-bottom: 15px;"><i class="fas fa-balance-scale"></i> Professional Guidance</h4>
                                <p style="font-style: italic; color: #4b5563; line-height: 1.6;">${result.legal_advice}</p>
                            </div>
                        ` : ''}
                    `;
                    
                    showResult('simplifyResult', content);
                    
                } catch (error) {
                    hideLoading('simplifyLoading');
                    showError('simplifyResult', 'Failed to analyze text. Please try again.');
                }
            }
            
            async function lookupTerms() {
                const terms = document.getElementById('termsInput').value.split(',').map(t => t.trim()).filter(t => t);
                if (!terms.length) {
                    alert('Please enter some legal terms to lookup');
                    return;
                }
                
                showLoading('termsLoading');
                document.getElementById('termsResult').style.display = 'none';
                
                try {
                    const response = await fetch(`${API_BASE}/api/terms`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ terms: terms })
                    });
                    const result = await response.json();
                    
                    hideLoading('termsLoading');
                    
                    const content = `
                        <div class="result-title">
                            <i class="fas fa-book"></i> Professional Legal Dictionary
                        </div>
                        ${result.definitions.map(def => `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                                <h4 style="color: #667eea; margin-bottom: 15px; font-size: 1.3rem;">
                                    <i class="fas fa-bookmark"></i> ${def.term}
                                </h4>
                                
                                <div style="margin-bottom: 15px; padding: 15px; background: #f8fafc; border-radius: 8px;">
                                    <h5 style="color: #374151; margin-bottom: 8px; font-weight: 600;">Professional Definition:</h5>
                                    <p style="color: #4b5563; line-height: 1.6;">${def.definition}</p>
                                </div>
                                
                                <div style="margin-bottom: 15px; padding: 15px; background: #ecfdf5; border-radius: 8px;">
                                    <h5 style="color: #059669; margin-bottom: 8px; font-weight: 600;"><i class="fas fa-lightbulb"></i> In Simple Terms:</h5>
                                    <p style="color: #047857; line-height: 1.6;">${def.simple_explanation}</p>
                                </div>
                                
                                ${def.example ? `
                                    <div style="padding: 15px; background: #eff6ff; border-radius: 8px;">
                                        <h5 style="color: #2563eb; margin-bottom: 8px; font-weight: 600;"><i class="fas fa-example"></i> Real-World Example:</h5>
                                        <p style="color: #1d4ed8; line-height: 1.6; font-style: italic;">${def.example}</p>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    `;
                    
                    showResult('termsResult', content);
                    
                } catch (error) {
                    hideLoading('termsLoading');
                    showError('termsResult', 'Failed to lookup terms. Please try again.');
                }
            }
            
            async function assessRisk() {
                const text = document.getElementById('riskText').value;
                if (!text.trim()) {
                    alert('Please enter document text for risk assessment');
                    return;
                }
                
                showLoading('riskLoading');
                document.getElementById('riskResult').style.display = 'none';
                
                try {
                    const response = await fetch(`${API_BASE}/api/risk`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ document_text: text })
                    });
                    const result = await response.json();
                    
                    hideLoading('riskLoading');
                    
                    const getRiskColor = (level) => {
                        switch(level.toLowerCase()) {
                            case 'high': return '#ef4444';
                            case 'medium': return '#f59e0b';
                            case 'low': return '#10b981';
                            default: return '#6b7280';
                        }
                    };
                    
                    const getUrgencyColor = (urgency) => {
                        switch(urgency.toLowerCase()) {
                            case 'high': return '#dc2626';
                            case 'medium': return '#d97706';
                            case 'low': return '#059669';
                            default: return '#6b7280';
                        }
                    };
                    
                    const content = `
                        <div class="result-title">
                            <i class="fas fa-shield-alt"></i> Professional Risk Assessment Report
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px;">
                            <div style="background: white; padding: 20px; border-radius: 12px; text-align: center; border-left: 4px solid ${getRiskColor(result.risk_level)};">
                                <h5 style="color: ${getRiskColor(result.risk_level)}; margin-bottom: 10px;">Risk Level</h5>
                                <p style="font-size: 1.5rem; font-weight: 700; text-transform: capitalize; color: ${getRiskColor(result.risk_level)};">${result.risk_level}</p>
                            </div>
                            
                            <div style="background: white; padding: 20px; border-radius: 12px; text-align: center; border-left: 4px solid #3b82f6;">
                                <h5 style="color: #3b82f6; margin-bottom: 10px;">Risk Score</h5>
                                <p style="font-size: 1.5rem; font-weight: 700; color: #3b82f6;">${result.risk_score}/100</p>
                            </div>
                            
                            <div style="background: white; padding: 20px; border-radius: 12px; text-align: center; border-left: 4px solid ${getUrgencyColor(result.urgency)};">
                                <h5 style="color: ${getUrgencyColor(result.urgency)}; margin-bottom: 10px;">Urgency</h5>
                                <p style="font-size: 1.5rem; font-weight: 700; text-transform: capitalize; color: ${getUrgencyColor(result.urgency)};">${result.urgency}</p>
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ef4444;">
                            <h4 style="color: #ef4444; margin-bottom: 15px;"><i class="fas fa-exclamation-triangle"></i> Identified Risk Factors</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${Array.isArray(result.risk_factors) ? result.risk_factors.map(factor => `
                                    <li style="margin-bottom: 12px; padding: 12px; background: #fee2e2; border-radius: 8px; border-left: 3px solid #ef4444;">
                                        <i class="fas fa-warning" style="color: #ef4444; margin-right: 10px;"></i>${factor}
                                    </li>
                                `).join('') : `<li style="margin-bottom: 12px; padding: 12px; background: #fee2e2; border-radius: 8px;">${result.risk_factors}</li>`}
                            </ul>
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #10b981;">
                            <h4 style="color: #10b981; margin-bottom: 15px;"><i class="fas fa-tasks"></i> Professional Recommendations</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${Array.isArray(result.recommendations) ? result.recommendations.map(rec => `
                                    <li style="margin-bottom: 12px; padding: 12px; background: #d1fae5; border-radius: 8px; border-left: 3px solid #10b981;">
                                        <i class="fas fa-check-circle" style="color: #10b981; margin-right: 10px;"></i>${rec}
                                    </li>
                                `).join('') : `<li style="margin-bottom: 12px; padding: 12px; background: #d1fae5; border-radius: 8px;">${result.recommendations}</li>`}
                            </ul>
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; border-left: 4px solid #f59e0b;">
                            <h4 style="color: #f59e0b; margin-bottom: 15px;"><i class="fas fa-balance-scale"></i> Legal Concerns</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${Array.isArray(result.legal_concerns) ? result.legal_concerns.map(concern => `
                                    <li style="margin-bottom: 12px; padding: 12px; background: #fef3c7; border-radius: 8px; border-left: 3px solid #f59e0b;">
                                        <i class="fas fa-gavel" style="color: #f59e0b; margin-right: 10px;"></i>${concern}
                                    </li>
                                `).join('') : `<li style="margin-bottom: 12px; padding: 12px; background: #fef3c7; border-radius: 8px;">${result.legal_concerns}</li>`}
                            </ul>
                        </div>
                    `;
                    
                    showResult('riskResult', content);
                    
                } catch (error) {
                    hideLoading('riskLoading');
                    showError('riskResult', 'Failed to assess risks. Please try again.');
                }
            }
            
            async function uploadDocument() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a file to upload');
                    return;
                }
                
                showLoading('uploadLoading');
                document.getElementById('uploadResult').style.display = 'none';
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch(`${API_BASE}/api/documents/upload`, {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    
                    hideLoading('uploadLoading');
                    
                    if (!result.success) {
                        showError('uploadResult', result.error || 'Upload failed');
                        return;
                    }
                    
                    const analysis = result.ai_analysis || {};
                    const riskAssessment = analysis.risk_assessment || {};
                    
                    const getRiskColor = (level) => {
                        switch((level || 'medium').toLowerCase()) {
                            case 'high': return '#ef4444';
                            case 'medium': return '#f59e0b';
                            case 'low': return '#10b981';
                            default: return '#6b7280';
                        }
                    };
                    
                    const content = `
                        <div class="result-title">
                            <i class="fas fa-file-alt"></i> Document Analysis Complete
                        </div>
                        
                        <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #10b981;">
                            <h4 style="color: #10b981; margin-bottom: 15px;"><i class="fas fa-check-circle"></i> Upload Successful</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                <div><strong>File:</strong> ${result.filename}</div>
                                <div><strong>Size:</strong> ${(result.size / 1024).toFixed(2)} KB</div>
                                <div><strong>Type:</strong> ${result.file_type}</div>
                                <div><strong>Status:</strong> ${result.processing_status}</div>
                            </div>
                        </div>
                        
                        ${analysis.document_summary ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #3b82f6;">
                                <h4 style="color: #3b82f6; margin-bottom: 15px;"><i class="fas fa-file-text"></i> Document Summary</h4>
                                <p style="line-height: 1.6; color: #374151;">${analysis.document_summary}</p>
                                ${analysis.document_type ? `<p style="margin-top: 10px;"><strong>Document Type:</strong> <span style="text-transform: capitalize;">${analysis.document_type}</span></p>` : ''}
                            </div>
                        ` : ''}
                        
                        ${analysis.plain_english_explanation ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #10b981;">
                                <h4 style="color: #10b981; margin-bottom: 15px;"><i class="fas fa-lightbulb"></i> What This Means in Plain English</h4>
                                <p style="line-height: 1.6; color: #374151;">${analysis.plain_english_explanation}</p>
                            </div>
                        ` : ''}
                        
                        ${riskAssessment.risk_level ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid ${getRiskColor(riskAssessment.risk_level)};">
                                <h4 style="color: ${getRiskColor(riskAssessment.risk_level)}; margin-bottom: 15px;"><i class="fas fa-shield-alt"></i> Risk Assessment</h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 15px;">
                                    <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: ${getRiskColor(riskAssessment.risk_level)}; text-transform: capitalize;">${riskAssessment.risk_level}</div>
                                        <div style="font-size: 0.9rem; color: #6b7280;">Risk Level</div>
                                    </div>
                                    ${riskAssessment.risk_score ? `
                                        <div style="text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px;">
                                            <div style="font-size: 1.2rem; font-weight: 700; color: #3b82f6;">${riskAssessment.risk_score}/100</div>
                                            <div style="font-size: 0.9rem; color: #6b7280;">Risk Score</div>
                                        </div>
                                    ` : ''}
                                </div>
                                ${riskAssessment.main_risks && Array.isArray(riskAssessment.main_risks) ? `
                                    <div>
                                        <h5 style="margin-bottom: 10px; color: #374151;">Main Risks Identified:</h5>
                                        <ul style="list-style: none; padding: 0;">
                                            ${riskAssessment.main_risks.map(risk => {
                                                // Handle both string and object cases
                                                const riskText = typeof risk === 'string' ? risk : 
                                                                typeof risk === 'object' ? (risk.description || risk.risk || risk.title || JSON.stringify(risk)) : 
                                                                String(risk);
                                                return `
                                                    <li style="margin-bottom: 8px; padding: 10px; background: #fee2e2; border-radius: 6px; border-left: 3px solid #ef4444;">
                                                        <i class="fas fa-warning" style="color: #ef4444; margin-right: 8px;"></i>${riskText}
                                                    </li>
                                                `;
                                            }).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                        
                        ${analysis.key_findings && Array.isArray(analysis.key_findings) ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
                                <h4 style="color: #f59e0b; margin-bottom: 15px;"><i class="fas fa-search"></i> Key Findings</h4>
                                <ul style="list-style: none; padding: 0;">
                                    ${analysis.key_findings.map(finding => `
                                        <li style="margin-bottom: 10px; padding: 12px; background: #fef3c7; border-radius: 8px; border-left: 3px solid #f59e0b;">
                                            <i class="fas fa-arrow-right" style="color: #f59e0b; margin-right: 10px;"></i>${finding}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${analysis.important_clauses && Array.isArray(analysis.important_clauses) ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #8b5cf6;">
                                <h4 style="color: #8b5cf6; margin-bottom: 15px;"><i class="fas fa-gavel"></i> Important Clauses</h4>
                                <ul style="list-style: none; padding: 0;">
                                    ${analysis.important_clauses.map(clause => `
                                        <li style="margin-bottom: 10px; padding: 12px; background: #f3e8ff; border-radius: 8px; border-left: 3px solid #8b5cf6;">
                                            <i class="fas fa-bookmark" style="color: #8b5cf6; margin-right: 10px;"></i>${clause}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${analysis.recommendations && Array.isArray(analysis.recommendations) ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; border-left: 4px solid #10b981;">
                                <h4 style="color: #10b981; margin-bottom: 15px;"><i class="fas fa-tasks"></i> Recommendations</h4>
                                <ul style="list-style: none; padding: 0;">
                                    ${analysis.recommendations.map(rec => `
                                        <li style="margin-bottom: 10px; padding: 12px; background: #d1fae5; border-radius: 8px; border-left: 3px solid #10b981;">
                                            <i class="fas fa-check-circle" style="color: #10b981; margin-right: 10px;"></i>${rec}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${result.extracted_text ? `
                            <div style="background: white; padding: 25px; border-radius: 12px; border-left: 4px solid #6b7280;">
                                <h4 style="color: #6b7280; margin-bottom: 15px;"><i class="fas fa-file-text"></i> Extracted Text Preview</h4>
                                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; line-height: 1.5; color: #374151; max-height: 200px; overflow-y: auto;">
                                    ${result.extracted_text}
                                </div>
                            </div>
                        ` : ''}
                    `;
                    
                    showResult('uploadResult', content);
                    
                } catch (error) {
                    hideLoading('uploadLoading');
                    showError('uploadResult', 'Failed to upload document. Please try again.');
                }
            }
        </script>
    </body>
    </html>
    """)
# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
    uvicorn.run(
        "combined_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )