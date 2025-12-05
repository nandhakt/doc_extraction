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

# Custom CSS for professional light theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables - Professional Light Theme */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --accent-primary: #1e40af;
        --accent-secondary: #3b82f6;
        --accent-light: rgba(30, 64, 175, 0.08);
        --accent-hover: rgba(30, 64, 175, 0.12);
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --success: #059669;
        --success-light: rgba(5, 150, 105, 0.1);
        --warning: #d97706;
        --warning-light: rgba(217, 119, 6, 0.1);
        --error: #dc2626;
        --error-light: rgba(220, 38, 38, 0.1);
        --border-color: #e2e8f0;
        --border-focus: #1e40af;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }
    
    /* Global Styles */
    .stApp {
        background: var(--bg-secondary);
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 100%;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        padding: 1.75rem 0;
        margin-bottom: 1.5rem;
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .main-header h1 {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1.875rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.375rem;
        letter-spacing: -0.025em;
    }
    
    .main-header h1 span {
        color: var(--accent-primary);
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 0.975rem;
        font-weight: 400;
    }
    
    /* Panel Styling */
    .panel {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }
    
    .panel-header {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .panel-header h3 {
        color: var(--text-primary);
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .panel-icon {
        font-size: 1.125rem;
    }
    
    /* PDF Viewer */
    .pdf-container {
        background: var(--bg-tertiary);
        border-radius: 8px;
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
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.875rem 1rem;
        margin-bottom: 0.625rem;
        transition: all 0.15s ease;
    }
    
    .field-card:hover {
        border-color: var(--accent-secondary);
        box-shadow: var(--shadow-md);
    }
    
    .field-name {
        color: var(--accent-primary);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        margin-bottom: 0.25rem;
    }
    
    .field-value {
        color: var(--text-primary);
        font-size: 0.9375rem;
        font-weight: 500;
        line-height: 1.4;
    }
    
    .confidence-bar {
        height: 3px;
        background: var(--bg-tertiary);
        border-radius: 2px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.4s ease;
    }
    
    .confidence-high { background: var(--success); }
    .confidence-medium { background: var(--warning); }
    .confidence-low { background: var(--error); }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        border-radius: 6px;
        font-size: 0.8125rem;
        font-weight: 500;
    }
    
    .status-success {
        background: var(--success-light);
        color: var(--success);
        border: 1px solid rgba(5, 150, 105, 0.2);
    }
    
    .status-warning {
        background: var(--warning-light);
        color: var(--warning);
        border: 1px solid rgba(217, 119, 6, 0.2);
    }
    
    .status-processing {
        background: var(--accent-light);
        color: var(--accent-primary);
        border: 1px solid rgba(30, 64, 175, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--accent-primary);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.25rem;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.15s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: #1e3a8a;
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Text Areas and Inputs */
    .stTextArea textarea, .stTextInput input {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8125rem !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--accent-light) !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: var(--bg-primary);
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--accent-secondary);
        background: var(--accent-light);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--bg-primary);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        border-radius: 6px;
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Typography Overrides */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    
    p, span, label, div {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    /* Info, Warning, Error boxes */
    .stAlert {
        border-radius: 6px;
        border: none;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .stDownloadButton > button:hover {
        background: var(--bg-secondary);
        border-color: var(--accent-secondary);
    }
    
    /* Code blocks */
    code {
        background: var(--bg-tertiary);
        color: var(--accent-primary);
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8125rem;
    }
    
    /* Success message */
    .stSuccess {
        background: var(--success-light);
        color: var(--success);
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
        <h1><span>DocExtract</span> AI</h1>
        <p>Intelligent document extraction with human-in-the-loop refinement</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.markdown("### Configuration")
        
        # JSON Schema Input
        st.markdown("#### Extraction Schema")
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
            st.markdown("#### Session Info")
            st.code(f"ID: {st.session_state.session_id[:8]}...")
            
            if st.session_state.pdf_info:
                st.markdown(f"**File:** {st.session_state.pdf_info.get('filename', 'Unknown')}")
                st.markdown(f"**Pages:** {st.session_state.pdf_info.get('page_count', 0)}")
            
            if st.button("Clear Session", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


def render_pdf_viewer():
    """Render the PDF viewer panel."""
    st.markdown("""
    <div class="panel">
        <div class="panel-header">
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
            with st.spinner("Uploading document..."):
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
            <h3>Extracted Data</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.pdf_uploaded:
        st.info("Upload a PDF document to begin extraction")
        return
    
    # Extract Button
    if st.session_state.json_schema:
        if st.button("Extract Fields", use_container_width=True, type="primary"):
            with st.spinner("Analyzing document..."):
                result = extract_fields(
                    st.session_state.session_id,
                    st.session_state.json_schema
                )
                if result:
                    st.session_state.extraction_result = result
                    st.rerun()
    else:
        st.warning("Please provide a valid JSON schema in the sidebar")
    
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
            "validated": "Validated",
            "needs_review": "Needs Review",
            "extracted": "Extracted"
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
        st.markdown("### Provide Feedback")
        
        feedback_text = st.text_area(
            "Provide corrections or additional context",
            placeholder="e.g., 'The invoice number should include the prefix INV-' or 'The date format should be YYYY-MM-DD'",
            key="feedback_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Re-extract with Feedback", use_container_width=True, disabled=not feedback_text):
                with st.spinner("Re-processing with feedback..."):
                    result = submit_feedback(
                        st.session_state.session_id,
                        feedback_text
                    )
                    if result:
                        st.session_state.extraction_result = result
                        st.success("Re-extraction completed!")
                        st.rerun()
        
        with col2:
            if st.button("Accept Results", use_container_width=True):
                st.success("Results accepted!")
                st.balloons()
        
        # Export Options
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Export Results"):
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


