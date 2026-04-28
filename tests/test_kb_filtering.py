"""Test knowledge base filtering functionality."""

import pytest
from llama_index.core import Document

from backend.services.indexing.index_manager import IndexManager


@pytest.mark.asyncio
async def test_kb_filtering():
    """Test that metadata filtering works correctly."""
    # Create index manager
    index_manager = IndexManager(
        collection_name="test_kb_filtering",
        use_hybrid=True,
    )

    # Create test documents with different knowledge base IDs
    docs_kb1 = [
        Document(
            text="This is a document about Python programming.",
            metadata={"knowledge_base_id": "kb_1", "source": "doc1.pdf"},
        ),
        Document(
            text="Python is a high-level programming language.",
            metadata={"knowledge_base_id": "kb_1", "source": "doc2.pdf"},
        ),
    ]

    docs_kb2 = [
        Document(
            text="This is a document about Java programming.",
            metadata={"knowledge_base_id": "kb_2", "source": "doc3.pdf"},
        ),
        Document(
            text="Java is an object-oriented programming language.",
            metadata={"knowledge_base_id": "kb_2", "source": "doc4.pdf"},
        ),
    ]

    # Add all documents to the index
    await index_manager.add_documents(docs_kb1 + docs_kb2, show_progress=False)

    # Test 1: Query without filters (should return results from both KBs)
    retriever_all = index_manager.get_retriever(
        similarity_top_k=4,
        retrieval_mode="vector",
        filters=None,
    )
    results_all = retriever_all.retrieve("programming language")
    assert len(results_all) > 0, "Should retrieve documents without filters"
    print(f"[PASS] Test 1: Retrieved {len(results_all)} documents without filters")

    # Test 2: Query with kb_1 filter (should only return Python docs)
    retriever_kb1 = index_manager.get_retriever(
        similarity_top_k=4,
        retrieval_mode="vector",
        filters={"knowledge_base_id": "kb_1"},
    )
    results_kb1 = retriever_kb1.retrieve("programming language")
    assert len(results_kb1) > 0, "Should retrieve documents from kb_1"
    for node in results_kb1:
        kb_id = node.metadata.get("knowledge_base_id")
        assert kb_id == "kb_1", f"Expected kb_1, got {kb_id}"
    print(f"[PASS] Test 2: Retrieved {len(results_kb1)} documents from kb_1 only")

    # Test 3: Query with kb_2 filter (should only return Java docs)
    retriever_kb2 = index_manager.get_retriever(
        similarity_top_k=4,
        retrieval_mode="vector",
        filters={"knowledge_base_id": "kb_2"},
    )
    results_kb2 = retriever_kb2.retrieve("programming language")
    assert len(results_kb2) > 0, "Should retrieve documents from kb_2"
    for node in results_kb2:
        kb_id = node.metadata.get("knowledge_base_id")
        assert kb_id == "kb_2", f"Expected kb_2, got {kb_id}"
    print(f"[PASS] Test 3: Retrieved {len(results_kb2)} documents from kb_2 only")

    # Test 4: Verify content is correct
    kb1_texts = [node.text for node in results_kb1]
    assert any("Python" in text for text in kb1_texts), "kb_1 results should mention Python"
    assert not any("Java" in text for text in kb1_texts), "kb_1 results should not mention Java"
    print("[PASS] Test 4: Content filtering is correct")

    # Cleanup
    await index_manager.clear_index()
    print("\n[SUCCESS] All tests passed! Knowledge base filtering works correctly.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_kb_filtering())
