"""Index manager for orchestrating document indexing and retrieval."""

import logging
from pathlib import Path
from typing import Optional

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.retrievers import BaseRetriever

from .bm25_retriever import BM25Retriever, create_bm25_retriever
from .embeddings import get_embedding_model
from .hybrid_retriever import HybridRetriever, create_hybrid_retriever
from .llm_config import get_llm
from .vector_store import VectorStoreManager, create_vector_store_manager

logger = logging.getLogger(__name__)


class IndexManager:
    """Manage document indexing and retrieval."""

    def __init__(
        self,
        collection_name: str = "documents",
        use_hybrid: bool = True,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
    ):
        """Initialize index manager.

        Args:
            collection_name: Name of the vector store collection
            use_hybrid: Whether to use hybrid retrieval (BM25 + vector)
            bm25_weight: Weight for BM25 in hybrid retrieval
            vector_weight: Weight for vector search in hybrid retrieval
        """
        self.collection_name = collection_name
        self.use_hybrid = use_hybrid
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight

        # Initialize components
        self.llm = get_llm()
        self.embed_model = get_embedding_model()
        self.vector_store_manager = create_vector_store_manager(collection_name)

        # Index and retrievers (initialized when documents are added)
        self.vector_index: Optional[VectorStoreIndex] = None
        self.bm25_retriever: Optional[BM25Retriever] = None
        self.documents: list[Document] = []

        logger.info(f"Initialized IndexManager for collection: {collection_name}")

    async def add_documents(
        self,
        documents: list[Document],
        show_progress: bool = True,
    ) -> None:
        """Add documents to the index.

        Args:
            documents: List of LlamaIndex Documents
            show_progress: Whether to show progress bar
        """
        if not documents:
            logger.warning("No documents to add")
            return

        logger.info(f"Adding {len(documents)} documents to index")

        # Store documents
        self.documents.extend(documents)

        # Build vector index
        storage_context = self.vector_store_manager.get_storage_context()

        if self.vector_index is None:
            # Create new index
            self.vector_index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=self.embed_model,
                show_progress=show_progress,
            )
        else:
            # Add to existing index
            for doc in documents:
                self.vector_index.insert(doc)

        # Build BM25 index
        if self.use_hybrid:
            self.bm25_retriever = create_bm25_retriever(
                self.documents,
                similarity_top_k=5,
            )

        logger.info(f"Successfully added {len(documents)} documents")

    async def update_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Update existing documents in the index.

        Args:
            documents: List of documents to update
        """
        # For now, we'll delete and re-add
        # TODO: Implement proper update logic
        doc_ids = [doc.doc_id for doc in documents]
        await self.delete_documents(doc_ids)
        await self.add_documents(documents)

    async def delete_documents(self, doc_ids: list[str]) -> None:
        """Delete documents from the index.

        Args:
            doc_ids: List of document IDs to delete
        """
        logger.info(f"Deleting {len(doc_ids)} documents")

        # Delete from vector store
        self.vector_store_manager.delete_documents(doc_ids)

        # Remove from local documents list
        self.documents = [doc for doc in self.documents if doc.doc_id not in doc_ids]

        # Rebuild BM25 index
        if self.use_hybrid and self.documents:
            self.bm25_retriever = create_bm25_retriever(
                self.documents,
                similarity_top_k=5,
            )

        logger.info(f"Successfully deleted {len(doc_ids)} documents")

    def get_retriever(
        self,
        similarity_top_k: int = 5,
        retrieval_mode: str = "hybrid",
    ) -> BaseRetriever:
        """Get retriever for querying.

        Args:
            similarity_top_k: Number of results to return
            retrieval_mode: Retrieval mode ("hybrid", "vector", "bm25")

        Returns:
            BaseRetriever instance

        Raises:
            ValueError: If index is not built or mode is invalid
        """
        if self.vector_index is None:
            raise ValueError("Index not built. Add documents first.")

        if retrieval_mode == "vector":
            # Vector-only retrieval
            return self.vector_index.as_retriever(
                similarity_top_k=similarity_top_k,
            )

        elif retrieval_mode == "bm25":
            # BM25-only retrieval
            if self.bm25_retriever is None:
                raise ValueError("BM25 retriever not available")
            self.bm25_retriever._similarity_top_k = similarity_top_k
            return self.bm25_retriever

        elif retrieval_mode == "hybrid":
            # Hybrid retrieval
            if self.bm25_retriever is None:
                raise ValueError("BM25 retriever not available for hybrid mode")

            vector_retriever = self.vector_index.as_retriever(
                similarity_top_k=similarity_top_k,
            )

            return create_hybrid_retriever(
                bm25_retriever=self.bm25_retriever,
                vector_retriever=vector_retriever,
                bm25_weight=self.bm25_weight,
                vector_weight=self.vector_weight,
                similarity_top_k=similarity_top_k,
            )

        else:
            raise ValueError(f"Invalid retrieval mode: {retrieval_mode}")

    def get_query_engine(
        self,
        similarity_top_k: int = 5,
        retrieval_mode: str = "hybrid",
    ):
        """Get query engine for Q&A.

        Args:
            similarity_top_k: Number of results to retrieve
            retrieval_mode: Retrieval mode ("hybrid", "vector", "bm25")

        Returns:
            Query engine instance
        """
        if self.vector_index is None:
            raise ValueError("Index not built. Add documents first.")

        retriever = self.get_retriever(
            similarity_top_k=similarity_top_k,
            retrieval_mode=retrieval_mode,
        )

        # Create query engine with custom retriever
        query_engine = self.vector_index.as_query_engine(
            llm=self.llm,
            retriever=retriever,
        )

        return query_engine

    def get_stats(self) -> dict[str, any]:
        """Get index statistics.

        Returns:
            Dictionary with index stats
        """
        vector_stats = self.vector_store_manager.get_collection_stats()

        return {
            "collection_name": self.collection_name,
            "total_documents": len(self.documents),
            "vector_store": vector_stats,
            "bm25_enabled": self.bm25_retriever is not None,
            "hybrid_enabled": self.use_hybrid,
            "retrieval_modes": ["vector", "bm25", "hybrid"] if self.use_hybrid else ["vector"],
        }

    async def clear_index(self) -> None:
        """Clear all documents from the index."""
        logger.info("Clearing index")

        self.vector_store_manager.clear_collection()
        self.documents = []
        self.vector_index = None
        self.bm25_retriever = None

        logger.info("Index cleared")


def create_index_manager(
    collection_name: str = "documents",
    use_hybrid: bool = True,
    bm25_weight: float = 0.5,
    vector_weight: float = 0.5,
) -> IndexManager:
    """Create index manager.

    Args:
        collection_name: Name of the collection
        use_hybrid: Whether to use hybrid retrieval
        bm25_weight: Weight for BM25 scores
        vector_weight: Weight for vector scores

    Returns:
        IndexManager instance
    """
    return IndexManager(
        collection_name=collection_name,
        use_hybrid=use_hybrid,
        bm25_weight=bm25_weight,
        vector_weight=vector_weight,
    )
