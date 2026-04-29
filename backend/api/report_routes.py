"""API routes for daily reports."""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict
import uuid

from backend.models.report import ReportRequest, ReportResponse, QuickReport, FullReport
from backend.services.knowledge.kb_manager import KnowledgeBaseManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Global dependencies (set from main.py)
_report_generator = None
_kb_manager: KnowledgeBaseManager = None
active_reports: Dict[str, ReportResponse] = {}


def init_report_routes(kb: KnowledgeBaseManager):
    """Initialize report routes with dependencies.

    Args:
        kb: KnowledgeBaseManager instance
    """
    global _kb_manager
    _kb_manager = kb
    logger.info("Report routes initialized")


def set_report_generator(generator):
    """Set report generator for routes.

    Args:
        generator: DailyReportGenerator instance
    """
    global _report_generator
    _report_generator = generator
    logger.info("Report generator set for report routes")


def _get_report_generator():
    """Get or create report generator.

    Returns:
        DailyReportGenerator instance

    Raises:
        HTTPException: If dependencies not initialized
    """
    if _report_generator is None:
        if _kb_manager is None:
            raise HTTPException(
                status_code=500,
                detail="Report routes not initialized"
            )
        # Import here to avoid circular dependency
        from backend.services.reports.daily_report_generator import create_report_generator
        from backend.api.analysis_routes import _get_analyzer

        analyzer = _get_analyzer()
        generator = create_report_generator(analyzer, _kb_manager)
        set_report_generator(generator)

    return _report_generator


@router.post("/daily", response_model=ReportResponse)
async def generate_daily_report(request: ReportRequest):
    """Generate a daily report.

    Args:
        request: Report generation request

    Returns:
        ReportResponse with report_id and initial status
    """
    generator = _get_report_generator()

    # Validate date format
    try:
        datetime.fromisoformat(request.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    report_id = str(uuid.uuid4())

    try:
        if request.mode == "quick":
            # Generate quick report synchronously
            quick_report = await generator.generate_quick_report(request.date)

            response = ReportResponse(
                report_id=report_id,
                status="complete",
                quick_report=quick_report
            )
            active_reports[report_id] = response

            return response

        elif request.mode == "full":
            # Start full report generation (will be completed via WebSocket)
            response = ReportResponse(
                report_id=report_id,
                status="generating"
            )
            active_reports[report_id] = response

            return response

        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use 'quick' or 'full'")

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily/{report_id}", response_model=ReportResponse)
async def get_daily_report(report_id: str):
    """Get a daily report by ID.

    Args:
        report_id: Report identifier

    Returns:
        ReportResponse with current status
    """
    if report_id not in active_reports:
        raise HTTPException(status_code=404, detail="Report not found")

    return active_reports[report_id]


@router.get("/daily/saved/{date}")
async def get_saved_report(date: str):
    """Get a saved daily report from knowledge base.

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        Saved report data
    """
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="Knowledge base manager not initialized")

    try:
        report_data = _kb_manager.get_daily_report(date)
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        return report_data
    except Exception as e:
        logger.error(f"Failed to get saved report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily/list")
async def list_saved_reports():
    """List all saved daily reports.

    Returns:
        List of report dates and metadata
    """
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="Knowledge base manager not initialized")

    try:
        reports = _kb_manager.list_daily_reports()
        return {"reports": reports}
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/daily/{report_id}")
async def websocket_daily_report(websocket: WebSocket, report_id: str):
    """WebSocket endpoint for real-time full report generation.

    Args:
        websocket: WebSocket connection
        report_id: Report identifier
    """
    await websocket.accept()

    generator = _get_report_generator()
    if not generator:
        await websocket.send_json({"type": "error", "message": "Report generator not initialized"})
        await websocket.close()
        return

    if report_id not in active_reports:
        await websocket.send_json({"type": "error", "message": "Report not found"})
        await websocket.close()
        return

    try:
        # Get report request data
        report = active_reports[report_id]

        # Send quick report first
        await websocket.send_json({"type": "status", "message": "Generating quick report..."})
        quick_report = await generator.generate_quick_report(report.quick_report.date if report.quick_report else datetime.now().strftime("%Y-%m-%d"))

        await websocket.send_json({
            "type": "quick_report",
            "data": quick_report.model_dump()
        })

        # Update stored report
        report.quick_report = quick_report
        report.status = "analyzing"

        # Generate full report
        await websocket.send_json({"type": "status", "message": "Analyzing issues..."})
        full_report = await generator.generate_full_report(quick_report.date)

        # Save to knowledge base
        await websocket.send_json({"type": "status", "message": "Saving to knowledge base..."})
        _kb_manager.save_daily_report(quick_report.date, full_report)

        # Send complete report
        await websocket.send_json({
            "type": "complete",
            "data": full_report.model_dump()
        })

        # Update stored report
        report.full_report = full_report
        report.status = "complete"

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for report {report_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket report generation: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
        report.status = "error"
        report.error = str(e)
    finally:
        await websocket.close()
