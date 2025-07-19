"""Chat API routes."""

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ...core.database import get_db
from ...core.config import settings
from ...models.conversation import Conversation
from ...schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ChatResponse:
    """Send a message to the AI agent and get a response."""
    
    start_time = time.time()
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Call AI agent service
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(
                f"{settings.ai_agent_url}/generate",
                json={
                    "message": request.message,
                    "session_id": session_id
                },
                timeout=30.0
            )
            ai_response.raise_for_status()
            ai_data = ai_response.json()
            ai_message = ai_data.get("response", "I'm sorry, I couldn't process your request.")
    
    except httpx.RequestError:
        # Fallback response if AI agent is unavailable
        ai_message = "I'm currently experiencing technical difficulties. Please try again later."
    
    except httpx.HTTPStatusError:
        # Fallback response for HTTP errors
        ai_message = "I'm sorry, I encountered an error while processing your request."
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Save conversation to database
    conversation = Conversation(
        session_id=session_id,
        user_message=request.message,
        ai_response=ai_message,
        response_time_ms=response_time_ms
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ChatResponse.model_validate(conversation)


@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50
):
    """Get chat history for a session."""
    
    from sqlalchemy import select
    
    stmt = (
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    
    return [ChatResponse.model_validate(conv) for conv in conversations]
