"""Data models for issue analysis."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RelatedIssue(BaseModel):
    """Related Jira issue."""

    issue_key: str = Field(..., description="Issue key (e.g., PROJ-123)")
    summary: str = Field(..., description="Issue summary")
    status: str = Field(..., description="Issue status")
    link_type: str = Field(..., description="Link type (e.g., blocks, relates to)")
    url: Optional[str] = Field(None, description="Issue URL")


class AnalysisSource(BaseModel):
    """Source document used in analysis."""

    source_id: str = Field(..., description="Source document ID")
    title: str = Field(..., description="Document title")
    snippet: str = Field(..., description="Relevant snippet")
    score: float = Field(..., description="Relevance score")
    source_type: str = Field(..., description="Source type (pdf, jira, confluence)")


class IssueAnalysisResult(BaseModel):
    """Result of issue analysis."""

    issue_key: str = Field(..., description="Issue key")
    issue_summary: str = Field(..., description="Issue summary")
    issue_description: str = Field(..., description="Issue description")
    analysis: str = Field(..., description="Generated analysis (Markdown format)")
    sources: list[AnalysisSource] = Field(default_factory=list, description="Source documents")
    related_issues: list[RelatedIssue] = Field(default_factory=list, description="Related issues")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Analysis timestamp")
    depth: str = Field("deep", description="Analysis depth (quick or deep)")


class AnalysisRequest(BaseModel):
    """Request for issue analysis."""

    issue_key: str = Field(..., description="Issue key to analyze")
    depth: str = Field("deep", description="Analysis depth (quick or deep)")
    include_related: bool = Field(True, description="Include related issues")
    save_to_kb: bool = Field(True, description="Save to knowledge base")


class AnalysisMetadata(BaseModel):
    """Metadata for saved analysis."""

    issue_key: str
    timestamp: str
    depth: str
    sources_count: int
    related_issues_count: int
