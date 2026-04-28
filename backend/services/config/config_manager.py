"""Configuration manager for JSON-based configuration storage."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigManager:
    """Manages JSON configuration files with CRUD operations."""

    def __init__(self, config_dir: Path):
        """Initialize config manager.

        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self, filename: str) -> Dict[str, Any]:
        """Load configuration file.

        Args:
            filename: Name of the configuration file

        Returns:
            Dictionary of configuration items
        """
        path = self.config_dir / filename
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding='utf-8'))

    def save(self, filename: str, data: Dict[str, Any]) -> None:
        """Save configuration file.

        Args:
            filename: Name of the configuration file
            data: Dictionary of configuration items to save
        """
        path = self.config_dir / filename
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    def get_by_id(self, filename: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration item by ID.

        Args:
            filename: Name of the configuration file
            item_id: ID of the item to retrieve

        Returns:
            Configuration item or None if not found
        """
        data = self.load(filename)
        return data.get(item_id)

    def list_all(self, filename: str) -> List[Dict[str, Any]]:
        """List all configuration items.

        Args:
            filename: Name of the configuration file

        Returns:
            List of all configuration items
        """
        data = self.load(filename)
        return list(data.values())

    def create(self, filename: str, item_id: str, item: Dict[str, Any]) -> None:
        """Create a new configuration item.

        Args:
            filename: Name of the configuration file
            item_id: ID for the new item
            item: Configuration item data
        """
        data = self.load(filename)
        data[item_id] = item
        self.save(filename, data)

    def update(self, filename: str, item_id: str, item: Dict[str, Any]) -> None:
        """Update an existing configuration item.

        Args:
            filename: Name of the configuration file
            item_id: ID of the item to update
            item: Updated configuration item data
        """
        data = self.load(filename)
        if item_id in data:
            data[item_id] = item
            self.save(filename, data)

    def delete(self, filename: str, item_id: str) -> None:
        """Soft delete a configuration item.

        Args:
            filename: Name of the configuration file
            item_id: ID of the item to delete
        """
        data = self.load(filename)
        if item_id in data:
            data[item_id]['status'] = 'deleted'
            self.save(filename, data)
