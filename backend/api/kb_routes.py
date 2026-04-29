"""Knowledge base API routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.config.kb_manager import KnowledgeBaseManager

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])

# Global manager instances
_kb_manager: KnowledgeBaseManager = None
_datasource_manager = None
_index_manager = None


def init_kb_routes(kb_manager: KnowledgeBaseManager, datasource_manager=None, index_manager=None):
    """Initialize knowledge base routes with managers."""
    global _kb_manager, _datasource_manager, _index_manager
    _kb_manager = kb_manager
    _datasource_manager = datasource_manager
    _index_manager = index_manager


class CreateKBRequest(BaseModel):
    """Request to create a knowledge base."""
    name: str
    description: str = ""
    datasource_ids: List[str] = []
    retrieval_config: dict = {}


class UpdateKBRequest(BaseModel):
    """Request to update a knowledge base."""
    name: Optional[str] = None
    description: Optional[str] = None
    datasource_ids: Optional[List[str]] = None
    retrieval_config: Optional[dict] = None


@router.post("")
async def create_kb(request: CreateKBRequest):
    """Create a new knowledge base."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    kb = _kb_manager.create(
        name=request.name,
        description=request.description,
        datasource_ids=request.datasource_ids,
        retrieval_config=request.retrieval_config
    )

    return kb.dict()


@router.get("")
async def list_kbs():
    """List all knowledge bases."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    kbs = _kb_manager.list()
    return [kb.dict() for kb in kbs]


@router.get("/{kb_id}")
async def get_kb(kb_id: str):
    """Get a knowledge base by ID."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    kb = _kb_manager.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return kb.dict()


@router.put("/{kb_id}")
async def update_kb(kb_id: str, request: UpdateKBRequest):
    """Update a knowledge base."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description
    if request.datasource_ids is not None:
        update_data["datasource_ids"] = request.datasource_ids
    if request.retrieval_config is not None:
        update_data["retrieval_config"] = request.retrieval_config

    kb = _kb_manager.update(kb_id, **update_data)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return kb.dict()


@router.delete("/{kb_id}")
async def delete_kb(kb_id: str):
    """Delete a knowledge base."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    success = _kb_manager.delete(kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return {"success": True}


@router.post("/{kb_id}/datasources/{datasource_id}")
async def add_datasource_to_kb(kb_id: str, datasource_id: str):
    """Add a data source to a knowledge base."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    kb = _kb_manager.add_datasource(kb_id, datasource_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return kb.dict()


@router.delete("/{kb_id}/datasources/{datasource_id}")
async def remove_datasource_from_kb(kb_id: str, datasource_id: str):
    """Remove a data source from a knowledge base."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    kb = _kb_manager.remove_datasource(kb_id, datasource_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return kb.dict()


@router.post("/{kb_id}/sync")
async def sync_knowledge_base(kb_id: str):
    """Sync all data sources in a knowledge base and build index."""
    if not _kb_manager:
        raise HTTPException(status_code=500, detail="KB manager not initialized")

    if not _datasource_manager:
        raise HTTPException(status_code=500, detail="DataSource manager not initialized")

    if not _index_manager:
        raise HTTPException(status_code=500, detail="Index manager not initialized")

    kb = _kb_manager.get(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    if not kb.datasource_ids:
        raise HTTPException(status_code=400, detail="No data sources configured for this knowledge base")

    try:
        from backend.services.datasource.file_datasource import FileDataSource

        all_documents = []

        # Fetch documents from all data sources
        for ds_id in kb.datasource_ids:
            ds = _datasource_manager.get(ds_id)
            if not ds:
                continue

            # Create data source instance
            if ds.type == "file":
                datasource = FileDataSource(ds.config.get("file_paths", []))
            else:
                # Skip unsupported types for now
                continue

            # Fetch documents
            documents = await datasource.fetch_documents()

            # Add metadata to track source
            for doc in documents:
                doc.metadata["datasource_id"] = ds_id
                doc.metadata["datasource_name"] = ds.name
                doc.metadata["knowledge_base_id"] = kb_id

            all_documents.extend(documents)

        if not all_documents:
            raise HTTPException(status_code=400, detail="No documents fetched from data sources")

        # Add to index
        print(f"[DEBUG] About to add {len(all_documents)} documents to index")
        print(f"[DEBUG] Index manager: {_index_manager}")
        print(f"[DEBUG] Current document count: {len(_index_manager.documents)}")
        await _index_manager.add_documents(all_documents)
        print(f"[DEBUG] After add, document count: {len(_index_manager.documents)}")

        # Update KB stats
        _kb_manager.update_index_stats(kb_id, len(all_documents))

        return {
            "success": True,
            "document_count": len(all_documents),
            "datasource_count": len(kb.datasource_ids),
            "message": f"Successfully synced {len(all_documents)} documents from {len(kb.datasource_ids)} data sources"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
