"""
Streamlit Frontend for Document Extraction Agent.

A beautiful, modern UI for PDF document extraction with human-in-the-loop feedback.
"""

import streamlit as st
import httpx
import json
import base64
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="DocExtract AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful, modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a24;
        --accent-primary: #6366f1;
        --accent-secondary: #818cf8;
        --accent-glow: rgba(99, 102, 241, 0.3);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --border-color: #2d2d3a;
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0d0d14 50%, #0a0a12 100%);
        font-family: 'Outfit', sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%);
        border-bottom: 1px solid var(--border-color);
    }
    
    .main-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Panel Styling */
    .panel {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }
    
    .panel-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .panel-header h3 {
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .panel-icon {
        font-size: 1.3rem;
    }
    
    /* PDF Viewer */
    .pdf-container {
        background: #000;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }
    
    .pdf-container img {
        width: 100%;
        height: auto;
        display: block;
    }
    
    /* Extracted Data Display */
    .field-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .field-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 20px var(--accent-glow);
    }
    
    .field-name {
        color: var(--accent-secondary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .field-value {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 500;
    }
    
    .confidence-bar {
        height: 4px;
        background: var(--bg-primary);
        border-radius: 2px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.5s ease;
    }
    
    .confidence-high { background: var(--success); }
    .confidence-medium { background: var(--warning); }
    .confidence-low { background: var(--error); }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.15);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.15);
        color: var(--warning);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-processing {
        background: rgba(99, 102, 241, 0.15);
        color: var(--accent-secondary);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.4);
    }
    
    /* Text Areas and Inputs */
    .stTextArea textarea, .stTextInput input {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: var(--bg-tertiary);
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--accent-primary);
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        border-radius: 10px;
        color: var(--text-primary);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "session_id": None,
        "pdf_uploaded": False,
        "pdf_info": None,
        "current_page": 1,
        "extraction_result": None,
        "json_schema": None,
        "feedback_submitted": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def upload_pdf(file) -> Optional[dict]:
    """Upload PDF to the API."""
    try:
        with httpx.Client(timeout=60.0) as client:
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            response = client.post(f"{API_BASE_URL}/upload", files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None


def extract_fields(session_id: str, schema: dict) -> Optional[dict]:
    """Extract fields from the PDF."""
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE_URL}/extract/{session_id}",
                data={"json_schema": json.dumps(schema)}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Extraction failed: {str(e)}")
        return None


def submit_feedback(session_id: str, feedback: str) -> Optional[dict]:
    """Submit feedback and re-run extraction."""
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{API_BASE_URL}/feedback",
                json={"session_id": session_id, "feedback": feedback}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Feedback submission failed: {str(e)}")
        return None


def get_pdf_page(session_id: str, page_num: int) -> Optional[str]:
    """Get a PDF page as base64 image."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{API_BASE_URL}/pdf/{session_id}/page/{page_num}")
            response.raise_for_status()
            return response.json().get("image_base64")
    except Exception as e:
        st.error(f"Failed to load page: {str(e)}")
        return None


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>📄 DocExtract AI</h1>
        <p>Intelligent document extraction with human-in-the-loop refinement</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # JSON Schema Input
        st.markdown("#### 📋 Extraction Schema")
        st.markdown("*Define the fields you want to extract*")
        
        default_schema = '''{
  "type": "object",
  "properties": {
    "invoice_number": {
      "type": "string",
      "description": "Invoice or document number"
    },
    "date": {
      "type": "string",
      "description": "Document date"
    },
    "total_amount": {
      "type": "number",
      "description": "Total amount/value"
    },
    "vendor_name": {
      "type": "string",
      "description": "Vendor or company name"
    },
    "line_items": {
      "type": "array",
      "description": "List of items",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "number"},
          "amount": {"type": "number"}
        }
      }
    }
  },
  "required": ["invoice_number", "date", "total_amount"]
}'''
        
        schema_input = st.text_area(
            "JSON Schema",
            value=default_schema,
            height=350,
            key="schema_input",
            label_visibility="collapsed"
        )
        
        try:
            st.session_state.json_schema = json.loads(schema_input)
            st.success("✓ Valid JSON schema")
        except json.JSONDecodeError:
            st.error("✗ Invalid JSON format")
            st.session_state.json_schema = None
        
        st.markdown("---")
        
        # Session Info
        if st.session_state.session_id:
            st.markdown("#### 📊 Session Info")
            st.code(f"ID: {st.session_state.session_id[:8]}...")
            
            if st.session_state.pdf_info:
                st.markdown(f"**File:** {st.session_state.pdf_info.get('filename', 'Unknown')}")
                st.markdown(f"**Pages:** {st.session_state.pdf_info.get('page_count', 0)}")
            
            if st.button("🗑️ Clear Session", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


def render_pdf_viewer():
    """Render the PDF viewer panel."""
    st.markdown("""
    <div class="panel">
        <div class="panel-header">
            <span class="panel-icon">📑</span>
            <h3>Document Viewer</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.pdf_uploaded:
        uploaded_file = st.file_uploader(
            "Drop your PDF here",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            with st.spinner("📤 Uploading document..."):
                result = upload_pdf(uploaded_file)
                if result:
                    st.session_state.session_id = result["session_id"]
                    st.session_state.pdf_uploaded = True
                    st.session_state.pdf_info = result
                    st.rerun()
    else:
        # Page navigation
        if st.session_state.pdf_info:
            total_pages = st.session_state.pdf_info.get("page_count", 1)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Prev", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col2:
                st.markdown(f"<center>Page {st.session_state.current_page} of {total_pages}</center>", unsafe_allow_html=True)
            with col3:
                if st.button("Next ▶", disabled=st.session_state.current_page >= total_pages):
                    st.session_state.current_page += 1
                    st.rerun()
            
            # Render PDF page
            with st.spinner("Loading page..."):
                page_image = get_pdf_page(
                    st.session_state.session_id,
                    st.session_state.current_page
                )
                if page_image:
                    st.markdown('<div class="pdf-container">', unsafe_allow_html=True)
                    st.image(
                        f"data:image/png;base64,{page_image}",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)


def render_extraction_panel():
    """Render the extraction results panel."""
    st.markdown("""
    <div class="panel">
        <div class="panel-header">
            <span class="panel-icon">🎯</span>
            <h3>Extracted Data</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.pdf_uploaded:
        st.info("📤 Upload a PDF to begin extraction")
        return
    
    # Extract Button
    if st.session_state.json_schema:
        if st.button("🚀 Extract Fields", use_container_width=True, type="primary"):
            with st.spinner("🔍 Analyzing document..."):
                result = extract_fields(
                    st.session_state.session_id,
                    st.session_state.json_schema
                )
                if result:
                    st.session_state.extraction_result = result
                    st.rerun()
    else:
        st.warning("⚠️ Please provide a valid JSON schema in the sidebar")
    
    # Display Results
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        
        # Status Badge
        status = result.get("status", "unknown")
        status_class = {
            "validated": "status-success",
            "needs_review": "status-warning",
            "extracted": "status-processing"
        }.get(status, "status-processing")
        
        status_text = {
            "validated": "✓ Validated",
            "needs_review": "⚠ Needs Review",
            "extracted": "● Extracted"
        }.get(status, status.title())
        
        st.markdown(f"""
        <div class="status-badge {status_class}">
            {status_text} &nbsp;•&nbsp; Iteration {result.get('iteration', 1)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Extracted Fields
        extracted_data = result.get("extracted_data", {})
        confidence_scores = result.get("confidence_scores", {})
        
        for field, value in extracted_data.items():
            confidence = confidence_scores.get(field, 0.5)
            confidence_pct = int(confidence * 100)
            
            if confidence >= 0.8:
                conf_class = "confidence-high"
            elif confidence >= 0.5:
                conf_class = "confidence-medium"
            else:
                conf_class = "confidence-low"
            
            # Handle complex values
            if isinstance(value, (dict, list)):
                display_value = json.dumps(value, indent=2)
            else:
                display_value = str(value) if value is not None else "Not found"
            
            st.markdown(f"""
            <div class="field-card">
                <div class="field-name">{field}</div>
                <div class="field-value">{display_value}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill {conf_class}" style="width: {confidence_pct}%"></div>
                </div>
                <div style="color: var(--text-secondary); font-size: 0.75rem; margin-top: 0.25rem;">
                    Confidence: {confidence_pct}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback Section
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💬 Human Feedback")
        
        feedback_text = st.text_area(
            "Provide corrections or additional context",
            placeholder="e.g., 'The invoice number should include the prefix INV-' or 'The date format should be YYYY-MM-DD'",
            key="feedback_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-extract with Feedback", use_container_width=True, disabled=not feedback_text):
                with st.spinner("♻️ Re-processing with feedback..."):
                    result = submit_feedback(
                        st.session_state.session_id,
                        feedback_text
                    )
                    if result:
                        st.session_state.extraction_result = result
                        st.success("Re-extraction completed!")
                        st.rerun()
        
        with col2:
            if st.button("✅ Accept Results", use_container_width=True):
                st.success("Results accepted! ✓")
                st.balloons()
        
        # Export Options
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📥 Export Results"):
            export_data = {
                "session_id": st.session_state.session_id,
                "filename": st.session_state.pdf_info.get("filename", ""),
                "extracted_data": extracted_data,
                "confidence_scores": confidence_scores,
                "status": status
            }
            
            st.download_button(
                "Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name="extraction_results.json",
                mime="application/json",
                use_container_width=True
            )


def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Main content - Two columns
    col_pdf, col_extract = st.columns([1, 1], gap="large")
    
    with col_pdf:
        render_pdf_viewer()
    
    with col_extract:
        render_extraction_panel()


if __name__ == "__main__":
    main()


