"""Query engine with citation support and streaming."""

import logging
from typing import AsyncIterator, Optional

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode, get_response_synthesizer
from llama_index.core.schema import NodeWithScore

from .index_manager import IndexManager

logger = logging.getLogger(__name__)


class CitationQueryEngine:
    """Query engine with source citation tracking."""

    def __init__(
        self,
        index_manager: IndexManager,
        similarity_top_k: int = 5,
        retrieval_mode: str = "hybrid",
        response_mode: ResponseMode = ResponseMode.COMPACT,
    ):
        """Initialize citation query engine.

        Args:
            index_manager: Index manager instance
            similarity_top_k: Number of documents to retrieve
            retrieval_mode: Retrieval mode ("hybrid", "vector", "bm25")
            response_mode: Response synthesis mode
        """
        self.index_manager = index_manager
        self.similarity_top_k = similarity_top_k
        self.retrieval_mode = retrieval_mode

        # Get retriever
        self.retriever = index_manager.get_retriever(
            similarity_top_k=similarity_top_k,
            retrieval_mode=retrieval_mode,
        )

        # Create response synthesizer
        self.response_synthesizer = get_response_synthesizer(
            llm=index_manager.llm,
            response_mode=response_mode,
        )

        # Create query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=self.response_synthesizer,
        )

        logger.info(
            f"Initialized CitationQueryEngine with {retrieval_mode} retrieval, "
            f"top_k={similarity_top_k}"
        )

    def query(self, query_str: str) -> dict[str, any]:
        """Query with citation tracking.

        Args:
            query_str: Query string

        Returns:
            Dictionary with response and sources:
            {
                "response": str,
                "sources": list[dict],
                "metadata": dict
            }
        """
        logger.info(f"Querying: {query_str[:100]}...")

        # Execute query
        response = self.query_engine.query(query_str)

        # Extract sources
        sources = self._extract_sources(response.source_nodes)

        return {
            "response": str(response),
            "sources": sources,
            "metadata": {
                "retrieval_mode": self.retrieval_mode,
                "num_sources": len(sources),
            },
        }

    async def aquery(self, query_str: str) -> dict[str, any]:
        """Async query with citation tracking.

        Args:
            query_str: Query string

        Returns:
            Dictionary with response and sources
        """
        logger.info(f"Async querying: {query_str[:100]}...")

        # Execute async query
        response = await self.query_engine.aquery(query_str)

        # Extract sources
        sources = self._extract_sources(response.source_nodes)

        return {
            "response": str(response),
            "sources": sources,
            "metadata": {
                "retrieval_mode": self.retrieval_mode,
                "num_sources": len(sources),
            },
        }

    async def stream_query(self, query_str: str) -> AsyncIterator[str]:
        """Stream query response.

        Args:
            query_str: Query string

        Yields:
            Response chunks
        """
        logger.info(f"Streaming query: {query_str[:100]}...")

        # Get streaming response
        streaming_response = self.query_engine.query(query_str)

        # Stream response
        async for chunk in streaming_response.async_response_gen():
            yield chunk

    def _extract_sources(
        self,
        source_nodes: Optional[list[NodeWithScore]],
    ) -> list[dict[str, any]]:
        """Extract source information from nodes.

        Args:
            source_nodes: List of source nodes with scores

        Returns:
            List of source dictionaries
        """
        if not source_nodes:
            return []

        sources = []
        for node_with_score in source_nodes:
            node = node_with_score.node
            score = node_with_score.score

            # Extract metadata
            metadata = node.metadata or {}

            source = {
                "source_id": metadata.get("source_id", ""),
                "source_type": metadata.get("source_type", "unknown"),
                "title": metadata.get("title", metadata.get("source", "Untitled")),
                "url": metadata.get("url", ""),
                "snippet": node.get_content()[:200] + "...",
                "relevance_score": float(score) if score is not None else 0.0,
                "metadata": metadata,
            }

            sources.append(source)

        # Sort by relevance score
        sources.sort(key=lambda x: x["relevance_score"], reverse=True)

        return sources


def create_citation_query_engine(
    index_manager: IndexManager,
    similarity_top_k: int = 5,
    retrieval_mode: str = "hybrid",
) -> CitationQueryEngine:
    """Create citation query engine.

    Args:
        index_manager: Index manager instance
        similarity_top_k: Number of documents to retrieve
        retrieval_mode: Retrieval mode

    Returns:
        CitationQueryEngine instance
    """
    return CitationQueryEngine(
        index_manager=index_manager,
        similarity_top_k=similarity_top_k,
        retrieval_mode=retrieval_mode,
    )
