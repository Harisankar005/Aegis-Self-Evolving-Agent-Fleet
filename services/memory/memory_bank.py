"""
memory_bank.py

Implements the Long-Term Memory (LTM) system for the Aegis multi-agent project.
This module provides:

✔ Structured long-term memory storage
✔ Memory retrieval with scoring & relevance filtering
✔ Memory provenance & lineage tracking
✔ Memory consolidation (summaries)
✔ Context engineering support
✔ In-memory + pluggable storage backend (extensible)

This follows the "Sessions & Memory" whitepaper concepts:
- Memory as extracted knowledge across sessions
- Provenance: knowing which agent created which data
- Retrieval timing & scoring for context construction
- Blocking vs background operations
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import time
import uuid


class MemoryItem:
    """
    Represents a single memory entry.
    Includes:
    - content: natural language text
    - metadata: tags, agent, timestamp, importance, etc.
    - provenance: which agent/tool created this
    """

    def __init__(
        self,
        content: str,
        memory_type: str,
        importance: float,
        agent: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.memory_type = memory_type          # e.g., "fact", "preference", "summary", "result"
        self.importance = importance            # 0.0 – 1.0 (used during retrieval)
        self.agent = agent
        self.session_id = session_id
        self.timestamp = time.time()
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "agent": self.agent,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class MemoryBank:
    """
    The central long-term memory store for Aegis.

    Key features:
    -------------
    ✔ Adds memories from agents across sessions
    ✔ Retrieves relevant memories for context construction
    ✔ Implements memory provenance (who generated what)
    ✔ Provides compaction/summarization APIs (optional)
    ✔ Supports plugin backends (vector DB, file store) if extended later

    This is the “background” memory system described in the context-engineering whitepaper.
    """

    def __init__(self):
        # In production, replace with vector DB, Firestore, Postgres, Redis, etc.
        self._store: List[MemoryItem] = []

    # -------------------------------------------------------------------------
    #                               ADD MEMORY
    # -------------------------------------------------------------------------
    def add_memory(
        self,
        content: str,
        memory_type: str,
        importance: float,
        agent: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryItem:
        """
        Store a new memory. Typically called at the end of a tool/agent step.

        importance:
            A signal used for retrieval relevance. 0.0–1.0.
            Can be based on LLM scoring or rule heuristics.
        """
        memory = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            agent=agent,
            session_id=session_id,
            metadata=metadata,
        )

        self._store.append(memory)
        return memory

    # -------------------------------------------------------------------------
    #                              RETRIEVE MEMORY
    # -------------------------------------------------------------------------
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        memory_types: Optional[List[str]] = None,
    ) -> List[MemoryItem]:
        """
        Simple keyword + importance retrieval.

        In production:
        - Replace with vector DB (FAISS, Pinecone)
        - Add embeddings
        - Add recency/time decay

        memory_types: filter by memory category (optional).
        """

        # Filter by memory_types if provided
        candidates = [
            m for m in self._store
            if (memory_types is None or m.memory_type in memory_types)
        ]

        # Very simple scoring: keyword match count + importance
        def score(m: MemoryItem):
            kw_score = sum(1 for word in query.lower().split() if word in m.content.lower())
            return kw_score + m.importance

        ranked = sorted(candidates, key=score, reverse=True)
        return ranked[:top_k]

    # -------------------------------------------------------------------------
    #                          CONSOLIDATE / SUMMARIZE MEMORY
    # -------------------------------------------------------------------------
    def consolidate_memories(self, session_id: str) -> MemoryItem:
        """
        Creates a summary of all important memories for a session.
        In production: call LLM summarizer (Gemini) with proper prompt.

        Here: simple concatenation summary (mock).
        """

        related = [m for m in self._store if m.session_id == session_id and m.importance > 0.4]

        if not related:
            return None

        combined_text = "\n".join([m.content for m in related])

        summary = self.add_memory(
            content=f"[SUMMARY for session={session_id}]:\n{combined_text}",
            memory_type="summary",
            importance=0.9,
            agent="MemoryBank",
            session_id=session_id,
            metadata={"source_count": len(related)},
        )

        return summary

    # -------------------------------------------------------------------------
    #                              DEBUG / UTILS
    # -------------------------------------------------------------------------
    def dump_all(self) -> List[Dict[str, Any]]:
        """Return all memories as dictionaries."""
        return [m.to_dict() for m in self._store]

    def clear(self):
        """Reset the entire memory bank."""
        self._store = []
