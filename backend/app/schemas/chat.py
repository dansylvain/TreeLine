"""Chat-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message to send to the AI agent"
    )
    
    session_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional session ID for conversation tracking"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    
    id: UUID = Field(..., description="Unique conversation ID")
    session_id: str = Field(..., description="Session ID for this conversation")
    user_message: str = Field(..., description="Original user message")
    ai_response: str = Field(..., description="AI agent response")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    created_at: datetime = Field(..., description="Timestamp when conversation was created")
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
