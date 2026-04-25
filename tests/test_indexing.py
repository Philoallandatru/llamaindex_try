"""Tests for indexing services."""

import pytest
from llama_index.core import Document

from backend.services.indexing.bm25_retriever import create_bm25_retriever
from backend.services.indexing.index_manager import create_index_manager


class TestBM25Retriever:
    """Test BM25 retriever."""

    def test_create_bm25_retriever(self):
        """Test BM25 retriever creation."""
        documents = [
            Document(text="This is a test document about Python programming."),
            Document(text="Another document discussing machine learning."),
            Document(text="Python is great for data science and AI."),
        ]

        retriever = create_bm25_retriever(documents, similarity_top_k=2)

        assert retriever is not None
        assert len(retriever.nodes) == 3
        assert retriever._similarity_top_k == 2

    def test_bm25_tokenization(self):
        """Test BM25 tokenization."""
        documents = [
            Document(text="Hello world! This is a test."),
        ]

        retriever = create_bm25_retriever(documents)

        # Test tokenization
        tokens = retriever._tokenize("Hello world! This is a test.")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        # Stop words should be removed
        assert "is" not in tokens
        assert "a" not in tokens


@pytest.mark.asyncio
class TestIndexManager:
    """Test index manager."""

    async def test_create_index_manager(self):
        """Test index manager creation."""
        manager = create_index_manager(
            collection_name="test_collection",
            use_hybrid=True,
        )

        assert manager is not None
        assert manager.collection_name == "test_collection"
        assert manager.use_hybrid is True

    async def test_add_documents(self):
        """Test adding documents to index."""
        manager = create_index_manager(collection_name="test_add_docs")

        documents = [
            Document(
                text="Python is a programming language.",
                metadata={"source": "test1"},
            ),
            Document(
                text="Machine learning uses Python.",
                metadata={"source": "test2"},
            ),
        ]

        await manager.add_documents(documents, show_progress=False)

        stats = manager.get_stats()
        assert stats["total_documents"] == 2
        assert stats["bm25_enabled"] is True

    async def test_get_retriever_modes(self):
        """Test different retrieval modes."""
        manager = create_index_manager(collection_name="test_retrieval_modes")

        documents = [
            Document(text="Test document 1"),
            Document(text="Test document 2"),
        ]

        await manager.add_documents(documents, show_progress=False)

        # Test vector retriever
        vector_retriever = manager.get_retriever(retrieval_mode="vector")
        assert vector_retriever is not None

        # Test BM25 retriever
        bm25_retriever = manager.get_retriever(retrieval_mode="bm25")
        assert bm25_retriever is not None

        # Test hybrid retriever
        hybrid_retriever = manager.get_retriever(retrieval_mode="hybrid")
        assert hybrid_retriever is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
