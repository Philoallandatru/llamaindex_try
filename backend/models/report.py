"""Data models for daily reports."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IssueStats(BaseModel):
    """Statistics for a single issue."""
    key: str
    summary: str
    status: str
    priority: str
    assignee: Optional[str] = None
    updated: str


class QuickReportStats(BaseModel):
    """Quick statistics for daily report."""
    total_issues: int
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)
    by_assignee: Dict[str, int] = Field(default_factory=dict)


class QuickReport(BaseModel):
    """Quick daily report (no LLM analysis)."""
    date: str
    issues: List[IssueStats]
    stats: QuickReportStats
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class FullReport(BaseModel):
    """Full daily report with LLM analysis."""
    date: str
    quick_report: QuickReport
    summary: str  # LLM-generated summary
    key_updates: List[str]  # Important updates
    recommendations: List[str]  # Action items
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ReportRequest(BaseModel):
    """Request to generate a daily report."""
    date: str  # YYYY-MM-DD format
    mode: str = "quick"  # "quick" or "full"


class ReportResponse(BaseModel):
    """Response for report generation."""
    report_id: str
    status: str  # "generating", "complete", "error"
    quick_report: Optional[QuickReport] = None
    full_report: Optional[FullReport] = None
    error: Optional[str] = None
