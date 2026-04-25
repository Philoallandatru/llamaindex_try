"""Data source API routes."""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config.settings import settings
from backend.models.api import (
    ConfluenceConnectionRequest,
    ConnectionTestResponse,
    JiraConnectionRequest,
    SyncSourceResponse,
    UploadFileResponse,
)
from backend.services.indexing.index_manager import IndexManager
from backend.services.ingestion.confluence_connector import ConfluenceConnector
from backend.services.ingestion.document_parser import DocumentParser
from backend.services.ingestion.jira_connector import JiraConnector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sources", tags=["sources"])

# Global instance (will be initialized in main.py)
index_manager: Optional[IndexManager] = None


def init_source_routes(manager: IndexManager) -> None:
    """Initialize source routes with dependencies.

    Args:
        manager: IndexManager instance
    """
    global index_manager
    index_manager = manager
    logger.info("Initialized source routes")


@router.post("/upload", response_model=UploadFileResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and index a file.

    Supports: PDF, DOCX, XLSX, PPTX

    Args:
        file: Uploaded file

    Returns:
        Upload status and document count
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        # Save file
        file_path = settings.upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Saved uploaded file: {file_path}")

        # Parse file
        parser = DocumentParser(use_mineru=True)

        if not parser.is_supported(file_path):
            file_path.unlink()  # Delete unsupported file
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_path.suffix}",
            )

        documents = await parser.parse_file(file_path)

        # Add to index
        await index_manager.add_documents(documents, show_progress=False)

        logger.info(f"Indexed {len(documents)} documents from {file.filename}")

        return UploadFileResponse(
            success=True,
            message=f"File uploaded and indexed successfully",
            file_path=str(file_path),
            documents_created=len(documents),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/test", response_model=ConnectionTestResponse)
async def test_jira_connection(request: JiraConnectionRequest):
    """Test Jira connection.

    Args:
        request: Jira connection details

    Returns:
        Connection test result
    """
    try:
        connector = JiraConnector(
            base_url=request.base_url,
            email=request.email,
            api_token=request.api_token,
        )

        result = await connector.test_connection()

        return ConnectionTestResponse(**result)

    except Exception as e:
        logger.error(f"Jira connection test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.post("/jira/sync", response_model=SyncSourceResponse)
async def sync_jira(request: JiraConnectionRequest):
    """Sync Jira issues and add to index.

    Args:
        request: Jira connection and query details

    Returns:
        Sync status
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        connector = JiraConnector(
            base_url=request.base_url,
            email=request.email,
            api_token=request.api_token,
        )

        # Fetch issues
        if request.jql:
            documents = await connector.fetch_issues(
                jql=request.jql,
                max_results=request.max_results,
            )
        elif request.project_key:
            documents = await connector.fetch_project(
                project_key=request.project_key,
                max_results=request.max_results,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either jql or project_key must be provided",
            )

        # Add to index
        await index_manager.add_documents(documents, show_progress=False)

        logger.info(f"Synced {len(documents)} Jira issues")

        return SyncSourceResponse(
            success=True,
            message=f"Synced {len(documents)} Jira issues",
            documents_synced=len(documents),
            source_id=request.project_key or "jira",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync Jira: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confluence/test", response_model=ConnectionTestResponse)
async def test_confluence_connection(request: ConfluenceConnectionRequest):
    """Test Confluence connection.

    Args:
        request: Confluence connection details

    Returns:
        Connection test result
    """
    try:
        connector = ConfluenceConnector(
            base_url=request.base_url,
            email=request.email,
            api_token=request.api_token,
        )

        result = await connector.test_connection()

        return ConnectionTestResponse(**result)

    except Exception as e:
        logger.error(f"Confluence connection test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.post("/confluence/sync", response_model=SyncSourceResponse)
async def sync_confluence(request: ConfluenceConnectionRequest):
    """Sync Confluence pages and add to index.

    Args:
        request: Confluence connection and query details

    Returns:
        Sync status
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        connector = ConfluenceConnector(
            base_url=request.base_url,
            email=request.email,
            api_token=request.api_token,
        )

        # Fetch pages
        if request.page_id:
            document = await connector.fetch_page(page_id=request.page_id)
            documents = [document]
        elif request.space_key:
            documents = await connector.fetch_space(
                space_key=request.space_key,
                max_pages=request.max_pages,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either page_id or space_key must be provided",
            )

        # Add to index
        await index_manager.add_documents(documents, show_progress=False)

        logger.info(f"Synced {len(documents)} Confluence pages")

        return SyncSourceResponse(
            success=True,
            message=f"Synced {len(documents)} Confluence pages",
            documents_synced=len(documents),
            source_id=request.space_key or request.page_id or "confluence",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync Confluence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_sources():
    """List all configured data sources.

    Returns:
        List of data sources
    """
    # This is a placeholder - in a real implementation,
    # you would store source configurations in a database
    return {
        "sources": [],
        "message": "Source listing not yet implemented",
    }
