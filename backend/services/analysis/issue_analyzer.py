"""Issue analyzer for deep analysis of Jira issues."""

import logging
from typing import Optional

from llama_index.core import Document
from llama_index.core.schema import NodeWithScore

from backend.models.analysis import (
    AnalysisSource,
    IssueAnalysisResult,
    RelatedIssue,
)
from backend.services.indexing.index_manager import IndexManager
from backend.services.ingestion.jira_connector import JiraConnector
from backend.services.knowledge.kb_manager import KnowledgeBaseManager

logger = logging.getLogger(__name__)


class IssueAnalyzer:
    """Analyze Jira issues with context from documents and related issues."""

    def __init__(
        self,
        jira_connector: JiraConnector,
        index_manager: IndexManager,
        kb_manager: KnowledgeBaseManager,
    ):
        """Initialize issue analyzer.

        Args:
            jira_connector: Jira connector instance
            index_manager: Index manager for document retrieval
            kb_manager: Knowledge base manager for saving results
        """
        self.jira_connector = jira_connector
        self.index_manager = index_manager
        self.kb_manager = kb_manager
        self.llm = index_manager.llm

    async def analyze_issue(
        self,
        issue_key: str,
        depth: str = "deep",
        include_related: bool = True,
        save_to_kb: bool = True,
    ) -> IssueAnalysisResult:
        """Analyze a Jira issue.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            depth: Analysis depth ("quick" or "deep")
            include_related: Whether to include related issues
            save_to_kb: Whether to save to knowledge base

        Returns:
            IssueAnalysisResult with analysis and sources
        """
        logger.info(f"Starting analysis for {issue_key} (depth={depth})")

        # 1. Fetch issue details
        issue_doc = await self.jira_connector.fetch_issue(issue_key)
        issue_metadata = issue_doc.metadata

        issue_summary = issue_metadata.get("summary", "")
        issue_description = issue_metadata.get("description", "")

        # 2. Build query from issue content
        query = self._build_query(issue_summary, issue_description)

        # 3. Retrieve relevant documents
        sources = await self._retrieve_documents(query, top_k=10)

        # 4. Find related issues
        related_issues = []
        if include_related:
            related_issues = await self._find_related_issues(issue_key, issue_metadata)

        # 5. Generate analysis using LLM
        analysis = await self._generate_analysis(
            issue_key=issue_key,
            issue_summary=issue_summary,
            issue_description=issue_description,
            sources=sources,
            related_issues=related_issues,
            depth=depth,
        )

        # 6. Create result
        result = IssueAnalysisResult(
            issue_key=issue_key,
            issue_summary=issue_summary,
            issue_description=issue_description,
            analysis=analysis,
            sources=sources,
            related_issues=related_issues,
            depth=depth,
        )

        # 7. Save to knowledge base
        if save_to_kb:
            self.kb_manager.save_issue_analysis(result)
            logger.info(f"Saved analysis for {issue_key} to knowledge base")

        return result

    def _build_query(self, summary: str, description: str) -> str:
        """Build search query from issue content.

        Args:
            summary: Issue summary
            description: Issue description

        Returns:
            Search query string
        """
        # Combine summary and first part of description
        desc_preview = description[:500] if description else ""
        query = f"{summary}\n{desc_preview}"
        return query.strip()

    async def _retrieve_documents(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[AnalysisSource]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of AnalysisSource objects
        """
        try:
            # Get retriever (hybrid mode for best results)
            retriever = self.index_manager.get_retriever(
                similarity_top_k=top_k,
                retrieval_mode="hybrid",
            )

            # Retrieve nodes
            nodes: list[NodeWithScore] = await retriever.aretrieve(query)

            # Convert to AnalysisSource
            sources = []
            for node in nodes:
                metadata = node.node.metadata
                sources.append(
                    AnalysisSource(
                        source_id=node.node.node_id,
                        title=metadata.get("title", metadata.get("file_name", "Unknown")),
                        snippet=node.node.get_content()[:500],  # First 500 chars
                        score=node.score or 0.0,
                        source_type=metadata.get("source_type", "unknown"),
                    )
                )

            logger.info(f"Retrieved {len(sources)} documents")
            return sources

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []

    async def _find_related_issues(
        self,
        issue_key: str,
        issue_metadata: dict,
    ) -> list[RelatedIssue]:
        """Find related Jira issues.

        Args:
            issue_key: Current issue key
            issue_metadata: Issue metadata

        Returns:
            List of RelatedIssue objects
        """
        related = []

        try:
            # Get issue links from metadata
            issue_links = issue_metadata.get("issuelinks", [])

            for link in issue_links:
                # Jira link structure: either "inwardIssue" or "outwardIssue"
                link_type = link.get("type", {}).get("name", "relates to")

                if "inwardIssue" in link:
                    linked_issue = link["inwardIssue"]
                    relation = link.get("type", {}).get("inward", "relates to")
                elif "outwardIssue" in link:
                    linked_issue = link["outwardIssue"]
                    relation = link.get("type", {}).get("outward", "relates to")
                else:
                    continue

                related.append(
                    RelatedIssue(
                        issue_key=linked_issue.get("key", ""),
                        summary=linked_issue.get("fields", {}).get("summary", ""),
                        status=linked_issue.get("fields", {}).get("status", {}).get("name", "Unknown"),
                        link_type=relation,
                        url=linked_issue.get("self", ""),
                    )
                )

            logger.info(f"Found {len(related)} related issues for {issue_key}")

        except Exception as e:
            logger.error(f"Failed to find related issues: {e}")

        return related

    async def _generate_analysis(
        self,
        issue_key: str,
        issue_summary: str,
        issue_description: str,
        sources: list[AnalysisSource],
        related_issues: list[RelatedIssue],
        depth: str,
    ) -> str:
        """Generate analysis using LLM.

        Args:
            issue_key: Issue key
            issue_summary: Issue summary
            issue_description: Issue description
            sources: Retrieved source documents
            related_issues: Related issues
            depth: Analysis depth

        Returns:
            Analysis text in Markdown format
        """
        # Build prompt
        prompt = self._build_analysis_prompt(
            issue_key=issue_key,
            issue_summary=issue_summary,
            issue_description=issue_description,
            sources=sources,
            related_issues=related_issues,
            depth=depth,
        )

        try:
            # Generate analysis
            response = await self.llm.acomplete(prompt)
            analysis = response.text.strip()

            logger.info(f"Generated analysis for {issue_key} ({len(analysis)} chars)")
            return analysis

        except Exception as e:
            logger.error(f"Failed to generate analysis: {e}")
            return f"分析生成失败: {str(e)}"

    def _build_analysis_prompt(
        self,
        issue_key: str,
        issue_summary: str,
        issue_description: str,
        sources: list[AnalysisSource],
        related_issues: list[RelatedIssue],
        depth: str,
    ) -> str:
        """Build analysis prompt for LLM.

        Args:
            issue_key: Issue key
            issue_summary: Issue summary
            issue_description: Issue description
            sources: Retrieved sources
            related_issues: Related issues
            depth: Analysis depth

        Returns:
            Prompt string
        """
        # Format sources
        sources_text = ""
        if sources:
            sources_text = "\n\n".join([
                f"**文档 {i+1}: {s.title}** (类型: {s.source_type}, 相关度: {s.score:.2f})\n{s.snippet}"
                for i, s in enumerate(sources[:5])  # Top 5 sources
            ])
        else:
            sources_text = "（未找到相关文档）"

        # Format related issues
        related_text = ""
        if related_issues:
            related_text = "\n".join([
                f"- **{r.issue_key}** ({r.link_type}): {r.summary} - 状态: {r.status}"
                for r in related_issues
            ])
        else:
            related_text = "（无关联 Issues）"

        # Build prompt based on depth
        if depth == "quick":
            prompt = f"""你是一个 SSD 工程团队的技术分析助手。请对以下 Jira Issue 进行快速分析。

Issue: {issue_key}
标题: {issue_summary}

描述:
{issue_description}

相关文档:
{sources_text}

关联 Issues:
{related_text}

请提供简要分析（2-3 段）：
1. 问题概述
2. 关键要点
3. 建议的下一步行动

要求：
- 简洁明了
- 突出重点
- 使用 Markdown 格式
"""
        else:  # deep
            prompt = f"""你是一个 SSD 工程团队的技术分析助手。请对以下 Jira Issue 进行深度分析。

Issue: {issue_key}
标题: {issue_summary}

描述:
{issue_description}

相关文档:
{sources_text}

关联 Issues:
{related_text}

请提供以下深度分析：

### 1. 问题根因分析
分析问题的根本原因，结合相关文档和技术背景。

### 2. 相关技术背景
说明涉及的技术领域、规范、设计文档等。引用具体的文档和章节。

### 3. 可能的解决方案
提供 2-3 个可行的解决方案，分析各自的优缺点。

### 4. 风险和注意事项
指出实施过程中需要注意的风险点和依赖关系。

### 5. 建议的行动计划
给出具体的下一步行动建议。

要求：
- 引用具体的文档和章节
- 提供技术细节
- 保持客观和准确
- 使用 Markdown 格式
- 如果相关文档不足，请明确指出
"""

        return prompt


def create_issue_analyzer(
    jira_connector: JiraConnector,
    index_manager: IndexManager,
    kb_manager: KnowledgeBaseManager,
) -> IssueAnalyzer:
    """Create issue analyzer.

    Args:
        jira_connector: Jira connector instance
        index_manager: Index manager instance
        kb_manager: Knowledge base manager instance

    Returns:
        IssueAnalyzer instance
    """
    return IssueAnalyzer(
        jira_connector=jira_connector,
        index_manager=index_manager,
        kb_manager=kb_manager,
    )
