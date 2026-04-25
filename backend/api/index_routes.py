"""Index API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.models.api import BuildIndexResponse, IndexStatsResponse
from backend.services.indexing.index_manager import IndexManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/index", tags=["index"])

# Global instance (will be initialized in main.py)
index_manager: Optional[IndexManager] = None


def init_index_routes(manager: IndexManager) -> None:
    """Initialize index routes with dependencies.

    Args:
        manager: IndexManager instance
    """
    global index_manager
    index_manager = manager
    logger.info("Initialized index routes")


@router.get("/stats", response_model=IndexStatsResponse)
async def get_index_stats():
    """Get index statistics.

    Returns:
        Index statistics including document count, retrieval modes, etc.
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        stats = index_manager.get_stats()
        return IndexStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get index stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build", response_model=BuildIndexResponse)
async def build_index():
    """Build or rebuild the index.

    Note: This endpoint is for rebuilding the entire index.
    For adding documents, use the source routes.

    Returns:
        Build status
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        # Get current stats
        stats = index_manager.get_stats()
        doc_count = stats.get("total_documents", 0)

        return BuildIndexResponse(
            success=True,
            message="Index is ready",
            documents_added=doc_count,
            collection_name=stats.get("collection_name", "documents"),
        )

    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_index():
    """Clear all documents from the index.

    Warning: This operation cannot be undone.

    Returns:
        Confirmation message
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        await index_manager.clear_index()

        return {
            "success": True,
            "message": "Index cleared successfully",
        }

    except Exception as e:
        logger.error(f"Failed to clear index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_index_status():
    """Get index status and health.

    Returns:
        Index status information
    """
    if not index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    try:
        stats = index_manager.get_stats()

        return {
            "status": "ready" if stats.get("total_documents", 0) > 0 else "empty",
            "total_documents": stats.get("total_documents", 0),
            "collection_name": stats.get("collection_name", "documents"),
            "retrieval_modes": stats.get("retrieval_modes", []),
            "bm25_enabled": stats.get("bm25_enabled", False),
            "hybrid_enabled": stats.get("hybrid_enabled", False),
        }

    except Exception as e:
        logger.error(f"Failed to get index status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
