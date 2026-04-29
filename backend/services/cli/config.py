"""Configuration loader for CLI tool"""

from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel

class JiraConfig(BaseModel):
    server_url: str
    token: str
    email: str
    project_keys: list[str]

class ConfluenceConfig(BaseModel):
    server_url: str
    token: str
    email: str
    space_keys: list[str]

class DocumentsConfig(BaseModel):
    folder: str

class LLMConfig(BaseModel):
    base_url: str
    model: str
    embedding_model: str

class RetrievalConfig(BaseModel):
    mode: str = "hybrid"  # vector, bm25, hybrid
    similarity_top_k: int = 10
    bm25_weight: float = 0.7
    vector_weight: float = 0.3

class StorageConfig(BaseModel):
    vector_store: str
    index_cache: str
    output: str

class CLIConfig(BaseModel):
    jira: JiraConfig
    confluence: Optional[ConfluenceConfig] = None
    documents: DocumentsConfig
    llm: LLMConfig
    retrieval: RetrievalConfig = RetrievalConfig()
    storage: StorageConfig

def load_config(path: Path) -> CLIConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return CLIConfig(**data)
