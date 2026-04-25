"""Vector store setup using ChromaDB."""

import logging
from pathlib import Path
from typing import Optional

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manage ChromaDB vector store."""

    def __init__(
        self,
        persist_dir: Optional[Path] = None,
        collection_name: str = "documents",
    ):
        """Initialize vector store manager.

        Args:
            persist_dir: Directory for persistent storage (default: from settings)
            collection_name: Name of the collection
        """
        self.persist_dir = persist_dir or settings.vector_store_dir
        self.collection_name = collection_name

        # Ensure directory exists
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir)
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )

        # Create vector store
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.collection
        )

        logger.info(f"Initialized ChromaDB at {self.persist_dir}, collection: {collection_name}")

    def get_storage_context(self) -> StorageContext:
        """Get storage context for LlamaIndex.

        Returns:
            StorageContext with ChromaDB vector store
        """
        return StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def get_collection_stats(self) -> dict[str, any]:
        """Get statistics about the collection.

        Returns:
            Dictionary with collection stats
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_dir": str(self.persist_dir),
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e),
            }

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Delete and recreate collection
            self.chroma_client.delete_collection(name=self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name
            )
            self.vector_store = ChromaVectorStore(
                chroma_collection=self.collection
            )
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise

    def delete_documents(self, doc_ids: list[str]) -> None:
        """Delete specific documents from the collection.

        Args:
            doc_ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents from collection")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise


def create_vector_store_manager(
    collection_name: str = "documents",
) -> VectorStoreManager:
    """Create vector store manager.

    Args:
        collection_name: Name of the collection

    Returns:
        VectorStoreManager instance
    """
    return VectorStoreManager(
        persist_dir=settings.vector_store_dir,
        collection_name=collection_name,
    )
