"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LM Studio Configuration
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio API base URL",
    )
    lm_studio_model: str = Field(
        default="qwen2.5-coder-7b-instruct",
        description="LLM model name",
    )
    lm_studio_api_key: str = Field(
        default="not-needed",
        description="API key (not required for LM Studio)",
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="BAAI/bge-small-zh-v1.5",
        description="HuggingFace embedding model",
    )

    # Jira Configuration
    jira_base_url: Optional[str] = Field(
        default=None,
        description="Jira instance URL",
    )
    jira_email: Optional[str] = Field(
        default=None,
        description="Jira user email",
    )
    jira_api_token: Optional[str] = Field(
        default=None,
        description="Jira API token",
    )

    # Confluence Configuration
    confluence_base_url: Optional[str] = Field(
        default=None,
        description="Confluence instance URL",
    )
    confluence_email: Optional[str] = Field(
        default=None,
        description="Confluence user email",
    )
    confluence_api_token: Optional[str] = Field(
        default=None,
        description="Confluence API token",
    )

    # Application Settings
    data_dir: Path = Field(
        default=Path("./data"),
        description="Root data directory",
    )
    vector_store_dir: Path = Field(
        default=Path("./data/vector_store"),
        description="ChromaDB storage directory",
    )
    upload_dir: Path = Field(
        default=Path("./data/uploads"),
        description="Uploaded files directory",
    )
    chat_history_dir: Path = Field(
        default=Path("./data/chat_history"),
        description="Chat session storage directory",
    )

    # Server Configuration
    backend_host: str = Field(
        default="0.0.0.0",
        description="Backend server host",
    )
    backend_port: int = Field(
        default=8000,
        description="Backend server port",
    )
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for CORS",
    )

    # Retrieval Configuration
    retrieval_top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for retrieval",
    )

    # Chat Configuration
    chat_context_window: int = Field(
        default=10,
        description="Number of previous messages to include in context",
    )
    llm_temperature: float = Field(
        default=0.3,
        description="LLM temperature for generation",
    )
    llm_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for LLM response",
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chat_history_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
