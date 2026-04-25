"""Document normalizer to convert various sources to LlamaIndex format."""

import logging
from datetime import datetime
from typing import Any, Optional

from llama_index.core import Document

logger = logging.getLogger(__name__)


class DocumentNormalizer:
    """Normalize documents from various sources to LlamaIndex Document format."""

    @staticmethod
    def normalize_jira_issue(issue_data: dict[str, Any]) -> Document:
        """Convert Jira issue to LlamaIndex Document.

        Args:
            issue_data: Raw Jira issue data

        Returns:
            LlamaIndex Document
        """
        fields = issue_data.get("fields", {})

        # Build text content
        text_parts = [
            f"Issue: {issue_data.get('key', 'Unknown')}",
            f"Summary: {fields.get('summary', '')}",
            f"Type: {fields.get('issuetype', {}).get('name', '')}",
            f"Status: {fields.get('status', {}).get('name', '')}",
            f"Priority: {fields.get('priority', {}).get('name', '')}",
            "",
            "Description:",
            fields.get("description", "No description"),
        ]

        # Add comments if available
        comments = fields.get("comment", {}).get("comments", [])
        if comments:
            text_parts.append("\nComments:")
            for comment in comments:
                author = comment.get("author", {}).get("displayName", "Unknown")
                body = comment.get("body", "")
                text_parts.append(f"- {author}: {body}")

        text = "\n".join(text_parts)

        # Build metadata
        metadata = {
            "source": issue_data.get("self", ""),
            "source_type": "jira",
            "source_id": issue_data.get("key", ""),
            "title": fields.get("summary", ""),
            "url": f"{issue_data.get('self', '').split('/rest/')[0]}/browse/{issue_data.get('key', '')}",
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "status": fields.get("status", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
            "reporter": fields.get("reporter", {}).get("displayName", "Unknown"),
        }

        return Document(text=text, metadata=metadata)

    @staticmethod
    def normalize_confluence_page(page_data: dict[str, Any]) -> Document:
        """Convert Confluence page to LlamaIndex Document.

        Args:
            page_data: Raw Confluence page data

        Returns:
            LlamaIndex Document
        """
        # Extract content
        body = page_data.get("body", {})
        storage = body.get("storage", {})
        content = storage.get("value", "")

        # Build text (strip HTML tags for now, could use BeautifulSoup for better parsing)
        import re
        text = re.sub(r"<[^>]+>", "", content)

        # Build full text with title
        title = page_data.get("title", "Untitled")
        full_text = f"# {title}\n\n{text}"

        # Build metadata
        space = page_data.get("space", {})
        metadata = {
            "source": page_data.get("_links", {}).get("self", ""),
            "source_type": "confluence",
            "source_id": page_data.get("id", ""),
            "title": title,
            "url": page_data.get("_links", {}).get("webui", ""),
            "space_key": space.get("key", ""),
            "space_name": space.get("name", ""),
            "created": page_data.get("history", {}).get("createdDate", ""),
            "updated": page_data.get("version", {}).get("when", ""),
            "creator": page_data.get("history", {}).get("createdBy", {}).get("displayName", "Unknown"),
        }

        return Document(text=full_text, metadata=metadata)

    @staticmethod
    def add_timestamp(document: Document) -> Document:
        """Add ingestion timestamp to document metadata.

        Args:
            document: LlamaIndex Document

        Returns:
            Document with timestamp added
        """
        document.metadata["ingested_at"] = datetime.utcnow().isoformat()
        return document

    @staticmethod
    def chunk_document(
        document: Document,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
    ) -> list[Document]:
        """Chunk a document into smaller pieces.

        Args:
            document: LlamaIndex Document
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of chunked Documents
        """
        from llama_index.core.node_parser import SentenceSplitter

        splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        nodes = splitter.get_nodes_from_documents([document])

        # Convert nodes back to documents
        chunked_docs = []
        for idx, node in enumerate(nodes):
            chunk_doc = Document(
                text=node.get_content(),
                metadata={
                    **document.metadata,
                    "chunk_index": idx,
                    "total_chunks": len(nodes),
                },
            )
            chunked_docs.append(chunk_doc)

        return chunked_docs

    @staticmethod
    def normalize_batch(
        items: list[dict[str, Any]],
        source_type: str,
    ) -> list[Document]:
        """Normalize a batch of items from a specific source.

        Args:
            items: List of raw items
            source_type: Type of source (jira, confluence)

        Returns:
            List of normalized Documents
        """
        documents = []

        for item in items:
            try:
                if source_type == "jira":
                    doc = DocumentNormalizer.normalize_jira_issue(item)
                elif source_type == "confluence":
                    doc = DocumentNormalizer.normalize_confluence_page(item)
                else:
                    logger.warning(f"Unknown source type: {source_type}")
                    continue

                doc = DocumentNormalizer.add_timestamp(doc)
                documents.append(doc)

            except Exception as e:
                logger.error(f"Failed to normalize item: {e}")
                continue

        return documents
