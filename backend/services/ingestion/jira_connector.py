"""Jira connector using atlassian-python-api."""

import logging
from typing import Optional

from atlassian import Jira
from llama_index.core import Document

from ..ingestion.normalizer import DocumentNormalizer

logger = logging.getLogger(__name__)


class JiraConnector:
    """Connector for fetching Jira issues."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        email: Optional[str] = None,
        cloud: bool = True,
    ):
        """Initialize Jira connector.

        Args:
            base_url: Jira instance URL
                - Cloud: https://your-domain.atlassian.net
                - Server: http://your-server:8080
            api_token: API token or Personal Access Token
            email: User email (required for Cloud, optional for Server)
            cloud: True for Jira Cloud, False for Jira Server
        """
        self.base_url = base_url
        self.cloud = cloud

        if cloud and not email:
            raise ValueError("email is required for Jira Cloud")

        # For Cloud: use email as username
        # For Server: use token directly (no username needed)
        if cloud:
            self.jira = Jira(
                url=base_url,
                username=email,
                password=api_token,
                cloud=True,
            )
        else:
            # Jira Server with token authentication
            self.jira = Jira(
                url=base_url,
                token=api_token,
                cloud=False,
            )

    async def test_connection(self) -> dict[str, any]:
        """Test Jira connection.

        Returns:
            Dictionary with connection status:
            {
                "success": bool,
                "message": str,
                "user": str (if successful)
            }
        """
        try:
            user = self.jira.myself()
            return {
                "success": True,
                "message": "Connection successful",
                "user": user.get("displayName", "Unknown"),
            }
        except Exception as e:
            logger.error(f"Jira connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
            }

    async def fetch_issue(self, issue_key: str) -> Document:
        """Fetch a single Jira issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")

        Returns:
            LlamaIndex Document

        Raises:
            RuntimeError: If fetch fails
        """
        try:
            issue = self.jira.issue(issue_key, expand="renderedFields,names,schema,transitions")
            return DocumentNormalizer.normalize_jira_issue(issue)
        except Exception as e:
            logger.error(f"Failed to fetch issue {issue_key}: {e}")
            raise RuntimeError(f"Failed to fetch Jira issue: {e}")

    async def fetch_issues(
        self,
        jql: str,
        max_results: int = 100,
        start_at: int = 0,
    ) -> list[Document]:
        """Fetch multiple Jira issues using JQL.

        Args:
            jql: JQL query string (e.g., "project = PROJ AND status = Open")
            max_results: Maximum number of results per page
            start_at: Starting index for pagination

        Returns:
            List of LlamaIndex Documents

        Raises:
            RuntimeError: If fetch fails
        """
        try:
            results = self.jira.jql(
                jql,
                limit=max_results,
                start=start_at,
                expand="renderedFields,names,schema,transitions",
            )

            issues = results.get("issues", [])
            documents = DocumentNormalizer.normalize_batch(issues, "jira")

            logger.info(f"Fetched {len(documents)} issues from Jira")
            return documents

        except Exception as e:
            logger.error(f"Failed to fetch issues with JQL '{jql}': {e}")
            raise RuntimeError(f"Failed to fetch Jira issues: {e}")

    async def fetch_project(
        self,
        project_key: str,
        max_results: int = 1000,
    ) -> list[Document]:
        """Fetch all issues from a Jira project.

        Args:
            project_key: Project key (e.g., "PROJ")
            max_results: Maximum number of issues to fetch

        Returns:
            List of LlamaIndex Documents
        """
        jql = f"project = {project_key} ORDER BY created DESC"
        return await self.fetch_issues(jql, max_results=max_results)

    async def fetch_by_status(
        self,
        project_key: str,
        status: str,
        max_results: int = 100,
    ) -> list[Document]:
        """Fetch issues by status.

        Args:
            project_key: Project key
            status: Status name (e.g., "Open", "In Progress", "Done")
            max_results: Maximum number of issues

        Returns:
            List of LlamaIndex Documents
        """
        jql = f'project = {project_key} AND status = "{status}" ORDER BY created DESC'
        return await self.fetch_issues(jql, max_results=max_results)

    async def fetch_updated_since(
        self,
        project_key: str,
        since_date: str,
        max_results: int = 100,
    ) -> list[Document]:
        """Fetch issues updated since a specific date.

        Args:
            project_key: Project key
            since_date: Date in format "YYYY-MM-DD"
            max_results: Maximum number of issues

        Returns:
            List of LlamaIndex Documents
        """
        jql = f'project = {project_key} AND updated >= "{since_date}" ORDER BY updated DESC'
        return await self.fetch_issues(jql, max_results=max_results)

    def get_projects(self) -> list[dict[str, str]]:
        """Get list of available projects.

        Returns:
            List of projects with keys and names
        """
        try:
            projects = self.jira.projects()
            return [
                {
                    "key": p.get("key", ""),
                    "name": p.get("name", ""),
                    "id": p.get("id", ""),
                }
                for p in projects
            ]
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
