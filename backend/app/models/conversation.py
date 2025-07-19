"""Conversation database model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class Conversation(Base):
    """Conversation model for storing chat interactions."""
    
    __tablename__ = "conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    session_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    user_message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    ai_response: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, session_id={self.session_id})>"
