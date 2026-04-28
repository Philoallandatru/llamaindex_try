"""Data source manager."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from backend.models.datasource import DataSourceConfig
from backend.services.config.config_manager import ConfigManager


class DataSourceManager:
    """Manages data source configurations."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config_file = "datasources.json"

    def create(self, name: str, type: str, config: Dict, description: str = "") -> DataSourceConfig:
        """Create a new data source."""
        datasource_id = str(uuid.uuid4())
        datasource = DataSourceConfig(
            id=datasource_id,
            name=name,
            type=type,
            config=config,
            description=description,
        )

        self.config_manager.create(self.config_file, datasource_id, datasource.dict())

        return datasource

    def get(self, datasource_id: str) -> Optional[DataSourceConfig]:
        """Get a data source by ID."""
        datasources = self.list()
        for ds in datasources:
            if ds.id == datasource_id and ds.status == "active":
                return ds
        return None

    def list(self, include_deleted: bool = False) -> List[DataSourceConfig]:
        """List all data sources."""
        data = self.config_manager.load(self.config_file)
        if not data:
            return []

        datasources = [DataSourceConfig(**ds) for ds in data.values()]

        if not include_deleted:
            datasources = [ds for ds in datasources if ds.status == "active"]

        return datasources

    def update(self, datasource_id: str, **kwargs) -> Optional[DataSourceConfig]:
        """Update a data source."""
        ds = self.config_manager.get_by_id(self.config_file, datasource_id)
        if not ds:
            return None

        for key, value in kwargs.items():
            if key in ds:
                ds[key] = value
        ds['updated_at'] = datetime.utcnow().isoformat()

        self.config_manager.update(self.config_file, datasource_id, ds)
        return DataSourceConfig(**ds)

    def delete(self, datasource_id: str) -> bool:
        """Soft delete a data source."""
        return self.update(datasource_id, status="deleted") is not None

    def update_sync_stats(self, datasource_id: str, document_count: int) -> Optional[DataSourceConfig]:
        """Update sync statistics."""
        return self.update(
            datasource_id,
            last_sync=datetime.utcnow().isoformat(),
            sync_count=self.get(datasource_id).sync_count + 1 if self.get(datasource_id) else 1,
            document_count=document_count,
        )
