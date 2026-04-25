"""Chat session manager for creating, loading, and saving sessions."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config.settings import settings
from backend.models.chat import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage chat sessions."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize session manager.

        Args:
            storage_dir: Directory for session storage (default: from settings)
        """
        self.storage_dir = storage_dir or settings.chat_history_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized SessionManager at {self.storage_dir}")

    def create_session(
        self,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ChatSession:
        """Create a new chat session.

        Args:
            name: Session name (optional)
            metadata: Session metadata (optional)

        Returns:
            New ChatSession
        """
        session_id = str(uuid.uuid4())

        session = ChatSession(
            session_id=session_id,
            name=name or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            metadata=metadata or {},
        )

        # Save session
        self._save_session(session)

        logger.info(f"Created session: {session_id}")

        return session

    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a chat session.

        Args:
            session_id: Session ID

        Returns:
            ChatSession if found, None otherwise
        """
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            logger.warning(f"Session not found: {session_id}")
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            session = ChatSession(**data)
            logger.info(f"Loaded session: {session_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def save_session(self, session: ChatSession) -> None:
        """Save a chat session.

        Args:
            session: ChatSession to save
        """
        # Update timestamp
        session.updated_at = datetime.utcnow()

        self._save_session(session)

    def _save_session(self, session: ChatSession) -> None:
        """Internal method to save session.

        Args:
            session: ChatSession to save
        """
        session_file = self._get_session_file(session.session_id)

        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.model_dump(), f, indent=2, default=str)

            logger.debug(f"Saved session: {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            raise

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            logger.warning(f"Session not found for deletion: {session_id}")
            return False

        try:
            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def list_sessions(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[dict]:
        """List all chat sessions.

        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip

        Returns:
            List of session summaries
        """
        session_files = sorted(
            self.storage_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        # Apply offset and limit
        session_files = session_files[offset:]
        if limit:
            session_files = session_files[:limit]

        sessions = []

        for session_file in session_files:
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Create summary
                summary = {
                    "session_id": data["session_id"],
                    "name": data.get("name", "Untitled"),
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "message_count": len(data.get("messages", [])),
                    "last_message": (
                        data["messages"][-1]["content"][:100]
                        if data.get("messages")
                        else None
                    ),
                }

                sessions.append(summary)

            except Exception as e:
                logger.error(f"Failed to load session summary from {session_file}: {e}")
                continue

        logger.info(f"Listed {len(sessions)} sessions")

        return sessions

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[list[dict]] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[ChatSession]:
        """Add a message to a session.

        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: Source citations (for assistant messages)
            metadata: Message metadata

        Returns:
            Updated ChatSession, or None if session not found
        """
        session = self.load_session(session_id)

        if not session:
            return None

        message = ChatMessage(
            role=role,
            content=content,
            sources=sources,
            metadata=metadata or {},
        )

        session.messages.append(message)
        self.save_session(session)

        logger.info(f"Added {role} message to session {session_id}")

        return session

    def get_conversation_history(
        self,
        session_id: str,
        max_messages: Optional[int] = None,
    ) -> list[ChatMessage]:
        """Get conversation history for a session.

        Args:
            session_id: Session ID
            max_messages: Maximum number of recent messages to return

        Returns:
            List of ChatMessage objects
        """
        session = self.load_session(session_id)

        if not session:
            return []

        messages = session.messages

        if max_messages:
            messages = messages[-max_messages:]

        return messages

    def _get_session_file(self, session_id: str) -> Path:
        """Get file path for a session.

        Args:
            session_id: Session ID

        Returns:
            Path to session file
        """
        return self.storage_dir / f"{session_id}.json"

    def clear_all_sessions(self) -> int:
        """Clear all sessions (use with caution).

        Returns:
            Number of sessions deleted
        """
        session_files = list(self.storage_dir.glob("*.json"))
        count = 0

        for session_file in session_files:
            try:
                session_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete {session_file}: {e}")

        logger.warning(f"Cleared {count} sessions")

        return count


def create_session_manager(storage_dir: Optional[Path] = None) -> SessionManager:
    """Create session manager.

    Args:
        storage_dir: Storage directory (default: from settings)

    Returns:
        SessionManager instance
    """
    return SessionManager(storage_dir=storage_dir)
