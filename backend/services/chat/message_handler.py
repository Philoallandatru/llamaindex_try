"""Message handler for input validation and routing."""

import logging
from typing import Optional

from backend.models.chat import SendMessageRequest

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handle message validation and routing."""

    @staticmethod
    def validate_message(message: str) -> tuple[bool, Optional[str]]:
        """Validate user message.

        Args:
            message: User message

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if message is empty
        if not message or not message.strip():
            return False, "Message cannot be empty"

        # Check message length
        if len(message) > 10000:
            return False, "Message is too long (max 10000 characters)"

        # Check for suspicious content (basic)
        suspicious_patterns = [
            "ignore previous instructions",
            "disregard all",
            "forget everything",
        ]

        message_lower = message.lower()
        for pattern in suspicious_patterns:
            if pattern in message_lower:
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return False, "Message contains suspicious content"

        return True, None

    @staticmethod
    def validate_request(request: SendMessageRequest) -> tuple[bool, Optional[str]]:
        """Validate send message request.

        Args:
            request: SendMessageRequest

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate message
        is_valid, error = MessageHandler.validate_message(request.message)
        if not is_valid:
            return False, error

        # Validate session_id
        if not request.session_id:
            return False, "Session ID is required"

        # Validate retrieval_mode
        valid_modes = ["hybrid", "vector", "bm25"]
        if request.retrieval_mode not in valid_modes:
            return False, f"Invalid retrieval mode. Must be one of: {', '.join(valid_modes)}"

        # Validate similarity_top_k
        if request.similarity_top_k < 1 or request.similarity_top_k > 20:
            return False, "similarity_top_k must be between 1 and 20"

        return True, None

    @staticmethod
    def sanitize_message(message: str) -> str:
        """Sanitize user message.

        Args:
            message: User message

        Returns:
            Sanitized message
        """
        # Strip whitespace
        message = message.strip()

        # Remove null bytes
        message = message.replace("\x00", "")

        # Normalize whitespace
        message = " ".join(message.split())

        return message

    @staticmethod
    def format_error_response(error: str) -> dict:
        """Format error response.

        Args:
            error: Error message

        Returns:
            Error response dictionary
        """
        return {
            "error": True,
            "message": error,
            "content": f"Sorry, I encountered an error: {error}",
        }

    @staticmethod
    def should_use_context(message: str, conversation_history: list) -> bool:
        """Determine if conversation context should be used.

        Args:
            message: Current message
            conversation_history: Previous messages

        Returns:
            True if context should be used
        """
        # Always use context if there's history
        if conversation_history:
            return True

        # Check for context-dependent phrases
        context_indicators = [
            "what about",
            "tell me more",
            "explain that",
            "what did you mean",
            "can you elaborate",
            "continue",
            "go on",
            "what else",
            "also",
            "additionally",
        ]

        message_lower = message.lower()
        for indicator in context_indicators:
            if indicator in message_lower:
                return True

        return False

    @staticmethod
    def extract_filters_from_message(message: str) -> dict:
        """Extract source filters from message.

        Args:
            message: User message

        Returns:
            Dictionary of filters
        """
        filters = {}

        message_lower = message.lower()

        # Check for source type filters
        if "jira" in message_lower or "issue" in message_lower:
            filters["source_type"] = "jira"
        elif "confluence" in message_lower or "wiki" in message_lower:
            filters["source_type"] = "confluence"
        elif "pdf" in message_lower or "document" in message_lower:
            filters["source_type"] = "pdf"

        # Check for date filters
        if "recent" in message_lower or "latest" in message_lower:
            filters["sort_by"] = "updated_at"
            filters["order"] = "desc"

        return filters
