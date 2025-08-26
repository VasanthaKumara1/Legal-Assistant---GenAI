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
UPLOAD_ENDPOINT = f"{API_BASE_URL}/documents/upload"
PROCESS_ENDPOINT = f"{API_BASE_URL}/documents"
SIMPLIFY_ENDPOINT = f"{API_BASE_URL}/ai/simplify"
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
        files = {"file": (file.name, file, file.type)}
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None


def process_document(document_id: int, process_ocr: bool = True, process_ai: bool = True) -> Optional[Dict[str, Any]]:
    """Process a document through OCR and AI."""
    try:
        data = {
            "document_id": document_id,
            "process_ocr": process_ocr,
            "process_ai": process_ai
        }
        response = requests.post(f"{PROCESS_ENDPOINT}/{document_id}/process", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Processing failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None


def get_document_content(document_id: int) -> Optional[Dict[str, Any]]:
    """Get document content from the API."""
    try:
        response = requests.get(f"{PROCESS_ENDPOINT}/{document_id}/content")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get content: {response.text}")
            return None
    except Exception as e:
        st.error(f"Content retrieval error: {str(e)}")
        return None


def simplify_text_direct(text: str, context: str = "") -> Optional[Dict[str, Any]]:
    """Directly simplify text using the AI API."""
    try:
        data = {"text": text, "context": context if context else None}
        response = requests.post(SIMPLIFY_ENDPOINT, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Simplification failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Simplification error: {str(e)}")
        return None


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
    
    if mode == "Document Upload & Processing":
        document_processing_mode()
    else:
        text_simplification_mode()


def document_processing_mode():
    """Document upload and processing interface."""
    
    st.markdown('<h2 class="section-header">📄 Document Processing</h2>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a legal document",
        type=["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"],
        help="Upload PDF, Word documents, text files, or images"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size:,} bytes")
        st.write(f"**Type:** {uploaded_file.type}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            process_ocr = st.checkbox("Extract text (OCR)", value=True)
        with col2:
            process_ai = st.checkbox("Simplify with AI", value=True)
        
        if st.button("Upload and Process Document", type="primary"):
            with st.spinner("Uploading document..."):
                # Upload document
                upload_result = upload_document(uploaded_file)
                
                if upload_result:
                    st.success(f"✅ Document uploaded successfully! ID: {upload_result['id']}")
                    document_id = upload_result['id']
                    
                    # Store document ID in session state
                    st.session_state.current_document_id = document_id
                    
                    with st.spinner("Processing document..."):
                        # Process document
                        process_result = process_document(document_id, process_ocr, process_ai)
                        
                        if process_result:
                            st.success("✅ Document processing completed!")
                            
                            # Auto-display results
                            display_document_results(document_id)
    
    # Option to view previously processed document
    st.markdown("---")
    st.markdown("### View Previously Processed Document")
    
    document_id_input = st.number_input(
        "Enter Document ID",
        min_value=1,
        value=getattr(st.session_state, 'current_document_id', 1),
        help="Enter the ID of a previously uploaded document"
    )
    
    if st.button("Load Document"):
        display_document_results(document_id_input)


def display_document_results(document_id: int):
    """Display the results of document processing."""
    with st.spinner("Loading document content..."):
        content = get_document_content(document_id)
        
        if content:
            st.markdown('<h2 class="section-header">📖 Document Content</h2>', unsafe_allow_html=True)
            
            # Status information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ocr_status = content['ocr_status']
                if ocr_status == "completed":
                    st.success(f"OCR: {ocr_status}")
                elif ocr_status == "failed":
                    st.error(f"OCR: {ocr_status}")
                else:
                    st.warning(f"OCR: {ocr_status}")
            
            with col2:
                ai_status = content['ai_status']
                if ai_status == "completed":
                    st.success(f"AI: {ai_status}")
                elif ai_status == "failed":
                    st.error(f"AI: {ai_status}")
                else:
                    st.warning(f"AI: {ai_status}")
            
            with col3:
                if content.get('processing_time'):
                    st.info(f"Time: {content['processing_time']:.2f}s")
            
            # Display content in two columns
            if content.get('original_text') or content.get('simplified_text'):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📄 Original Text")
                    if content.get('original_text'):
                        st.text_area(
                            "Original Content",
                            value=content['original_text'],
                            height=400,
                            label_visibility="collapsed"
                        )
                    else:
                        st.info("No original text available. OCR may not have completed successfully.")
                
                with col2:
                    st.markdown("#### ✨ Simplified Text")
                    if content.get('simplified_text'):
                        st.text_area(
                            "Simplified Content",
                            value=content['simplified_text'],
                            height=400,
                            label_visibility="collapsed"
                        )
                    else:
                        st.info("No simplified text available. AI processing may not have completed successfully.")
                
                # Processing details
                if content.get('tokens_used') or content.get('model_used'):
                    st.markdown("#### 📊 Processing Details")
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        if content.get('tokens_used'):
                            st.metric("Tokens Used", content['tokens_used'])
                    
                    with detail_col2:
                        if content.get('model_used'):
                            st.metric("AI Model", content['model_used'])
            else:
                st.warning("No content available yet. The document may still be processing.")


def text_simplification_mode():
    """Direct text simplification interface."""
    
    st.markdown('<h2 class="section-header">✨ Direct Text Simplification</h2>', unsafe_allow_html=True)
    st.markdown("Paste legal text directly to get a simplified version.")
    
    # Text input
    legal_text = st.text_area(
        "Enter legal text to simplify:",
        height=200,
        placeholder="Paste your legal document text here..."
    )
    
    context = st.text_input(
        "Additional context (optional):",
        placeholder="e.g., This is a rental agreement, contract type, etc."
    )
    
    if st.button("Simplify Text", type="primary", disabled=not legal_text.strip()):
        if legal_text.strip():
            with st.spinner("Simplifying text with AI..."):
                result = simplify_text_direct(legal_text, context)
                
                if result:
                    st.markdown('<h2 class="section-header">📖 Simplification Results</h2>', unsafe_allow_html=True)
                    
                    # Processing info
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Processing Time", f"{result['processing_time']:.2f}s")
                    with col2:
                        st.metric("Tokens Used", result['tokens_used'])
                    with col3:
                        st.metric("AI Model", result['model_used'])
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📄 Original Text")
                        st.text_area(
                            "Original",
                            value=result['original_text'],
                            height=300,
                            label_visibility="collapsed"
                        )
                    
                    with col2:
                        st.markdown("#### ✨ Simplified Text")
                        st.text_area(
                            "Simplified",
                            value=result['simplified_text'],
                            height=300,
                            label_visibility="collapsed"
                        )


if __name__ == "__main__":
    main()