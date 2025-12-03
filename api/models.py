"""
Pydantic models for API request/response schemas.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request model for document extraction."""
    json_schema: Dict[str, Any] = Field(
        ..., 
        description="JSON schema defining the fields to extract"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for tracking extraction state"
    )


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    session_id: str = Field(..., description="Session ID of the extraction")
    feedback: str = Field(..., description="Human feedback for re-extraction")


class ExtractionResponse(BaseModel):
    """Response model for extraction results."""
    session_id: str
    status: str
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[Dict[str, float]] = None
    iteration: int = 1
    needs_feedback: bool = False
    message: Optional[str] = None


class PDFInfoResponse(BaseModel):
    """Response model for PDF information."""
    filename: str
    page_count: int
    metadata: Dict[str, Any]


class PDFPageResponse(BaseModel):
    """Response model for PDF page image."""
    page_number: int
    total_pages: int
    image_base64: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"


