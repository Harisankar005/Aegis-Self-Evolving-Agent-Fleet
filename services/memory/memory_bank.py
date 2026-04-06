"""
memory_bank.py
--------------
Long-Term Memory (LTM) system for the Aegis multi-agent project.

Provides:
✔ Structured long-term memory storage
✔ Memory retrieval with importance scoring
✔ Memory provenance & lineage tracking
✔ Session-level consolidation (summarise)
✔ In-memory store with a pluggable backend interface

FIX LOG (v2):
- store(namespace, key, value) helper added — tests and agents call mb.store();
  the v1 API only had add_memory() which has a different signature.
- retrieve(namespace) now works with just a namespace argument (as tests expect)
  in addition to the full-text query mode used by the orchestrator.
- Each stored item now always contains "key" and "timestamp" fields so that
  test_memory_provenance passes without modification.
- consolidate_memories() now returns an empty dict (not None) when there is
  nothing to consolidate, so callers don't need None guards.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


class MemoryItem:
    """
    A single memory entry.

    Attributes
    ----------
    id           : Unique identifier.
    content      : Natural-language text.
    memory_type  : Category, e.g. "fact", "preference", "summary", "result".
    importance   : Retrieval-relevance weight (0.0–1.0).
    agent        : Which agent created this entry.
    session_id   : Session the entry belongs to.
    namespace    : Optional grouping key (used by store/retrieve helpers).
    key          : Short descriptor label (used by store/retrieve helpers).
    timestamp    : Unix epoch float.
    metadata     : Arbitrary extra payload.
    """

    def __init__(
        self,
        content: str,
        memory_type: str,
        importance: float,
        agent: str,
        session_id: str,
        namespace: str = "default",
        key: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id          = str(uuid.uuid4())
        self.content     = content
        self.memory_type = memory_type
        self.importance  = importance
        self.agent       = agent
        self.session_id  = session_id
        self.namespace   = namespace
        self.key         = key
        self.timestamp   = time.time()
        self.metadata    = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":          self.id,
            "content":     self.content,
            "memory_type": self.memory_type,
            "importance":  self.importance,
            "agent":       self.agent,
            "session_id":  self.session_id,
            "namespace":   self.namespace,
            "key":         self.key,
            "timestamp":   self.timestamp,
            "metadata":    self.metadata,
            # convenience alias so tests can do item["value"]
            "value":       self.content,
        }


class MemoryBank:
    """
    The central long-term memory store for Aegis.

    Public API
    ----------
    add_memory(content, memory_type, importance, agent, session_id, **kwargs)
        Low-level write used by the consolidation layer.

    store(namespace, key, value, agent="system", session_id="global", importance=0.5)
        Convenience write used by agents and tests.

    retrieve(namespace_or_query, top_k=5, memory_types=None)
        Dual-mode retrieval:
        - If called with a single short string that matches a namespace → returns
          all items in that namespace (used by tests).
        - Otherwise → keyword + importance ranked retrieval over full content
          (used by the orchestrator / agents).

    consolidate_memories(session_id)
        Summarise important memories for a session into a single entry.
    """

    def __init__(self):
        self._store: List[MemoryItem] = []

    # ------------------------------------------------------------------ #
    # Low-level write
    # ------------------------------------------------------------------ #

    def add_memory(
        self,
        content: str,
        memory_type: str,
        importance: float,
        agent: str,
        session_id: str,
        namespace: str = "default",
        key: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryItem:
        """
        Store a new memory. Typically called at the end of an agent step.

        Parameters
        ----------
        content      : Natural-language text to store.
        memory_type  : Category tag ("fact", "summary", "result", etc.).
        importance   : 0.0–1.0 retrieval weight.
        agent        : Name of the agent creating this memory.
        session_id   : Session identifier.
        namespace    : Logical grouping (default "default").
        key          : Short label / descriptor.
        metadata     : Arbitrary extra dict.
        """
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            agent=agent,
            session_id=session_id,
            namespace=namespace,
            key=key,
            metadata=metadata,
        )
        self._store.append(item)
        return item

    # ------------------------------------------------------------------ #
    # Convenience write (used by agents and tests)
    # ------------------------------------------------------------------ #

    def store(
        self,
        namespace: str,
        key: str,
        value: str,
        agent: str = "system",
        session_id: str = "global",
        importance: float = 0.5,
    ) -> MemoryItem:
        """
        Simplified write interface.

        Parameters
        ----------
        namespace  : Logical bucket (e.g. "user_pref", "mission").
        key        : Descriptor label (e.g. "product_interest").
        value      : The text content to store.
        agent      : Source agent name.
        session_id : Session context.
        importance : Retrieval weight (default 0.5).
        """
        return self.add_memory(
            content=value,
            memory_type="fact",
            importance=importance,
            agent=agent,
            session_id=session_id,
            namespace=namespace,
            key=key,
        )

    # ------------------------------------------------------------------ #
    # Retrieval
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        namespace_or_query: str,
        top_k: int = 5,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Dual-mode retrieval.

        Mode A — namespace lookup (tests / simple agents):
            retrieve("user_pref") → all items whose namespace == "user_pref"

        Mode B — full-text ranked search (orchestrator / advanced agents):
            retrieve("AI marketing trends for students") → keyword + importance ranking

        The mode is selected automatically: if the query string exactly matches
        a known namespace, Mode A is used; otherwise Mode B applies.

        Returns a list of plain dicts (via MemoryItem.to_dict()).
        """
        known_namespaces = {m.namespace for m in self._store}

        if namespace_or_query in known_namespaces:
            # Mode A: namespace filter
            items = [
                m for m in self._store
                if m.namespace == namespace_or_query
                and (memory_types is None or m.memory_type in memory_types)
            ]
            return [m.to_dict() for m in items]

        # Mode B: ranked retrieval
        query = namespace_or_query
        candidates = [
            m for m in self._store
            if memory_types is None or m.memory_type in memory_types
        ]

        def _score(m: MemoryItem) -> float:
            kw_hits = sum(
                1 for word in query.lower().split()
                if word in m.content.lower()
            )
            return kw_hits + m.importance

        ranked = sorted(candidates, key=_score, reverse=True)
        return [m.to_dict() for m in ranked[:top_k]]

    # ------------------------------------------------------------------ #
    # Consolidation / summarisation
    # ------------------------------------------------------------------ #

    def consolidate_memories(self, session_id: str) -> Dict[str, Any]:
        """
        Create a summary of all important memories for *session_id*.

        In production: call an LLM summariser (Gemini) with a proper prompt.
        Here: simple concatenation (mock).

        Returns the summary MemoryItem as a dict, or an empty dict if there
        is nothing important enough to consolidate.
        """
        related = [
            m for m in self._store
            if m.session_id == session_id and m.importance > 0.4
        ]

        if not related:
            return {}

        combined = "\n".join(m.content for m in related)
        summary_item = self.add_memory(
            content=f"[SUMMARY for session={session_id}]:\n{combined}",
            memory_type="summary",
            importance=0.9,
            agent="MemoryBank",
            session_id=session_id,
            namespace="summaries",
            key=f"summary_{session_id}",
            metadata={"source_count": len(related)},
        )
        result = summary_item.to_dict()
        result["summary"] = result["content"]   # convenience alias
        return result

    # ------------------------------------------------------------------ #
    # Debug utilities
    # ------------------------------------------------------------------ #

    def dump_all(self) -> List[Dict[str, Any]]:
        """Return all stored memories as plain dicts."""
        return [m.to_dict() for m in self._store]

    def clear(self):
        """Reset the entire memory bank."""
        self._store = []

    def __len__(self) -> int:
        return len(self._store)
