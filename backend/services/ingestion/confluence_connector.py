"""Confluence connector using atlassian-python-api."""

import logging
from typing import Optional

from atlassian import Confluence
from llama_index.core import Document

from ..ingestion.normalizer import DocumentNormalizer

logger = logging.getLogger(__name__)


class ConfluenceConnector:
    """Connector for fetching Confluence pages."""

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
    ):
        """Initialize Confluence connector.

        Args:
            base_url: Confluence instance URL (e.g., https://your-domain.atlassian.net/wiki)
            email: User email
            api_token: API token from Confluence
        """
        self.base_url = base_url
        self.confluence = Confluence(
            url=base_url,
            username=email,
            password=api_token,
            cloud=True,
        )

    async def test_connection(self) -> dict[str, any]:
        """Test Confluence connection.

        Returns:
            Dictionary with connection status:
            {
                "success": bool,
                "message": str,
                "user": str (if successful)
            }
        """
        try:
            user = self.confluence.get_current_user()
            return {
                "success": True,
                "message": "Connection successful",
                "user": user.get("displayName", "Unknown"),
            }
        except Exception as e:
            logger.error(f"Confluence connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
            }

    async def fetch_page(self, page_id: str) -> Document:
        """Fetch a single Confluence page.

        Args:
            page_id: Page ID

        Returns:
            LlamaIndex Document

        Raises:
            RuntimeError: If fetch fails
        """
        try:
            page = self.confluence.get_page_by_id(
                page_id,
                expand="body.storage,version,space,history",
            )
            return DocumentNormalizer.normalize_confluence_page(page)
        except Exception as e:
            logger.error(f"Failed to fetch page {page_id}: {e}")
            raise RuntimeError(f"Failed to fetch Confluence page: {e}")

    async def fetch_page_by_title(
        self,
        space_key: str,
        title: str,
    ) -> Document:
        """Fetch a page by title.

        Args:
            space_key: Space key
            title: Page title

        Returns:
            LlamaIndex Document

        Raises:
            RuntimeError: If fetch fails
        """
        try:
            page = self.confluence.get_page_by_title(
                space=space_key,
                title=title,
                expand="body.storage,version,space,history",
            )
            if not page:
                raise RuntimeError(f"Page not found: {title}")
            return DocumentNormalizer.normalize_confluence_page(page)
        except Exception as e:
            logger.error(f"Failed to fetch page '{title}' in space {space_key}: {e}")
            raise RuntimeError(f"Failed to fetch Confluence page: {e}")

    async def fetch_space(
        self,
        space_key: str,
        max_pages: int = 100,
    ) -> list[Document]:
        """Fetch all pages from a Confluence space.

        Args:
            space_key: Space key
            max_pages: Maximum number of pages to fetch

        Returns:
            List of LlamaIndex Documents
        """
        try:
            documents = []
            start = 0
            limit = 25  # Confluence API limit per request

            while len(documents) < max_pages:
                pages = self.confluence.get_all_pages_from_space(
                    space=space_key,
                    start=start,
                    limit=limit,
                    expand="body.storage,version,space,history",
                )

                if not pages:
                    break

                # Normalize pages
                page_docs = DocumentNormalizer.normalize_batch(pages, "confluence")
                documents.extend(page_docs)

                if len(pages) < limit:
                    break

                start += limit

            logger.info(f"Fetched {len(documents)} pages from space {space_key}")
            return documents[:max_pages]

        except Exception as e:
            logger.error(f"Failed to fetch space {space_key}: {e}")
            raise RuntimeError(f"Failed to fetch Confluence space: {e}")

    async def fetch_pages_by_label(
        self,
        space_key: str,
        label: str,
        max_pages: int = 100,
    ) -> list[Document]:
        """Fetch pages with a specific label.

        Args:
            space_key: Space key
            label: Label name
            max_pages: Maximum number of pages

        Returns:
            List of LlamaIndex Documents
        """
        try:
            # Use CQL (Confluence Query Language)
            cql = f'space = "{space_key}" AND label = "{label}"'
            results = self.confluence.cql(
                cql,
                limit=max_pages,
                expand="body.storage,version,space,history",
            )

            pages = results.get("results", [])
            documents = []

            for result in pages:
                content = result.get("content", {})
                if content:
                    doc = DocumentNormalizer.normalize_confluence_page(content)
                    documents.append(doc)

            logger.info(f"Fetched {len(documents)} pages with label '{label}'")
            return documents

        except Exception as e:
            logger.error(f"Failed to fetch pages with label '{label}': {e}")
            raise RuntimeError(f"Failed to fetch Confluence pages: {e}")

    async def fetch_updated_since(
        self,
        space_key: str,
        since_date: str,
        max_pages: int = 100,
    ) -> list[Document]:
        """Fetch pages updated since a specific date.

        Args:
            space_key: Space key
            since_date: Date in format "YYYY-MM-DD"
            max_pages: Maximum number of pages

        Returns:
            List of LlamaIndex Documents
        """
        try:
            cql = f'space = "{space_key}" AND lastModified >= "{since_date}"'
            results = self.confluence.cql(
                cql,
                limit=max_pages,
                expand="body.storage,version,space,history",
            )

            pages = results.get("results", [])
            documents = []

            for result in pages:
                content = result.get("content", {})
                if content:
                    doc = DocumentNormalizer.normalize_confluence_page(content)
                    documents.append(doc)

            logger.info(f"Fetched {len(documents)} pages updated since {since_date}")
            return documents

        except Exception as e:
            logger.error(f"Failed to fetch updated pages: {e}")
            raise RuntimeError(f"Failed to fetch Confluence pages: {e}")

    def get_spaces(self) -> list[dict[str, str]]:
        """Get list of available spaces.

        Returns:
            List of spaces with keys and names
        """
        try:
            spaces = self.confluence.get_all_spaces(limit=100)
            return [
                {
                    "key": s.get("key", ""),
                    "name": s.get("name", ""),
                    "id": s.get("id", ""),
                }
                for s in spaces.get("results", [])
            ]
        except Exception as e:
            logger.error(f"Failed to get spaces: {e}")
            return []
