"""Data source API routes."""

import logging
import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.services.config.datasource_manager import DataSourceManager
from backend.services.datasource.file_datasource import FileDataSource

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/datasources", tags=["datasources"])

# Global manager instance
_datasource_manager: DataSourceManager = None
_index_manager = None  # Will be set during initialization


def init_datasource_routes(datasource_manager: DataSourceManager, index_manager=None):
    """Initialize datasource routes with manager."""
    global _datasource_manager, _index_manager
    _datasource_manager = datasource_manager
    _index_manager = index_manager


class CreateDataSourceRequest(BaseModel):
    """Request to create a data source."""
    name: str
    description: str = ""
    type: str
    config: dict


class UpdateDataSourceRequest(BaseModel):
    """Request to update a data source."""
    name: str = None
    description: str = None
    config: dict = None


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files for File data source.

    Returns list of saved file paths.
    """
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []

    for file in files:
        # Save file
        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        saved_paths.append(str(file_path.absolute()))

    return {"file_paths": saved_paths}


@router.post("")
async def create_datasource(request: CreateDataSourceRequest):
    """Create a new data source."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    # Validate config based on type
    if request.type == "file":
        file_paths = request.config.get("file_paths", [])
        if not file_paths:
            raise HTTPException(status_code=400, detail="file_paths required for File data source")

        # Validate files exist
        datasource = FileDataSource(file_paths)
        is_valid, error = await datasource.validate_config()
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

    # Create data source
    ds = _datasource_manager.create(
        name=request.name,
        description=request.description,
        type=request.type,
        config=request.config
    )

    return ds.dict()


@router.get("")
async def list_datasources():
    """List all data sources."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    datasources = _datasource_manager.list()
    return [ds.dict() for ds in datasources]


@router.get("/{datasource_id}")
async def get_datasource(datasource_id: str):
    """Get a data source by ID."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    ds = _datasource_manager.get(datasource_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")

    return ds.dict()


@router.put("/{datasource_id}")
async def update_datasource(datasource_id: str, request: UpdateDataSourceRequest):
    """Update a data source."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description
    if request.config is not None:
        update_data["config"] = request.config

    ds = _datasource_manager.update(datasource_id, **update_data)
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")

    return ds.dict()


@router.delete("/{datasource_id}")
async def delete_datasource(datasource_id: str):
    """Delete a data source."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    success = _datasource_manager.delete(datasource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Data source not found")

    return {"success": True}


@router.post("/{datasource_id}/validate")
async def validate_datasource(datasource_id: str):
    """Validate a data source configuration."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    ds = _datasource_manager.get(datasource_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Create appropriate data source instance
    if ds.type == "file":
        datasource = FileDataSource(ds.config.get("file_paths", []))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported data source type: {ds.type}")

    is_valid, error = await datasource.validate_config()

    return {
        "valid": is_valid,
        "error": error if not is_valid else None
    }


@router.post("/{datasource_id}/sync")
async def sync_datasource(datasource_id: str):
    """Sync a data source and index its documents."""
    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    if not _index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    ds = _datasource_manager.get(datasource_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        # Create data source instance
        if ds.type == "file":
            file_paths = ds.config.get("file_paths", [])
            logger.info(f"Creating FileDataSource with paths: {file_paths}")
            datasource = FileDataSource(file_paths)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data source type: {ds.type}")

        # Fetch documents
        logger.info(f"Fetching documents...")
        documents = await datasource.fetch_documents()
        logger.info(f"Fetched {len(documents)} documents")

        if not documents:
            raise HTTPException(status_code=400, detail="No documents fetched")

        # Add to index
        logger.info(f"Adding documents to index...")
        await _index_manager.add_documents(documents)

        # Update sync stats
        _datasource_manager.update_sync_stats(datasource_id, len(documents))

        return {
            "success": True,
            "document_count": len(documents),
            "message": f"Successfully synced {len(documents)} documents"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception during sync: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

