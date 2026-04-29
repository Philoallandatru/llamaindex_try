"""Knowledge base manager."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from backend.models.knowledge_base import KnowledgeBase
from backend.services.config.config_manager import ConfigManager


class KnowledgeBaseManager:
    """Manages knowledge base configurations."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config_file = "knowledge_bases.json"

    def create(
        self,
        name: str,
        description: str = "",
        datasource_ids: Optional[List[str]] = None,
        retrieval_config: Optional[Dict] = None,
    ) -> KnowledgeBase:
        """Create a new knowledge base."""
        kb_id = str(uuid.uuid4())
        collection_name = f"kb_{kb_id[:8]}"

        kb = KnowledgeBase(
            id=kb_id,
            name=name,
            description=description,
            datasource_ids=datasource_ids or [],
            collection_name=collection_name,
            retrieval_config=retrieval_config or {},
        )

        self.config_manager.create(self.config_file, kb_id, kb.dict())

        return kb

    def get(self, kb_id: str) -> Optional[KnowledgeBase]:
        """Get a knowledge base by ID."""
        kb_data = self.config_manager.get_by_id(self.config_file, kb_id)
        if kb_data and kb_data.get('status') == 'active':
            return KnowledgeBase(**kb_data)
        return None

    def list(self, include_deleted: bool = False) -> List[KnowledgeBase]:
        """List all knowledge bases."""
        data = self.config_manager.load(self.config_file)
        if not data:
            return []

        kbs = [KnowledgeBase(**kb) for kb in data.values()]

        if not include_deleted:
            kbs = [kb for kb in kbs if kb.status == 'active']

        return kbs

    def update(self, kb_id: str, **kwargs) -> Optional[KnowledgeBase]:
        """Update a knowledge base."""
        kb = self.config_manager.get_by_id(self.config_file, kb_id)
        if not kb:
            return None

        for key, value in kwargs.items():
            if key in kb:
                kb[key] = value
        kb['updated_at'] = datetime.utcnow().isoformat()

        self.config_manager.update(self.config_file, kb_id, kb)
        return KnowledgeBase(**kb)

    def delete(self, kb_id: str) -> bool:
        """Soft delete a knowledge base."""
        return self.update(kb_id, status='deleted') is not None

    def add_datasource(self, kb_id: str, datasource_id: str) -> Optional[KnowledgeBase]:
        """Add a data source to a knowledge base."""
        kb = self.get(kb_id)
        if kb and datasource_id not in kb.datasource_ids:
            kb.datasource_ids.append(datasource_id)
            return self.update(kb_id, datasource_ids=kb.datasource_ids)
        return kb

    def remove_datasource(self, kb_id: str, datasource_id: str) -> Optional[KnowledgeBase]:
        """Remove a data source from a knowledge base."""
        kb = self.get(kb_id)
        if kb and datasource_id in kb.datasource_ids:
            kb.datasource_ids.remove(datasource_id)
            return self.update(kb_id, datasource_ids=kb.datasource_ids)
        return kb

    def update_index_stats(self, kb_id: str, document_count: int) -> Optional[KnowledgeBase]:
        """Update index statistics."""
        return self.update(
            kb_id,
            document_count=document_count,
        )
