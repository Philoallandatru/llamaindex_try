"""
Test BM25 retriever with custom tokenizer
"""
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.embeddings.openai import OpenAIEmbedding
import re

def simple_tokenizer(text: str) -> list[str]:
    """Simple whitespace tokenizer that handles empty strings"""
    if not text or not text.strip():
        return [""]  # Return single empty token for empty text
    # Split on whitespace and punctuation
    tokens = re.findall(r'\w+', text.lower())
    return tokens if tokens else [""]

def test_bm25():
    """Test BM25 retriever"""

    print("=" * 60)
    print("BM25 Retriever Test")
    print("=" * 60)

    # Setup LM Studio embeddings
    print("[SETUP] Configuring LM Studio embeddings...")
    Settings.embed_model = OpenAIEmbedding(
        api_base="http://localhost:1234/v1",
        api_key="lm-studio",
        model="text-embedding-ada-002"  # Use generic model name for LM Studio
    )

    # Create test documents
    docs = [
        Document(text="NVMe SSD performance degradation after firmware update", metadata={"id": "1"}),
        Document(text="PCIe Gen4 bandwidth issues with NVMe drives", metadata={"id": "2"}),
        Document(text="Firmware v3.3 causes latency increase", metadata={"id": "3"}),
        Document(text="Sequential read performance dropped significantly", metadata={"id": "4"}),
        Document(text="Random IOPS decreased by 25 percent", metadata={"id": "5"}),
    ]

    print(f"[DOCS] Created {len(docs)} test documents")

    # Create index
    print("[INDEX] Building vector index...")
    index = VectorStoreIndex.from_documents(docs)

    # Test 1: BM25 with custom tokenizer
    print("\n[TEST 1] BM25 with custom tokenizer")
    try:
        bm25_retriever = BM25Retriever.from_defaults(
            docstore=index.docstore,
            similarity_top_k=3,
            tokenizer=simple_tokenizer
        )

        query = "firmware performance degradation"
        print(f"[QUERY] {query}")

        results = bm25_retriever.retrieve(query)
        print(f"[RESULTS] Found {len(results)} results")

        for i, node in enumerate(results, 1):
            print(f"\n  {i}. Score: {node.score:.4f}")
            print(f"     Text: {node.text[:80]}...")

        print("\n[PASS] BM25 with custom tokenizer works!")

    except Exception as e:
        print(f"[FAIL] BM25 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: BM25 with default tokenizer
    print("\n[TEST 2] BM25 with default tokenizer")
    try:
        bm25_default = BM25Retriever.from_defaults(
            docstore=index.docstore,
            similarity_top_k=3
        )

        results = bm25_default.retrieve(query)
        print(f"[RESULTS] Found {len(results)} results")
        print("[PASS] BM25 with default tokenizer works!")

    except Exception as e:
        print(f"[FAIL] BM25 default failed: {e}")
        import traceback
        traceback.print_exc()

    return True

if __name__ == "__main__":
    print()
    success = test_bm25()
    print()
    print("=" * 60)
    if success:
        print("[PASS] BM25 test passed")
    else:
        print("[FAIL] BM25 test failed")
    print("=" * 60)
