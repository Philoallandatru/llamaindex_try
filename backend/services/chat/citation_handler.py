"""Citation handler for extracting and formatting source citations."""

import logging
from typing import Any, Optional

from llama_index.core.schema import NodeWithScore

from backend.models.chat import Citation

logger = logging.getLogger(__name__)


class CitationHandler:
    """Handle source citation extraction and formatting."""

    @staticmethod
    def extract_citations(
        source_nodes: Optional[list[NodeWithScore]],
        max_citations: int = 5,
    ) -> list[Citation]:
        """Extract citations from source nodes.

        Args:
            source_nodes: List of source nodes with scores
            max_citations: Maximum number of citations to return

        Returns:
            List of Citation objects
        """
        if not source_nodes:
            return []

        citations = []

        for node_with_score in source_nodes[:max_citations]:
            node = node_with_score.node
            score = node_with_score.score or 0.0

            # Extract metadata
            metadata = node.metadata or {}

            # Create citation
            citation = Citation(
                source_id=metadata.get("source_id", node.node_id),
                source_type=metadata.get("source_type", "unknown"),
                title=metadata.get("title", metadata.get("source", "Untitled")),
                url=metadata.get("url"),
                snippet=CitationHandler._create_snippet(node.get_content()),
                relevance_score=float(score),
                metadata=metadata,
            )

            citations.append(citation)

        # Sort by relevance score
        citations.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.info(f"Extracted {len(citations)} citations")

        return citations

    @staticmethod
    def _create_snippet(text: str, max_length: int = 200) -> str:
        """Create a snippet from text.

        Args:
            text: Full text
            max_length: Maximum snippet length

        Returns:
            Text snippet
        """
        if len(text) <= max_length:
            return text

        # Try to cut at sentence boundary
        snippet = text[:max_length]
        last_period = snippet.rfind(".")
        last_question = snippet.rfind("?")
        last_exclamation = snippet.rfind("!")

        last_sentence_end = max(last_period, last_question, last_exclamation)

        if last_sentence_end > max_length * 0.5:
            # Cut at sentence boundary if it's not too short
            return snippet[: last_sentence_end + 1]
        else:
            # Cut at word boundary
            last_space = snippet.rfind(" ")
            if last_space > 0:
                return snippet[:last_space] + "..."
            else:
                return snippet + "..."

    @staticmethod
    def deduplicate_citations(citations: list[Citation]) -> list[Citation]:
        """Remove duplicate citations based on source_id.

        Args:
            citations: List of citations

        Returns:
            Deduplicated list of citations
        """
        seen_ids = set()
        unique_citations = []

        for citation in citations:
            if citation.source_id not in seen_ids:
                seen_ids.add(citation.source_id)
                unique_citations.append(citation)

        logger.info(f"Deduplicated {len(citations)} -> {len(unique_citations)} citations")

        return unique_citations

    @staticmethod
    def format_citations_markdown(citations: list[Citation]) -> str:
        """Format citations as markdown.

        Args:
            citations: List of citations

        Returns:
            Markdown formatted citations
        """
        if not citations:
            return ""

        lines = ["## Sources\n"]

        for idx, citation in enumerate(citations, start=1):
            # Title with link if available
            if citation.url:
                title_line = f"{idx}. [{citation.title}]({citation.url})"
            else:
                title_line = f"{idx}. {citation.title}"

            lines.append(title_line)

            # Source type and score
            lines.append(f"   - Type: {citation.source_type}")
            lines.append(f"   - Relevance: {citation.relevance_score:.2f}")

            # Snippet
            lines.append(f"   - Snippet: {citation.snippet}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_citations_html(citations: list[Citation]) -> str:
        """Format citations as HTML.

        Args:
            citations: List of citations

        Returns:
            HTML formatted citations
        """
        if not citations:
            return ""

        html_parts = ['<div class="citations">']
        html_parts.append("<h3>Sources</h3>")
        html_parts.append("<ol>")

        for citation in citations:
            html_parts.append("<li>")

            # Title with link
            if citation.url:
                html_parts.append(
                    f'<a href="{citation.url}" target="_blank">{citation.title}</a>'
                )
            else:
                html_parts.append(f"<strong>{citation.title}</strong>")

            # Metadata
            html_parts.append(
                f'<div class="citation-meta">'
                f'Type: {citation.source_type} | '
                f'Relevance: {citation.relevance_score:.2f}'
                f'</div>'
            )

            # Snippet
            html_parts.append(f'<div class="citation-snippet">{citation.snippet}</div>')

            html_parts.append("</li>")

        html_parts.append("</ol>")
        html_parts.append("</div>")

        return "\n".join(html_parts)

    @staticmethod
    def citations_to_dict(citations: list[Citation]) -> list[dict[str, Any]]:
        """Convert citations to dictionary format.

        Args:
            citations: List of citations

        Returns:
            List of citation dictionaries
        """
        return [citation.model_dump() for citation in citations]
