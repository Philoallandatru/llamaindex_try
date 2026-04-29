"""Chat engine using LlamaIndex for conversational retrieval."""

import logging
import uuid
from typing import AsyncIterator, Optional

from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer

from backend.models.chat import ChatMessage, ChatResponse, Citation
from backend.services.indexing.index_manager import IndexManager

from .citation_handler import CitationHandler
from .message_handler import MessageHandler
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class ChatEngine:
    """Chat engine with conversation context and retrieval."""

    def __init__(
        self,
        index_manager: IndexManager,
        session_manager: SessionManager,
        context_window: int = 10,
    ):
        """Initialize chat engine.

        Args:
            index_manager: Index manager for retrieval
            session_manager: Session manager for persistence
            context_window: Number of previous messages to include in context
        """
        self.index_manager = index_manager
        self.session_manager = session_manager
        self.context_window = context_window

        logger.info(f"Initialized ChatEngine with context window: {context_window}")

    async def send_message(
        self,
        session_id: str,
        message: str,
        retrieval_mode: str = "hybrid",
        similarity_top_k: int = 5,
        source_filters: Optional[dict] = None,
        knowledge_base_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> ChatResponse:
        """Send a message and get response.

        Args:
            session_id: Session ID
            message: User message
            retrieval_mode: Retrieval mode ('hybrid', 'vector', 'bm25')
            similarity_top_k: Number of sources to retrieve
            source_filters: Filters for source retrieval
            knowledge_base_id: Knowledge base ID (overrides session default)
            model_id: Model ID (overrides session default)

        Returns:
            ChatResponse with assistant message and sources
        """
        # Validate message
        is_valid, error = MessageHandler.validate_message(message)
        if not is_valid:
            raise ValueError(error)

        # Sanitize message
        message = MessageHandler.sanitize_message(message)

        # Load session
        session = self.session_manager.load_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Determine which knowledge base and model to use
        # Priority: request parameter > session default > system default
        effective_kb_id = knowledge_base_id or session.knowledge_base_id
        effective_model_id = model_id or session.model_id

        # Add user message to session
        self.session_manager.add_message(
            session_id=session_id,
            role="user",
            content=message,
        )

        # Get conversation history
        history = self.session_manager.get_conversation_history(
            session_id=session_id,
            max_messages=self.context_window,
        )

        # Create chat engine with context
        chat_engine = self._create_chat_engine(
            retrieval_mode=retrieval_mode,
            similarity_top_k=similarity_top_k,
            conversation_history=history[:-1],  # Exclude current message
            knowledge_base_id=effective_kb_id,
            model_id=effective_model_id,
        )

        # Query
        response = await chat_engine.achat(message)

        # Extract citations
        citations = CitationHandler.extract_citations(
            source_nodes=response.source_nodes,
            max_citations=similarity_top_k,
        )

        # Deduplicate citations
        citations = CitationHandler.deduplicate_citations(citations)

        # Convert to dict
        sources = CitationHandler.citations_to_dict(citations)

        # Add assistant message to session
        self.session_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=str(response),
            sources=sources,
        )

        # Create response
        chat_response = ChatResponse(
            message_id=str(uuid.uuid4()),
            content=str(response),
            sources=sources,
            metadata={
                "retrieval_mode": retrieval_mode,
                "num_sources": len(sources),
                "session_id": session_id,
                "knowledge_base_id": effective_kb_id,
                "model_id": effective_model_id,
            },
        )

        logger.info(f"Generated response for session {session_id} with {len(sources)} sources (KB: {effective_kb_id}, Model: {effective_model_id})")

        return chat_response

    async def stream_message(
        self,
        session_id: str,
        message: str,
        retrieval_mode: str = "hybrid",
        similarity_top_k: int = 5,
        source_filters: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """Stream a message response.

        Args:
            session_id: Session ID
            message: User message
            retrieval_mode: Retrieval mode
            similarity_top_k: Number of sources to retrieve
            source_filters: Filters for source retrieval

        Yields:
            Response chunks
        """
        # Validate message
        is_valid, error = MessageHandler.validate_message(message)
        if not is_valid:
            raise ValueError(error)

        # Sanitize message
        message = MessageHandler.sanitize_message(message)

        # Load session
        session = self.session_manager.load_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Add user message
        self.session_manager.add_message(
            session_id=session_id,
            role="user",
            content=message,
        )

        # Get conversation history
        history = self.session_manager.get_conversation_history(
            session_id=session_id,
            max_messages=self.context_window,
        )

        # Create chat engine
        chat_engine = self._create_chat_engine(
            retrieval_mode=retrieval_mode,
            similarity_top_k=similarity_top_k,
            conversation_history=history[:-1],
        )

        # Stream response
        streaming_response = await chat_engine.astream_chat(message)

        full_response = ""

        async for chunk in streaming_response.async_response_gen():
            full_response += chunk
            yield chunk

        # Extract citations after streaming completes
        citations = CitationHandler.extract_citations(
            source_nodes=streaming_response.source_nodes,
            max_citations=similarity_top_k,
        )

        citations = CitationHandler.deduplicate_citations(citations)
        sources = CitationHandler.citations_to_dict(citations)

        # Add assistant message
        self.session_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=full_response,
            sources=sources,
        )

        logger.info(f"Streamed response for session {session_id}")

    def _create_chat_engine(
        self,
        retrieval_mode: str,
        similarity_top_k: int,
        conversation_history: list[ChatMessage],
        knowledge_base_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> CondensePlusContextChatEngine:
        """Create chat engine with context.

        Args:
            retrieval_mode: Retrieval mode
            similarity_top_k: Number of sources
            conversation_history: Previous messages
            knowledge_base_id: Knowledge base ID (optional, uses default if None)
            model_id: Model ID (optional, uses default if None)

        Returns:
            CondensePlusContextChatEngine
        """
        # Construct metadata filters if knowledge_base_id is provided
        filters = None
        if knowledge_base_id:
            filters = {"knowledge_base_id": knowledge_base_id}
            logger.info(f"Filtering documents by knowledge_base_id: {knowledge_base_id}")

        # Get retriever with filters
        retriever = self.index_manager.get_retriever(
            similarity_top_k=similarity_top_k,
            retrieval_mode=retrieval_mode,
            filters=filters,
        )

        # Create memory buffer
        memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

        # Add conversation history to memory
        for msg in conversation_history:
            memory.put({"role": msg.role, "content": msg.content})

        # Create chat engine
        chat_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,
            llm=self.index_manager.llm,
            memory=memory,
            context_prompt=(
                "You are a helpful assistant that answers questions based on the provided context. "
                "Always cite your sources and be specific. "
                "If you don't know the answer, say so clearly."
            ),
            verbose=True,
        )

        return chat_engine


def create_chat_engine(
    index_manager: IndexManager,
    session_manager: SessionManager,
    context_window: int = 10,
) -> ChatEngine:
    """Create chat engine.

    Args:
        index_manager: Index manager
        session_manager: Session manager
        context_window: Context window size

    Returns:
        ChatEngine instance
    """
    return ChatEngine(
        index_manager=index_manager,
        session_manager=session_manager,
        context_window=context_window,
    )
