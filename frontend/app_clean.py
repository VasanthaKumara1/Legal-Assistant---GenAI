"""
Legal Assistant GenAI - Streamlit Frontend
Simplified working frontend for the prototype
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Legal Assistant GenAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .risk-high {
        background: #ffebee;
        border-left-color: #f44336;
    }
    .risk-medium {
        background: #fff3e0;
        border-left-color: #ff9800;
    }
    .risk-low {
        background: #e8f5e8;
        border-left-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection() -> bool:
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_document(file) -> Optional[Dict[str, Any]]:
    """Upload document to the API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def simplify_text(text: str, document_type: str = "general") -> Optional[Dict[str, Any]]:
    """Simplify text using the AI API"""
    try:
        data = {"text": text, "document_type": document_type}
        response = requests.post(f"{API_BASE_URL}/ai/simplify", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Simplification failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Simplification error: {str(e)}")
        return None

def get_risk_assessment(document_id: str) -> Optional[Dict[str, Any]]:
    """Get risk assessment from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/risk-assessment")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Risk assessment failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Risk assessment error: {str(e)}")
        return None

def get_document_analysis(document_id: str) -> Optional[Dict[str, Any]]:
    """Get document analysis from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/analysis")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Document analysis failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Document analysis error: {str(e)}")
        return None

def display_risk_level(risk_level: str):
    """Display risk level with appropriate styling"""
    risk_colors = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🔴"
    }
    color = risk_colors.get(risk_level.lower(), "⚪")
    st.markdown(f"**Risk Level:** {color} {risk_level.upper()}")

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ Legal Assistant GenAI</h1>', unsafe_allow_html=True)
    st.markdown("### AI-powered legal document simplification and analysis")
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to the API server. Please make sure the backend is running on http://localhost:8000")
        st.stop()
    
    st.success("✅ Connected to API server")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Choose a feature:",
            [
                "📄 Document Upload & Analysis", 
                "✏️ Text Simplification",
                "⚠️ Risk Assessment Demo", 
                "📊 Document Analysis Demo"
            ]
        )
    
    # Main content area
    if mode == "📄 Document Upload & Analysis":
        show_document_upload()
    elif mode == "✏️ Text Simplification":
        show_text_simplification()
    elif mode == "⚠️ Risk Assessment Demo":
        show_risk_assessment_demo()
    elif mode == "📊 Document Analysis Demo":
        show_document_analysis_demo()

def show_document_upload():
    """Document upload and processing interface"""
    st.header("📄 Document Upload & Processing")
    
    st.markdown("""
    Upload a legal document (PDF, DOCX, or TXT) to extract text and perform analysis.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Upload PDF, DOCX, or TXT files for analysis"
    )
    
    if uploaded_file is not None:
        st.markdown("### File Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{len(uploaded_file.getvalue())} bytes")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        if st.button("📤 Upload and Process"):
            with st.spinner("Processing document..."):
                result = upload_document(uploaded_file)
                
                if result:
                    st.success("✅ Document processed successfully!")
                    
                    # Display results
                    st.markdown("### Processing Results")
                    st.json(result)
                    
                    # Store document ID for other features
                    st.session_state.current_doc_id = result.get("document_id", "mock_doc_123")
                    
                    st.info("💡 You can now use other features with this document!")

def show_text_simplification():
    """Text simplification interface"""
    st.header("✏️ Legal Text Simplification")
    
    st.markdown("""
    Paste complex legal text below to get a simplified, easy-to-understand version.
    """)
    
    # Document type selection
    document_type = st.selectbox(
        "Document Type",
        ["general", "contract", "lease", "terms_of_service", "privacy_policy", "employment"]
    )
    
    # Text input
    legal_text = st.text_area(
        "Legal Text to Simplify",
        height=200,
        placeholder="Paste your legal text here...",
        help="Enter the complex legal text you want to simplify"
    )
    
    if legal_text and st.button("🤖 Simplify Text"):
        with st.spinner("Analyzing and simplifying text..."):
            result = simplify_text(legal_text, document_type)
            
            if result:
                st.success("✅ Text simplified successfully!")
                
                # Display simplified text
                st.markdown("### 📝 Simplified Version")
                st.markdown(f"<div class='feature-card'>{result['simplified_text']}</div>", 
                          unsafe_allow_html=True)
                
                # Display analysis results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🔑 Key Points")
                    for point in result['key_points']:
                        st.markdown(f"• {point}")
                
                with col2:
                    st.markdown("### ⚠️ Risk Factors")
                    display_risk_level(result['risk_level'])
                    for factor in result['risk_factors']:
                        st.markdown(f"• {factor}")
                
                # Recommendations
                st.markdown("### 💡 Recommendations")
                for rec in result['recommendations']:
                    st.markdown(f"• {rec}")
                
                # Confidence score
                st.markdown(f"**Confidence Score:** {result['confidence_score']:.0%}")

def show_risk_assessment_demo():
    """Risk assessment demo interface"""
    st.header("⚠️ Risk Assessment Demo")
    
    st.markdown("""
    See how our AI analyzes legal documents for potential risks and concerns.
    """)
    
    if st.button("🔍 Run Risk Assessment Demo"):
        with st.spinner("Analyzing document risks..."):
            # Use a mock document ID for demo
            result = get_risk_assessment("demo_doc_123")
            
            if result:
                st.success("✅ Risk assessment completed!")
                
                # Overall risk level
                st.markdown("### 📊 Overall Risk Assessment")
                display_risk_level(result['overall_risk'])
                
                # Risk factors
                st.markdown("### 🚨 Identified Risk Factors")
                
                for factor in result['risk_factors']:
                    risk_class = f"risk-{factor['risk_level']}"
                    st.markdown(f"""
                    <div class="feature-card {risk_class}">
                        <h4>{factor['risk_type'].replace('_', ' ').title()}</h4>
                        <p><strong>Risk Level:</strong> {factor['risk_level'].title()}</p>
                        <p><strong>Description:</strong> {factor['description']}</p>
                        <p><strong>Recommendation:</strong> {factor['recommendation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # General recommendations
                st.markdown("### 💡 General Recommendations")
                for rec in result['recommendations']:
                    st.markdown(f"• {rec}")
                
                # Confidence score
                st.markdown(f"**Analysis Confidence:** {result['confidence_score']:.0%}")

def show_document_analysis_demo():
    """Document analysis demo interface"""
    st.header("📊 Document Analysis Demo")
    
    st.markdown("""
    See detailed analysis of document structure, key terms, and important information.
    """)
    
    if st.button("📈 Run Document Analysis Demo"):
        with st.spinner("Analyzing document structure..."):
            result = get_document_analysis("demo_doc_123")
            
            if result:
                st.success("✅ Document analysis completed!")
                
                analysis = result['analysis']
                
                # Document overview
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Document Type", analysis['document_type'].replace('_', ' ').title())
                with col2:
                    st.metric("Parties Involved", len(analysis['parties']))
                with col3:
                    st.metric("Key Sections", len(analysis['key_sections']))
                
                # Parties
                st.markdown("### 👥 Parties Involved")
                for party in analysis['parties']:
                    st.markdown(f"• {party}")
                
                # Key sections
                st.markdown("### 📑 Key Sections")
                for section in analysis['key_sections']:
                    importance_color = {
                        'high': '🔴',
                        'medium': '🟡', 
                        'low': '🟢'
                    }.get(section['importance'], '⚪')
                    st.markdown(f"{importance_color} **{section['section']}** ({section['importance']} importance)")
                
                # Important dates
                st.markdown("### 📅 Important Dates")
                for date_info in analysis['important_dates']:
                    st.markdown(f"• **{date_info['date']}**: {date_info['description']}")
                
                # Financial terms
                st.markdown("### 💰 Financial Terms")
                fin_terms = analysis['financial_terms']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Monthly Rent", fin_terms['monthly_rent'])
                with col2:
                    st.metric("Security Deposit", fin_terms['security_deposit'])
                with col3:
                    st.metric("Late Fees", fin_terms['late_fees'])
                
                # Summary
                st.markdown("### 📋 Summary")
                st.markdown(f"<div class='feature-card'>{result['summary']}</div>", 
                          unsafe_allow_html=True)
                
                # Confidence score
                st.markdown(f"**Analysis Confidence:** {result['confidence_score']:.0%}")

if __name__ == "__main__":
    main()