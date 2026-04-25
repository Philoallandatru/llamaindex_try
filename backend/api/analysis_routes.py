"""API routes for issue analysis."""

import logging

from fastapi import APIRouter, HTTPException

from backend.models.analysis import AnalysisRequest, IssueAnalysisResult
from backend.services.analysis.issue_analyzer import create_issue_analyzer
from backend.services.ingestion.jira_connector import JiraConnector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Global dependencies (set from main.py or source_routes)
_index_manager = None
_kb_manager = None
_jira_connector = None


def init_analysis_routes(index_manager, kb_manager):
    """Initialize analysis routes with dependencies.

    Args:
        index_manager: IndexManager instance
        kb_manager: KnowledgeBaseManager instance
    """
    global _index_manager, _kb_manager
    _index_manager = index_manager
    _kb_manager = kb_manager
    logger.info("Analysis routes initialized")


def set_jira_connector(jira_connector: JiraConnector):
    """Set Jira connector for analysis.

    Args:
        jira_connector: JiraConnector instance
    """
    global _jira_connector
    _jira_connector = jira_connector
    logger.info("Jira connector set for analysis routes")


def _get_analyzer():
    """Get or create issue analyzer.

    Returns:
        IssueAnalyzer instance

    Raises:
        HTTPException: If dependencies not initialized
    """
    if _index_manager is None or _kb_manager is None:
        raise HTTPException(status_code=500, detail="Analysis service not initialized")

    if _jira_connector is None:
        raise HTTPException(
            status_code=400,
            detail="Jira not configured. Please configure Jira connection first via /api/sources/jira/test"
        )

    return create_issue_analyzer(
        jira_connector=_jira_connector,
        index_manager=_index_manager,
        kb_manager=_kb_manager,
    )


@router.post("/issue/{issue_key}", response_model=IssueAnalysisResult)
async def analyze_issue(issue_key: str, request: AnalysisRequest = None):
    """Analyze a Jira issue.

    Args:
        issue_key: Issue key (e.g., "PROJ-123")
        request: Analysis request parameters (optional)

    Returns:
        IssueAnalysisResult with analysis and sources
    """
    analyzer = _get_analyzer()

    # Use defaults if no request body
    if request is None:
        request = AnalysisRequest(issue_key=issue_key)
    else:
        request.issue_key = issue_key

    try:
        result = await analyzer.analyze_issue(
            issue_key=request.issue_key,
            depth=request.depth,
            include_related=request.include_related,
            save_to_kb=request.save_to_kb,
        )
        return result

    except RuntimeError as e:
        logger.error(f"Failed to analyze issue {issue_key}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Error analyzing issue {issue_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/issue/{issue_key}", response_model=dict)
async def get_saved_analysis(issue_key: str):
    """Get saved analysis for an issue.

    Args:
        issue_key: Issue key

    Returns:
        Saved analysis data
    """
    if _kb_manager is None:
        raise HTTPException(status_code=500, detail="Knowledge base not initialized")

    try:
        result = _kb_manager.get_issue_analysis(issue_key)
        if result is None:
            raise HTTPException(status_code=404, detail=f"No analysis found for {issue_key}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis for {issue_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")


@router.get("/issues", response_model=list[dict])
async def list_analyzed_issues():
    """List all analyzed issues.

    Returns:
        List of issue metadata
    """
    if _kb_manager is None:
        raise HTTPException(status_code=500, detail="Knowledge base not initialized")

    try:
        issues = _kb_manager.list_analyzed_issues()
        return issues

    except Exception as e:
        logger.error(f"Error listing analyzed issues: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list issues: {str(e)}")
