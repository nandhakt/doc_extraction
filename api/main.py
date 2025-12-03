"""
FastAPI Backend for Document Extraction Agent.
"""

import os
import uuid
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.models import (
    ExtractionResponse,
    FeedbackRequest,
    PDFInfoResponse,
    PDFPageResponse,
    HealthResponse
)
from agent.extraction_agent import extraction_agent
from utils.pdf_processor import pdf_processor
from config import UPLOAD_DIR


app = FastAPI(
    title="Document Extraction Agent API",
    description="Agentic document extraction with LangGraph and human-in-the-loop feedback",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded PDFs and their text
pdf_storage = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """
    Upload a PDF file for processing.
    
    Returns:
        Session info with file details
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save the file
    file_path = Path(UPLOAD_DIR) / f"{session_id}.pdf"
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Extract text and metadata
    try:
        text = pdf_processor.extract_text(str(file_path))
        metadata = pdf_processor.get_pdf_metadata(str(file_path))
        
        # Store in memory
        pdf_storage[session_id] = {
            "file_path": str(file_path),
            "filename": file.filename,
            "text": text,
            "metadata": metadata
        }
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "page_count": metadata["page_count"],
            "text_preview": text[:500] + "..." if len(text) > 500 else text,
            "message": "PDF uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/extract/{session_id}", response_model=ExtractionResponse)
async def extract_fields(
    session_id: str,
    json_schema: str = Form(...)
) -> ExtractionResponse:
    """
    Extract fields from an uploaded PDF using the provided JSON schema.
    
    Args:
        session_id: The session ID from the upload
        json_schema: JSON schema string defining fields to extract
    
    Returns:
        Extraction results with confidence scores
    """
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first.")
    
    try:
        schema = json.loads(json_schema)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON schema")
    
    pdf_data = pdf_storage[session_id]
    
    try:
        result = extraction_agent.extract(
            document_text=pdf_data["text"],
            json_schema=schema,
            session_id=session_id
        )
        
        return ExtractionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")


@app.post("/feedback", response_model=ExtractionResponse)
async def submit_feedback(request: FeedbackRequest) -> ExtractionResponse:
    """
    Submit human feedback and re-run extraction.
    
    Args:
        request: Feedback request with session ID and feedback text
    
    Returns:
        Updated extraction results
    """
    session_id = request.session_id
    
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    session_state = extraction_agent.get_session(session_id)
    
    if not session_state:
        raise HTTPException(status_code=404, detail="No extraction found for this session")
    
    try:
        result = extraction_agent.extract(
            document_text=pdf_data["text"],
            json_schema=session_state["json_schema"],
            session_id=session_id,
            feedback=request.feedback
        )
        
        return ExtractionResponse(**result, message="Re-extraction completed with feedback")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback processing error: {str(e)}")


@app.get("/pdf/{session_id}/info", response_model=PDFInfoResponse)
async def get_pdf_info(session_id: str) -> PDFInfoResponse:
    """Get PDF information and metadata."""
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    
    return PDFInfoResponse(
        filename=pdf_data["filename"],
        page_count=pdf_data["metadata"]["page_count"],
        metadata=pdf_data["metadata"]
    )


@app.get("/pdf/{session_id}/page/{page_num}")
async def get_pdf_page(session_id: str, page_num: int) -> PDFPageResponse:
    """
    Get a specific page of the PDF as a base64 image.
    
    Args:
        session_id: Session ID
        page_num: Page number (1-indexed)
    
    Returns:
        Base64 encoded page image
    """
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    page_count = pdf_data["metadata"]["page_count"]
    
    if page_num < 1 or page_num > page_count:
        raise HTTPException(
            status_code=400, 
            detail=f"Page number must be between 1 and {page_count}"
        )
    
    try:
        images = pdf_processor.pdf_to_base64_images(pdf_data["file_path"])
        
        return PDFPageResponse(
            page_number=page_num,
            total_pages=page_count,
            image_base64=images[page_num - 1]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering page: {str(e)}")


@app.get("/pdf/{session_id}/text")
async def get_pdf_text(session_id: str) -> dict:
    """Get the extracted text from the PDF."""
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    
    return {
        "session_id": session_id,
        "text": pdf_data["text"]
    }


@app.get("/session/{session_id}")
async def get_session_status(session_id: str) -> dict:
    """Get the current status of an extraction session."""
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    session_state = extraction_agent.get_session(session_id)
    
    return {
        "session_id": session_id,
        "filename": pdf_data["filename"],
        "has_extraction": session_state is not None,
        "extraction_status": session_state["status"] if session_state else None,
        "iteration": session_state["iteration"] if session_state else 0
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a session and its associated files."""
    if session_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_data = pdf_storage[session_id]
    
    # Delete the file
    try:
        os.remove(pdf_data["file_path"])
    except OSError:
        pass
    
    # Remove from storage
    del pdf_storage[session_id]
    
    return {"message": "Session deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    from config import FASTAPI_HOST, FASTAPI_PORT
    
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)


