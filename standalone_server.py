"""
Legal Assistant GenAI - Ultra Simple Version for Railway
Standalone deployment with minimal dependencies
"""

import json
import os
from typing import Optional

# Simple HTTP server using only Python standard library
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class LegalAssistantHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        return
        
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "Legal Assistant GenAI"}
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Legal Assistant GenAI API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "simplify": "/api/simplify",
                    "terms": "/api/terms"
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/features':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "features": [
                    {"name": "Text Simplification", "description": "Convert legal jargon to plain English"},
                    {"name": "Legal Terms Lookup", "description": "Get definitions for legal terms"},
                    {"name": "Document Analysis", "description": "Basic document risk assessment"},
                    {"name": "Health Check", "description": "API status monitoring"}
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Endpoint not found", "path": path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
            except:
                data = {}
        else:
            data = {}
        
        if path == '/api/simplify':
            text = data.get('text', '')
            complexity = data.get('complexity_level', 'high_school')
            
            response = {
                "success": True,
                "original_text": text,
                "simplified_text": f"Simplified to {complexity} level: {text[:100]}...",
                "complexity_level": complexity,
                "key_points": ["Legal terms explained", "Complex clauses simplified"],
                "red_flags": ["Review recommended", "Check terms carefully"]
            }
            
        elif path == '/api/terms':
            term = data.get('term', '')
            
            terms_db = {
                "liability": "Legal responsibility for damages",
                "indemnify": "To compensate for harm or loss",
                "arbitration": "Alternative dispute resolution",
                "jurisdiction": "Legal authority area"
            }
            
            definition = terms_db.get(term.lower(), f"Definition for '{term}' would appear here")
            
            response = {
                "success": True,
                "term": term,
                "definition": definition,
                "simple_explanation": f"In simple terms: {definition}"
            }
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "API endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    """Run the HTTP server"""
    port = int(os.getenv('PORT', 8001))
    host = '0.0.0.0'
    
    print(f"🚀 Starting Legal Assistant GenAI...")
    print(f"📡 Server running on http://{host}:{port}")
    print(f"💓 Health check: http://{host}:{port}/health")
    
    server = HTTPServer((host, port), LegalAssistantHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    run_server()