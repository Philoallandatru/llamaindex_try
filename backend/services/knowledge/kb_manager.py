"""Knowledge base manager for storing and retrieving analysis results."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.models.analysis import AnalysisMetadata, IssueAnalysisResult
from backend.models.report import FullReport

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manage knowledge base storage and retrieval."""

    def __init__(self, base_dir: str = "workspace/knowledge"):
        """Initialize knowledge base manager.

        Args:
            base_dir: Base directory for knowledge base storage
        """
        self.base_dir = Path(base_dir)
        self.issues_dir = self.base_dir / "issues"
        self.reports_dir = self.base_dir / "reports" / "daily"

        # Create directories
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized KnowledgeBaseManager at {self.base_dir}")

    def save_issue_analysis(
        self,
        analysis_result: IssueAnalysisResult,
    ) -> dict[str, str]:
        """Save issue analysis to knowledge base.

        Args:
            analysis_result: Analysis result to save

        Returns:
            Dictionary with saved file paths
        """
        issue_key = analysis_result.issue_key
        issue_dir = self.issues_dir / issue_key
        issue_dir.mkdir(parents=True, exist_ok=True)

        # Save analysis as Markdown
        analysis_path = issue_dir / "analysis.md"
        markdown_content = self._format_analysis_markdown(analysis_result)
        analysis_path.write_text(markdown_content, encoding="utf-8")

        # Save metadata as JSON
        metadata = AnalysisMetadata(
            issue_key=issue_key,
            timestamp=analysis_result.timestamp,
            depth=analysis_result.depth,
            sources_count=len(analysis_result.sources),
            related_issues_count=len(analysis_result.related_issues),
        )
        metadata_path = issue_dir / "metadata.json"
        metadata_path.write_text(
            metadata.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Save sources as JSON
        sources_path = issue_dir / "sources.json"
        sources_data = {
            "sources": [s.model_dump() for s in analysis_result.sources],
            "related_issues": [r.model_dump() for r in analysis_result.related_issues],
        }
        sources_path.write_text(
            json.dumps(sources_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info(f"Saved analysis for {issue_key} to {issue_dir}")

        return {
            "analysis_path": str(analysis_path),
            "metadata_path": str(metadata_path),
            "sources_path": str(sources_path),
        }

    def get_issue_analysis(self, issue_key: str) -> Optional[dict]:
        """Get saved analysis for an issue.

        Args:
            issue_key: Issue key

        Returns:
            Dictionary with analysis data or None if not found
        """
        issue_dir = self.issues_dir / issue_key
        if not issue_dir.exists():
            return None

        analysis_path = issue_dir / "analysis.md"
        metadata_path = issue_dir / "metadata.json"
        sources_path = issue_dir / "sources.json"

        if not analysis_path.exists():
            return None

        # Read files
        analysis_md = analysis_path.read_text(encoding="utf-8")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        sources = json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.exists() else {}

        return {
            "issue_key": issue_key,
            "analysis": analysis_md,
            "metadata": metadata,
            "sources": sources.get("sources", []),
            "related_issues": sources.get("related_issues", []),
        }

    def list_analyzed_issues(self) -> list[dict]:
        """List all analyzed issues.

        Returns:
            List of issue metadata
        """
        issues = []
        if not self.issues_dir.exists():
            return issues

        for issue_dir in self.issues_dir.iterdir():
            if not issue_dir.is_dir():
                continue

            metadata_path = issue_dir / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                issues.append(metadata)

        # Sort by timestamp (newest first)
        issues.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return issues

    def _format_analysis_markdown(self, result: IssueAnalysisResult) -> str:
        """Format analysis result as Markdown.

        Args:
            result: Analysis result

        Returns:
            Markdown formatted string
        """
        lines = [
            f"# {result.issue_key}: {result.issue_summary}",
            "",
            f"**分析时间**: {result.timestamp}",
            f"**分析深度**: {result.depth}",
            "",
            "## Issue 描述",
            "",
            result.issue_description,
            "",
            "## 深度分析",
            "",
            result.analysis,
            "",
        ]

        # Add related issues
        if result.related_issues:
            lines.extend([
                "## 关联 Issues",
                "",
            ])
            for related in result.related_issues:
                link_text = f"[{related.issue_key}]({related.url})" if related.url else related.issue_key
                lines.append(f"- **{link_text}** ({related.link_type}): {related.summary} - *{related.status}*")
            lines.append("")

        # Add sources
        if result.sources:
            lines.extend([
                "## 参考文档",
                "",
            ])
            for i, source in enumerate(result.sources, 1):
                lines.extend([
                    f"### {i}. {source.title}",
                    f"**类型**: {source.source_type} | **相关度**: {source.score:.2f}",
                    "",
                    f"> {source.snippet}",
                    "",
                ])

        return "\n".join(lines)

    def _format_report_markdown(self, report: FullReport) -> str:
        """Format daily report as Markdown.

        Args:
            report: Full report object

        Returns:
            Markdown formatted string
        """
        lines = [
            f"# Daily Report - {report.date}",
            "",
            f"**生成时间**: {report.generated_at}",
            "",
            "## 概览",
            "",
            report.summary,
            "",
            "## 统计信息",
            "",
            f"**总计**: {report.quick_report.stats.total_issues} 个 Issues 更新",
            "",
        ]

        # Status breakdown
        if report.quick_report.stats.by_status:
            lines.extend([
                "### 按状态分类",
                "",
            ])
            for status, count in report.quick_report.stats.by_status.items():
                lines.append(f"- **{status}**: {count}")
            lines.append("")

        # Priority breakdown
        if report.quick_report.stats.by_priority:
            lines.extend([
                "### 按优先级分类",
                "",
            ])
            for priority, count in report.quick_report.stats.by_priority.items():
                lines.append(f"- **{priority}**: {count}")
            lines.append("")

        # Key updates
        if report.key_updates:
            lines.extend([
                "## 关键更新",
                "",
            ])
            for update in report.key_updates:
                lines.append(f"- {update}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.extend([
                "## 建议",
                "",
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Issue list
        if report.quick_report.issues:
            lines.extend([
                "## 更新的 Issues",
                "",
            ])
            for issue in report.quick_report.issues:
                assignee = issue.assignee or "未分配"
                lines.append(
                    f"- **{issue.key}**: {issue.summary} "
                    f"[{issue.status}] [{issue.priority}] - {assignee}"
                )
            lines.append("")

        return "\n".join(lines)

    def save_daily_report(
        self,
        date: str,
        full_report: FullReport,
    ) -> dict[str, str]:
        """Save daily report to knowledge base.

        Args:
            date: Report date (YYYY-MM-DD)
            full_report: Full report object

        Returns:
            Dictionary with saved file paths
        """
        report_dir = self.reports_dir / date
        report_dir.mkdir(parents=True, exist_ok=True)

        # Save full report as JSON
        report_path = report_dir / "report.json"
        report_path.write_text(
            full_report.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Save as Markdown for readability
        markdown_content = self._format_report_markdown(full_report)
        markdown_path = report_dir / "report.md"
        markdown_path.write_text(markdown_content, encoding="utf-8")

        # Save metadata
        metadata = {
            "date": date,
            "timestamp": full_report.generated_at,
            "issues_count": full_report.quick_report.stats.total_issues,
        }
        metadata_path = report_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info(f"Saved daily report for {date} to {report_dir}")

        return {
            "report_path": str(report_path),
            "markdown_path": str(markdown_path),
            "metadata_path": str(metadata_path),
        }

    def get_daily_report(self, date: str) -> Optional[dict]:
        """Get saved daily report.

        Args:
            date: Report date (YYYY-MM-DD)

        Returns:
            Dictionary with report data or None if not found
        """
        report_dir = self.reports_dir / date
        if not report_dir.exists():
            return None

        report_path = report_dir / "report.json"
        markdown_path = report_dir / "report.md"
        metadata_path = report_dir / "metadata.json"

        if not report_path.exists():
            return None

        # Read files
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else None
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}

        return {
            "date": date,
            "report": report_data,
            "markdown": markdown,
            "metadata": metadata,
        }

    def list_daily_reports(self) -> list[dict]:
        """List all daily reports.

        Returns:
            List of report metadata
        """
        reports = []
        if not self.reports_dir.exists():
            return reports

        for report_dir in self.reports_dir.iterdir():
            if not report_dir.is_dir():
                continue

            metadata_path = report_dir / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                reports.append(metadata)

        # Sort by date (newest first)
        reports.sort(key=lambda x: x.get("date", ""), reverse=True)
        return reports


def create_kb_manager(base_dir: str = "workspace/knowledge") -> KnowledgeBaseManager:
    """Create knowledge base manager.

    Args:
        base_dir: Base directory for knowledge base

    Returns:
        KnowledgeBaseManager instance
    """
    return KnowledgeBaseManager(base_dir=base_dir)
