"""Sync task model."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class SyncTask(BaseModel):
    """Sync task status and metadata."""

    id: str
    datasource_id: Optional[str] = None
    knowledge_base_id: str
    type: Literal["sync", "kb_sync"]
    status: Literal["pending", "running", "completed", "failed", "cancelled"] = "pending"
    progress: float = 0.0
    current_step: str = "Initializing..."
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    error_message: Optional[str] = None
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    celery_task_id: Optional[str] = None
