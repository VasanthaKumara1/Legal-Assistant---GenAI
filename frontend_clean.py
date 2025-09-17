"""
Streamlit frontend for the AI Legal Assistant.
"""
import streamlit as st
import requests
import time
from typing import Optional, Dict, Any
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/upload"
PROCESS_ENDPOINT = f"{API_BASE_URL}/api/process"
SIMPLIFY_ENDPOINT = f"{API_BASE_URL}/api/simplify"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Page configuration
st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection() -> bool:
    """Check if the API server is running."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_document(file) -> Optional[Dict[str, Any]]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def process_document(file_id: str) -> Optional[Dict[str, Any]]:
    """Process a document and extract text."""
    try:
        response = requests.get(f"{PROCESS_ENDPOINT}/{file_id}", timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Processing failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None

def simplify_text(text: str, reading_level: str = "high_school") -> Optional[Dict[str, Any]]:
    """Simplify text using the API."""
    try:
        data = {
            "text": text,
            "reading_level": reading_level
        }
        response = requests.post(SIMPLIFY_ENDPOINT, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Simplification failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Simplification error: {str(e)}")
        return None

def document_processing_mode():
    """Document upload and processing mode."""
    st.markdown('<h2 class="section-header">📄 Document Upload & Processing</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a document file",
        type=["txt", "pdf", "docx", "doc"],
        help="Upload a legal document for processing and simplification"
    )
    
    if uploaded_file is not None:
        st.write(f"File: {uploaded_file.name}")
        st.write(f"Size: {uploaded_file.size} bytes")
        st.write(f"Type: {uploaded_file.type}")
        
        if st.button("Upload and Process Document"):
            with st.spinner("Uploading document..."):
                upload_result = upload_document(uploaded_file)
            
            if upload_result:
                st.success("✅ Document uploaded successfully!")
                
                file_id = upload_result["file_id"]
                
                with st.spinner("Processing document..."):
                    process_result = process_document(file_id)
                
                if process_result:
                    st.success("✅ Document processed successfully!")
                    
                    # Display extracted text
                    extracted_text = process_result["extracted_text"]
                    st.subheader("📝 Extracted Text")
                    st.text_area("Original Text", extracted_text, height=200)
                    
                    # Simplify the extracted text
                    reading_level = st.selectbox(
                        "Choose reading level for simplification:",
                        ["elementary", "high_school", "college"],
                        index=1
                    )
                    
                    if st.button("Simplify Extracted Text"):
                        with st.spinner("Simplifying text..."):
                            simplify_result = simplify_text(extracted_text, reading_level)
                        
                        if simplify_result:
                            st.subheader("✨ Simplified Text")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Original Text:**")
                                st.text_area("", simplify_result["original_text"], height=150, key="orig")
                            
                            with col2:
                                st.markdown("**Simplified Text:**")
                                st.text_area("", simplify_result["simplified_text"], height=150, key="simp")

def text_simplification_mode():
    """Direct text simplification mode."""
    st.markdown('<h2 class="section-header">✨ Direct Text Simplification</h2>', unsafe_allow_html=True)
    
    st.write("Paste legal text below and get a simplified version:")
    
    input_text = st.text_area(
        "Legal Text to Simplify",
        placeholder="Enter legal text here...",
        height=200
    )
    
    reading_level = st.selectbox(
        "Choose reading level:",
        ["elementary", "high_school", "college"],
        index=1,
        help="Elementary: Grade 1-6, High School: Grade 7-12, College: Higher education level"
    )
    
    if st.button("Simplify Text", type="primary"):
        if not input_text.strip():
            st.warning("Please enter some text to simplify.")
            return
        
        with st.spinner("Simplifying text..."):
            result = simplify_text(input_text, reading_level)
        
        if result:
            st.success("✅ Text simplified successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Text:**")
                st.text_area("", result["original_text"], height=200, key="direct_orig")
            
            with col2:
                st.markdown("**Simplified Text:**")
                st.text_area("", result["simplified_text"], height=200, key="direct_simp")
            
            # Show metadata
            st.info(f"Reading level: {result['reading_level']}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ AI Legal Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Upload legal documents and get simplified, easy-to-understand versions using AI.")
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to the API server. Please make sure the backend is running on http://localhost:8000")
        st.stop()
    
    st.success("✅ Connected to API server")
    
    # Sidebar for options
    st.sidebar.title("Options")
    mode = st.sidebar.radio(
        "Choose Mode:",
        ["Document Upload & Processing", "Direct Text Simplification"]
    )
    
    # API Information in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Information")
    try:
        health_response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.sidebar.write(f"**Service:** {health_data.get('service', 'N/A')}")
            st.sidebar.write(f"**Version:** {health_data.get('version', 'N/A')}")
            st.sidebar.write(f"**Status:** {health_data.get('status', 'N/A')}")
            
            if health_data.get('openai_configured'):
                st.sidebar.success("🤖 AI Service: OpenAI Connected")
            else:
                st.sidebar.warning("🤖 AI Service: Mock Mode (No API Key)")
    except:
        st.sidebar.error("Could not fetch API information")
    
    # Main content
    if mode == "Document Upload & Processing":
        document_processing_mode()
    else:
        text_simplification_mode()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with Streamlit and FastAPI | "
        "[API Documentation](http://localhost:8000/docs)"
    )

if __name__ == "__main__":
    main()