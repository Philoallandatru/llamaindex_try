"""Track indexed items to support incremental indexing"""

import json
from pathlib import Path
from datetime import datetime
from typing import Set

class IndexTracker:
    def __init__(self, cache_path: Path):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if self.cache_path.exists():
            with open(self.cache_path) as f:
                return json.load(f)
        return {"jira_issues": {}, "confluence_pages": {}, "documents": {}}

    def _save(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def is_indexed(self, category: str, item_id: str) -> bool:
        return item_id in self.data.get(category, {})

    def mark_indexed(self, category: str, item_id: str, metadata: dict = None):
        if category not in self.data:
            self.data[category] = {}
        self.data[category][item_id] = {
            "indexed_at": datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save()

    def get_indexed_items(self, category: str) -> Set[str]:
        return set(self.data.get(category, {}).keys())

    def clear(self):
        self.data = {"jira_issues": {}, "confluence_pages": {}, "documents": {}}
        self._save()
