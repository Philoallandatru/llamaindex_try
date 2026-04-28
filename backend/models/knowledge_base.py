"""Knowledge base model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class RetrievalConfig(BaseModel):
    """Retrieval configuration for a knowledge base."""

    mode: Literal["vector", "bm25", "hybrid"] = "hybrid"
    bm25_weight: float = 0.5
    vector_weight: float = 0.5
    similarity_top_k: int = 5
    enable_reranker: bool = False
    reranker_model: str = "BAAI/bge-reranker-base"
    reranker_top_n: int = 3


class KnowledgeBaseConfig(BaseModel):
    """Configuration for a knowledge base."""

    id: str
    name: str
    description: str
    datasource_ids: List[str] = Field(default_factory=list)
    collection_name: str
    retrieval_config: RetrievalConfig = Field(default_factory=RetrievalConfig)
    status: Literal["active", "deleted"] = "active"
    document_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Alias for backward compatibility
KnowledgeBase = KnowledgeBaseConfig
