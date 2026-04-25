"""WebSocket routes for streaming chat."""

import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.chat.chat_engine import ChatEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Global instance (will be initialized in main.py)
chat_engine: Optional[ChatEngine] = None


def init_websocket_routes(engine: ChatEngine) -> None:
    """Initialize WebSocket routes with dependencies.

    Args:
        engine: ChatEngine instance
    """
    global chat_engine
    chat_engine = engine
    logger.info("Initialized WebSocket routes")


@router.websocket("/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming chat.

    Args:
        websocket: WebSocket connection
        session_id: Session ID

    Message format (client -> server):
    {
        "message": "user message",
        "retrieval_mode": "hybrid",
        "similarity_top_k": 5
    }

    Message format (server -> client):
    {
        "type": "chunk|complete|error",
        "content": "response chunk or full response",
        "sources": [...] (only in complete message)
    }
    """
    if not chat_engine:
        await websocket.close(code=1011, reason="Chat engine not initialized")
        return

    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message = data.get("message")
            retrieval_mode = data.get("retrieval_mode", "hybrid")
            similarity_top_k = data.get("similarity_top_k", 5)

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Message is required",
                })
                continue

            try:
                # Stream response
                full_response = ""

                async for chunk in chat_engine.stream_message(
                    session_id=session_id,
                    message=message,
                    retrieval_mode=retrieval_mode,
                    similarity_top_k=similarity_top_k,
                ):
                    full_response += chunk

                    # Send chunk to client
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk,
                    })

                # Get session to retrieve sources from last message
                from backend.services.chat.session_manager import session_manager

                if session_manager:
                    session = session_manager.load_session(session_id)
                    if session and session.messages:
                        last_message = session.messages[-1]
                        sources = last_message.sources or []
                    else:
                        sources = []
                else:
                    sources = []

                # Send completion message with sources
                await websocket.send_json({
                    "type": "complete",
                    "content": full_response,
                    "sources": sources,
                })

            except ValueError as e:
                # Validation error
                await websocket.send_json({
                    "type": "error",
                    "content": str(e),
                })

            except Exception as e:
                # Internal error
                logger.error(f"Error in WebSocket chat: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": f"Internal error: {str(e)}",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")

    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
