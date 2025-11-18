import os
import json
import uuid
from typing import List, Dict, Any, Optional


class MemoryEntry:
    """
    A single stored memory item with provenance and a semantic vector.
    For this capstone, vector storage is optional; the structure is included for extensibility.
    """

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None,
        entry_id: Optional[str] = None
    ):
        self.id = entry_id or str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}
        self.vector = vector or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "vector": self.vector,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return MemoryEntry(
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            vector=data.get("vector", []),
            entry_id=data.get("id"),
        )


class MemoryBank:
    """
    A lightweight memory store for agent systems.

    Features:
    - Append/retrieve memory entries
    - Optional persistence to a JSON file
    - Filtering by metadata
    - Lookup by ID
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.entries: List[MemoryEntry] = []

        if self.storage_path and os.path.exists(self.storage_path):
            self._load()

    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None
    ) -> MemoryEntry:
        entry = MemoryEntry(content, metadata, vector)
        self.entries.append(entry)
        self._save()
        return entry

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def search_by_metadata(self, key: str, value: Any) -> List[MemoryEntry]:
        return [e for e in self.entries if e.metadata.get(key) == value]

    def all(self) -> List[MemoryEntry]:
        return list(self.entries)

    def _save(self):
        if not self.storage_path:
            return
        data = [e.to_dict() for e in self.entries]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.entries = [MemoryEntry.from_dict(d) for d in data]
