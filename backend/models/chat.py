"""Pydantic models for chat functionality."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    sources: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Source citations for assistant messages",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ChatSession(BaseModel):
    """Chat session model."""

    session_id: str = Field(..., description="Unique session identifier")
    name: Optional[str] = Field(default=None, description="Session name")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    messages: list[ChatMessage] = Field(default_factory=list, description="Message history")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    knowledge_base_id: Optional[str] = Field(default=None, description="Knowledge base ID for this session")
    model_id: Optional[str] = Field(default=None, description="Model ID for this session")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SendMessageRequest(BaseModel):
    """Request to send a message."""

    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="User message")
    source_filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Filters for source retrieval",
    )
    retrieval_mode: str = Field(
        default="hybrid",
        description="Retrieval mode: 'hybrid', 'vector', or 'bm25'",
    )
    similarity_top_k: int = Field(
        default=5,
        description="Number of sources to retrieve",
    )
    knowledge_base_id: Optional[str] = Field(
        default=None,
        description="Knowledge base ID to use for this message",
    )
    model_id: Optional[str] = Field(
        default=None,
        description="Model ID to use for this message",
    )


class ChatResponse(BaseModel):
    """Response from chat engine."""

    message_id: str = Field(..., description="Message identifier")
    content: str = Field(..., description="Assistant response")
    sources: list[dict[str, Any]] = Field(default_factory=list, description="Source citations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""

    name: Optional[str] = Field(default=None, description="Session name")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    knowledge_base_id: Optional[str] = Field(default=None, description="Knowledge base ID for this session")
    model_id: Optional[str] = Field(default=None, description="Model ID for this session")


class SessionListResponse(BaseModel):
    """Response with list of sessions."""

    sessions: list[dict[str, Any]] = Field(..., description="List of session summaries")
    total: int = Field(..., description="Total number of sessions")


class Citation(BaseModel):
    """Source citation model."""

    source_id: str = Field(..., description="Source document ID")
    source_type: str = Field(..., description="Source type (jira, confluence, pdf, etc.)")
    title: str = Field(..., description="Source title")
    url: Optional[str] = Field(default=None, description="Source URL")
    snippet: str = Field(..., description="Relevant text snippet")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
