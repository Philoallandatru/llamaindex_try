"""Base data source interface."""

from abc import ABC, abstractmethod
from typing import List, Tuple

from llama_index.core import Document


class BaseDataSource(ABC):
    """Base class for all data sources."""

    @abstractmethod
    async def validate_config(self) -> Tuple[bool, str]:
        """Validate data source configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def fetch_documents(self) -> List[Document]:
        """Fetch documents from the data source.

        Returns:
            List of LlamaIndex Document objects
        """
        pass

    @abstractmethod
    async def get_document_count(self) -> int:
        """Get the number of documents in the data source.

        Returns:
            Document count
        """
        pass
