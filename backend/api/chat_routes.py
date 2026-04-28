"""Chat API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.models.chat import (
    ChatResponse,
    CreateSessionRequest,
    SendMessageRequest,
    SessionListResponse,
)
from backend.services.chat.chat_engine import ChatEngine
from backend.services.chat.session_manager import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global instances (will be initialized in main.py)
chat_engine: Optional[ChatEngine] = None
session_manager: Optional[SessionManager] = None


def init_chat_routes(engine: ChatEngine, manager: SessionManager) -> None:
    """Initialize chat routes with dependencies.

    Args:
        engine: ChatEngine instance
        manager: SessionManager instance
    """
    global chat_engine, session_manager
    chat_engine = engine
    session_manager = manager
    logger.info("Initialized chat routes")


@router.post("/sessions", response_model=dict)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session.

    Args:
        request: Session creation request

    Returns:
        Session information
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        session = session_manager.create_session(
            name=request.name,
            metadata=request.metadata,
            knowledge_base_id=request.knowledge_base_id,
            model_id=request.model_id,
        )

        return {
            "session_id": session.session_id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "message_count": 0,
            "knowledge_base_id": session.knowledge_base_id,
            "model_id": session.model_id,
        }

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List all chat sessions.

    Args:
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip

    Returns:
        List of session summaries
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        sessions = session_manager.list_sessions(limit=limit, offset=offset)

        return SessionListResponse(
            sessions=sessions,
            total=len(sessions),
        )

    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details.

    Args:
        session_id: Session ID

    Returns:
        Session information with message history
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        session = session_manager.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session.session_id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "sources": msg.sources,
                }
                for msg in session.messages
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session.

    Args:
        session_id: Session ID

    Returns:
        Deletion confirmation
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        success = session_manager.delete_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"success": True, "message": "Session deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=ChatResponse)
async def send_message(request: SendMessageRequest):
    """Send a message and get response.

    Args:
        request: Message request

    Returns:
        Chat response with sources
    """
    if not chat_engine:
        raise HTTPException(status_code=500, detail="Chat engine not initialized")

    try:
        response = await chat_engine.send_message(
            session_id=request.session_id,
            message=request.message,
            retrieval_mode=request.retrieval_mode,
            similarity_top_k=request.similarity_top_k,
            source_filters=request.source_filters,
            knowledge_base_id=request.knowledge_base_id,
            model_id=request.model_id,
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    max_messages: Optional[int] = Query(default=None, ge=1, le=100),
):
    """Get conversation history for a session.

    Args:
        session_id: Session ID
        max_messages: Maximum number of recent messages

    Returns:
        List of messages
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")

    try:
        history = session_manager.get_conversation_history(
            session_id=session_id,
            max_messages=max_messages,
        )

        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "sources": msg.sources,
                }
                for msg in history
            ],
        }

    except Exception as e:
        logger.error(f"Failed to get history for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
