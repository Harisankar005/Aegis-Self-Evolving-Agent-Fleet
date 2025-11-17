import uuid
import time
from typing import List, Dict, Any


class MemoryBank:
    """
    Long-term memory storage.
    Works like a simple vector store + metadata registry.
    """

    def __init__(self):
        # In real production: Pinecone, Milvus, Chroma
        self.storage: List[Dict[str, Any]] = []

    def add(self, content: str, source_agent: str, metadata=None):
        """
        Store a memory item with provenance.
        """
        mem = {
            "id": str(uuid.uuid4()),
            "content": content,
            "source_agent": source_agent,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        self.storage.append(mem)
        return mem

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Mock semantic search using keyword matching.
        Replace with vector DB in production.
        """
        results = []
        for mem in self.storage:
            if query.lower() in mem["content"].lower():
                results.append(mem)

        # Sort by recency
        results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
        return results[:top_k]

    def consolidate(self, session_trace):
        """
        Converts session trace into concise long-term memory items.
        Useful for summarizing executed tasks.
        """
        summary = []
        for event in session_trace:
            summary.append(f"{event['agent']} → {event['output']}")
        
        content = "\n".join(summary)
        return self.add(
            content=content,
            source_agent="SessionConsolidator",
            metadata={"type": "session_summary"}
        )

    def delete(self, memory_id: str):
        self.storage = [m for m in self.storage if m["id"] != memory_id]

    def get_all(self):
        return self.storage
