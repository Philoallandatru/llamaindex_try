# Indexing Services

This module handles document indexing, retrieval, and query processing using LlamaIndex.

## Components

### 1. LLM Configuration (`llm_config.py`)
- Configures LM Studio OpenAI-compatible LLM
- Supports custom model, temperature, max_tokens
- Connection testing

### 2. Embedding Model (`embeddings.py`)
- HuggingFace embeddings for local inference
- Default: `BAAI/bge-small-zh-v1.5` (Chinese + English)
- No API calls required

### 3. Vector Store (`vector_store.py`)
- ChromaDB persistent vector storage
- Collection management
- Document CRUD operations

### 4. BM25 Retriever (`bm25_retriever.py`)
- **Keyword-based full-text search**
- BM25 probabilistic ranking algorithm
- Configurable k1 (term frequency saturation) and b (length normalization)
- Stop word filtering
- Excellent for exact keyword matching

### 5. Hybrid Retriever (`hybrid_retriever.py`)
- **Combines BM25 + Vector search**
- Configurable weights for each method
- Score normalization and fusion
- Best of both worlds: keywords + semantics

### 6. Index Manager (`index_manager.py`)
- Orchestrates all indexing operations
- Supports 3 retrieval modes:
  - `vector`: Semantic similarity only
  - `bm25`: Keyword matching only
  - `hybrid`: Combined (recommended)
- Document CRUD operations
- Index statistics

### 7. Query Engine (`query_engine.py`)
- Citation-aware query engine
- Source tracking with relevance scores
- Streaming response support
- Async query support

## Retrieval Modes

### Vector Search (Semantic)
- Uses embeddings to find semantically similar documents
- Good for: conceptual queries, paraphrasing, multilingual
- Example: "What is machine learning?" matches "AI and data science"

### BM25 Search (Keyword)
- Uses term frequency and document frequency
- Good for: exact terms, technical jargon, IDs, names
- Example: "SSD-777" matches exact issue key

### Hybrid Search (Recommended)
- Combines both approaches with weighted scores
- Default weights: 50% BM25 + 50% Vector
- Best overall performance for most queries

## Usage Examples

### Initialize Index Manager
```python
from backend.services.indexing.index_manager import create_index_manager

# Create with hybrid retrieval (BM25 + Vector)
manager = create_index_manager(
    collection_name="my_documents",
    use_hybrid=True,
    bm25_weight=0.5,  # 50% weight for BM25
    vector_weight=0.5,  # 50% weight for vector
)
```

### Add Documents
```python
from llama_index.core import Document

documents = [
    Document(
        text="Python is a programming language.",
        metadata={"source": "doc1", "type": "tutorial"}
    ),
    Document(
        text="Machine learning uses Python for AI.",
        metadata={"source": "doc2", "type": "article"}
    ),
]

await manager.add_documents(documents)
```

### Query with Different Modes
```python
# Hybrid retrieval (recommended)
query_engine = manager.get_query_engine(
    similarity_top_k=5,
    retrieval_mode="hybrid"
)

response = query_engine.query("What is Python used for?")
print(response)

# BM25 only (keyword matching)
bm25_engine = manager.get_query_engine(retrieval_mode="bm25")
response = bm25_engine.query("Python programming")

# Vector only (semantic)
vector_engine = manager.get_query_engine(retrieval_mode="vector")
response = vector_engine.query("coding languages")
```

### Citation Query Engine
```python
from backend.services.indexing.query_engine import create_citation_query_engine

citation_engine = create_citation_query_engine(
    index_manager=manager,
    similarity_top_k=5,
    retrieval_mode="hybrid"
)

result = citation_engine.query("What is machine learning?")

print(result["response"])
for source in result["sources"]:
    print(f"- {source['title']} (score: {source['relevance_score']:.2f})")
    print(f"  {source['snippet']}")
```

### Streaming Responses
```python
async for chunk in citation_engine.stream_query("Explain Python"):
    print(chunk, end="", flush=True)
```

## BM25 Algorithm

BM25 (Best Matching 25) is a probabilistic ranking function:

```
score(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))
```

Where:
- `D`: Document
- `Q`: Query
- `qi`: Query term i
- `f(qi, D)`: Term frequency of qi in D
- `|D|`: Document length
- `avgdl`: Average document length
- `k1`: Term frequency saturation (default: 1.5)
- `b`: Length normalization (default: 0.75)
- `IDF(qi)`: Inverse document frequency

## Performance Tips

1. **Use hybrid retrieval** for best results
2. **Adjust weights** based on your use case:
   - More technical/exact queries → increase BM25 weight
   - More conceptual queries → increase vector weight
3. **Tune BM25 parameters**:
   - Higher k1 → more weight to term frequency
   - Higher b → more length normalization
4. **Batch document additions** for better performance
5. **Use appropriate similarity_top_k** (5-10 is usually good)

## Dependencies

- `llama-index` - Core framework
- `llama-index-llms-openai-like` - LM Studio integration
- `llama-index-embeddings-huggingface` - Local embeddings
- `llama-index-vector-stores-chroma` - ChromaDB integration
- `chromadb` - Vector database
