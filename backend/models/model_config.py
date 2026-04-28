"""Model configuration model."""

from datetime import datetime
from typing import Any, Dict, Literal
from pydantic import BaseModel, Field


class ModelParameters(BaseModel):
    """LLM model parameters."""

    temperature: float = 0.3
    max_tokens: int = 2000
    top_p: float = 0.9


class ModelConfig(BaseModel):
    """Configuration for an LLM model."""

    id: str
    name: str
    api_base: str
    api_key: str
    model_name: str
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    is_default: bool = False
    status: Literal["active", "deleted"] = "active"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
