"""Data source model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""

    id: str
    name: str
    description: str = ""
    type: Literal["file", "jira", "confluence"]
    config: Dict[str, Any]
    status: Literal["active", "deleted"] = "active"
    last_sync: Optional[str] = None
    sync_count: int = 0
    document_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FileDataSourceConfig(BaseModel):
    """File data source specific configuration."""

    files: List[str] = Field(default_factory=list)


class JiraDataSourceConfig(BaseModel):
    """Jira data source specific configuration."""

    url: str
    email: str
    token: str
    jql: str = ""


class ConfluenceDataSourceConfig(BaseModel):
    """Confluence data source specific configuration."""

    url: str
    email: str
    token: str
    space_keys: List[str] = Field(default_factory=list)
    page_ids: List[str] = Field(default_factory=list)
