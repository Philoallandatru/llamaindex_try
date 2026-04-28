"""Daily report generator service."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

from backend.models.report import (
    QuickReport, FullReport, IssueStats, QuickReportStats
)
from backend.services.ingestion.jira_connector import JiraConnector
from backend.services.analysis.issue_analyzer import IssueAnalyzer

logger = logging.getLogger(__name__)


class DailyReportGenerator:
    """Generates daily reports of Jira updates."""

    def __init__(self, jira_connector: JiraConnector, issue_analyzer: IssueAnalyzer):
        self.jira = jira_connector
        self.analyzer = issue_analyzer

    async def generate_quick_report(self, date: str) -> QuickReport:
        """Generate quick report without LLM analysis.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            QuickReport with statistics
        """
        logger.info(f"Generating quick report for {date}")

        # Fetch issues updated on this date
        date_obj = datetime.fromisoformat(date)
        next_day = date_obj + timedelta(days=1)

        issues = await self.jira.fetch_updated_since(date)

        # Filter to only issues updated on the specific date
        # (fetch_updated_since returns all issues since date, we want just that day)
        issue_stats = []
        for issue in issues:
            updated = issue.get('fields', {}).get('updated', '')
            if updated.startswith(date):
                issue_stats.append(IssueStats(
                    key=issue['key'],
                    summary=issue['fields'].get('summary', ''),
                    status=issue['fields'].get('status', {}).get('name', 'Unknown'),
                    priority=issue['fields'].get('priority', {}).get('name', 'None'),
                    assignee=issue['fields'].get('assignee', {}).get('displayName') if issue['fields'].get('assignee') else None,
                    updated=updated
                ))

        # Calculate statistics
        stats = self._calculate_stats(issue_stats)

        return QuickReport(
            date=date,
            issues=issue_stats,
            stats=stats
        )

    def _calculate_stats(self, issues: List[IssueStats]) -> QuickReportStats:
        """Calculate statistics from issue list."""
        by_status = defaultdict(int)
        by_priority = defaultdict(int)
        by_assignee = defaultdict(int)

        for issue in issues:
            by_status[issue.status] += 1
            by_priority[issue.priority] += 1
            if issue.assignee:
                by_assignee[issue.assignee] += 1
            else:
                by_assignee['Unassigned'] += 1

        return QuickReportStats(
            total_issues=len(issues),
            by_status=dict(by_status),
            by_priority=dict(by_priority),
            by_assignee=dict(by_assignee)
        )

    async def generate_full_report(self, date: str) -> FullReport:
        """Generate full report with LLM analysis.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            FullReport with analysis and recommendations
        """
        logger.info(f"Generating full report for {date}")

        # Get quick report first
        quick_report = await self.generate_quick_report(date)

        if not quick_report.issues:
            return FullReport(
                date=date,
                quick_report=quick_report,
                summary="No issues were updated on this date.",
                key_updates=[],
                recommendations=[]
            )

        # Analyze each issue
        analyses = []
        for issue in quick_report.issues:
            try:
                analysis = await self.analyzer.analyze_issue(issue.key)
                analyses.append(analysis)
            except Exception as e:
                logger.warning(f"Failed to analyze {issue.key}: {e}")

        # Generate summary using LLM
        summary, key_updates, recommendations = await self._generate_summary(
            quick_report, analyses
        )

        return FullReport(
            date=date,
            quick_report=quick_report,
            summary=summary,
            key_updates=key_updates,
            recommendations=recommendations
        )

    async def _generate_summary(
        self,
        quick_report: QuickReport,
        analyses: List[Any]
    ) -> tuple[str, List[str], List[str]]:
        """Generate summary, key updates, and recommendations using LLM."""

        # Build context for LLM
        context = f"""Daily Report for {quick_report.date}

Total Issues Updated: {quick_report.stats.total_issues}

Status Breakdown:
{self._format_dict(quick_report.stats.by_status)}

Priority Breakdown:
{self._format_dict(quick_report.stats.by_priority)}

Issues:
"""
        for issue in quick_report.issues:
            context += f"\n- {issue.key}: {issue.summary} [{issue.status}] [{issue.priority}]"

        # Add analysis insights if available
        if analyses:
            context += "\n\nDetailed Analysis:\n"
            for analysis in analyses:
                context += f"\n{analysis.issue_key}:\n{analysis.analysis[:500]}...\n"

        # Generate summary using LLM
        prompt = f"""Based on the following daily Jira update report, provide:

1. A concise summary (2-3 sentences) of the day's activity
2. Key updates (3-5 bullet points of important changes)
3. Recommendations (2-3 action items for the team)

{context}

Format your response as:

SUMMARY:
[Your summary here]

KEY_UPDATES:
- [Update 1]
- [Update 2]
...

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
..."""

        try:
            response = await self.analyzer.llm.acomplete(prompt)
            response_text = str(response)

            # Parse response
            summary = ""
            key_updates = []
            recommendations = []

            current_section = None
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('SUMMARY:'):
                    current_section = 'summary'
                    continue
                elif line.startswith('KEY_UPDATES:'):
                    current_section = 'key_updates'
                    continue
                elif line.startswith('RECOMMENDATIONS:'):
                    current_section = 'recommendations'
                    continue

                if current_section == 'summary' and line:
                    summary += line + " "
                elif current_section == 'key_updates' and line.startswith('-'):
                    key_updates.append(line[1:].strip())
                elif current_section == 'recommendations' and line.startswith('-'):
                    recommendations.append(line[1:].strip())

            return summary.strip(), key_updates, recommendations

        except Exception as e:
            logger.error(f"Failed to generate LLM summary: {e}")
            return (
                f"Report generated for {quick_report.stats.total_issues} issues.",
                [f"{issue.key}: {issue.summary}" for issue in quick_report.issues[:5]],
                ["Review updated issues", "Follow up on high priority items"]
            )

    def _format_dict(self, d: Dict[str, int]) -> str:
        """Format dictionary for display."""
        return "\n".join(f"  {k}: {v}" for k, v in d.items())


def create_report_generator(issue_analyzer, kb_manager):
    """Factory function to create DailyReportGenerator instance.

    Args:
        issue_analyzer: IssueAnalyzer instance
        kb_manager: KnowledgeBaseManager instance

    Returns:
        DailyReportGenerator instance
    """
    return DailyReportGenerator(issue_analyzer, kb_manager)
