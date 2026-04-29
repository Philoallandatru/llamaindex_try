"""API request and response models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Index API Models
# ============================================================================


class BuildIndexRequest(BaseModel):
    """Request to build index from documents."""

    source_type: str = Field(..., description="Source type: 'file', 'jira', 'confluence'")
    source_config: dict[str, Any] = Field(..., description="Source-specific configuration")
    collection_name: str = Field(default="documents", description="Collection name")


class IndexStatsResponse(BaseModel):
    """Response with index statistics."""

    collection_name: str
    total_documents: int
    vector_store: dict[str, Any]
    bm25_enabled: bool
    hybrid_enabled: bool
    retrieval_modes: list[str]


class BuildIndexResponse(BaseModel):
    """Response after building index."""

    success: bool
    message: str
    documents_added: int
    collection_name: str


# ============================================================================
# Source API Models
# ============================================================================


class UploadFileRequest(BaseModel):
    """Request to upload a file."""

    collection_name: str = Field(default="documents", description="Target collection")


class UploadFileResponse(BaseModel):
    """Response after file upload."""

    success: bool
    message: str
    file_path: str
    documents_created: int


class JiraConnectionRequest(BaseModel):
    """Request to connect to Jira."""

    base_url: str = Field(..., description="Jira base URL")
    api_token: str = Field(..., description="API token or Personal Access Token")
    email: Optional[str] = Field(default=None, description="User email (required for Cloud, optional for Server)")
    jql: Optional[str] = Field(default=None, description="JQL query (optional)")
    project_key: Optional[str] = Field(default=None, description="Project key (optional)")
    max_results: int = Field(default=100, description="Maximum results")
    cloud: bool = Field(default=True, description="True for Jira Cloud, False for Jira Server")


class ConfluenceConnectionRequest(BaseModel):
    """Request to connect to Confluence."""

    base_url: str = Field(..., description="Confluence base URL")
    api_token: str = Field(..., description="API token or Personal Access Token")
    email: Optional[str] = Field(default=None, description="User email (required for Cloud, optional for Server)")
    space_key: Optional[str] = Field(default=None, description="Space key (optional)")
    page_id: Optional[str] = Field(default=None, description="Page ID (optional)")
    max_pages: int = Field(default=100, description="Maximum pages")
    cloud: bool = Field(default=True, description="True for Confluence Cloud, False for Confluence Server")


class ConnectionTestResponse(BaseModel):
    """Response from connection test."""

    success: bool
    message: str
    user: Optional[str] = None


class SyncSourceRequest(BaseModel):
    """Request to sync a data source."""

    source_id: str = Field(..., description="Source identifier")
    incremental: bool = Field(default=True, description="Incremental sync")


class SyncSourceResponse(BaseModel):
    """Response after syncing source."""

    success: bool
    message: str
    documents_synced: int
    source_id: str


# ============================================================================
# Health Check Models
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="0.1.0")
    components: dict[str, str] = Field(default_factory=dict)


# ============================================================================
# Error Models
# ============================================================================


class ErrorResponse(BaseModel):
    """Error response."""

    error: bool = True
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
