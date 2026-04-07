"""
memory_consolidation.py
-----------------------
Memory consolidation logic for the Aegis agent system.

Extracts relevant signals from agent outputs and trace logs, then:
1. Scores their relevance.
2. Summarises each chunk into a compact form.
3. Deduplicates using SHA-256 content hashes.
4. Returns a clean list of consolidated memory entries ready for MemoryBank.

This version is fully API-key-free.
Extend with:
- LLM summarisation → Gemini
- Embeddings → vector DB similarity
- Richer relevance scoring → semantic distance
"""

import hashlib
import time
import uuid
from typing import Any, Dict, List


class MemoryConsolidation:
    """
    Consolidates raw session event data into long-term memory entries.

    Input format (session_events):
    --------------------------------
    [
        {
            "agent":     "MarketResearchAgent",
            "output":    {"insights": "...", "confidence": 0.85},
            "timestamp": 1731200301.24
        },
        ...
    ]

    Output format:
    --------------------------------
    [
        {
            "id":        "<uuid>",
            "summary":   "<first sentence or 120 chars>",
            "source":    "MarketResearchAgent",
            "timestamp": 1731200301.24,
            "tags":      ["market", "insight"],
            "hash":      "<sha256 hex>",
        },
        ...
    ]
    """

    def __init__(self, relevance_threshold: float = 0.1):
        self.relevance_threshold = relevance_threshold

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def consolidate(self, session_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Full consolidation pipeline:
        1. Extract raw memory candidates from events.
        2. Filter by relevance score.
        3. Summarise each candidate.
        4. Deduplicate by content hash.
        """
        raw      = self._extract_raw_memories(session_events)
        filtered = [m for m in raw if m["relevance"] >= self.relevance_threshold]
        summaries = [self._summarise_memory(m) for m in filtered]
        return self._dedupe(summaries)

    # ------------------------------------------------------------------ #
    # Step 1: Extraction
    # ------------------------------------------------------------------ #

    def _extract_raw_memories(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        memories = []
        for evt in events:
            agent     = evt.get("agent", "unknown")
            output    = evt.get("output", evt.get("content", {}))
            ts        = evt.get("timestamp", time.time())
            text      = self._stringify(output)
            relevance = self._estimate_relevance(text)
            memories.append({
                "agent":     agent,
                "raw_text":  text,
                "timestamp": ts,
                "relevance": relevance,
            })
        return memories

    # ------------------------------------------------------------------ #
    # Step 2: Relevance scoring
    # ------------------------------------------------------------------ #

    def _estimate_relevance(self, text: str) -> float:
        """
        Heuristic: longer text → higher relevance, normalised to 0–1.
        Replace with embedding similarity in production.
        """
        if not text:
            return 0.0
        return round(min(len(text) / 200.0, 1.0), 3)

    # ------------------------------------------------------------------ #
    # Step 3: Summarisation
    # ------------------------------------------------------------------ #

    def _summarise_memory(self, mem: Dict[str, Any]) -> Dict[str, Any]:
        raw     = mem["raw_text"]
        summary = self._simple_summary(raw)
        return {
            "id":        str(uuid.uuid4()),
            "summary":   summary,
            "source":    mem["agent"],
            "timestamp": mem["timestamp"],
            "tags":      self._extract_tags(summary),
            "hash":      self._compute_hash(summary),
        }

    def _simple_summary(self, text: str) -> str:
        """First sentence if meaningful, otherwise first 120 characters."""
        if "." in text:
            first = text.split(".")[0].strip()
            if len(first) > 20:
                return first
        return text[:120]

    def _extract_tags(self, text: str) -> List[str]:
        lower = text.lower()
        tags  = []
        for kw in ("market", "insight", "campaign", "copy", "analysis",
                   "deploy", "research", "audience", "competitor"):
            if kw in lower:
                tags.append(kw)
        return tags or ["general"]

    # ------------------------------------------------------------------ #
    # Step 4: Deduplication
    # ------------------------------------------------------------------ #

    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _dedupe(
        self,
        memories: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        seen: set  = set()
        result     = []
        for mem in memories:
            h = mem["hash"]
            if h not in seen:
                seen.add(h)
                result.append(mem)
        return result

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _stringify(self, output: Any) -> str:
        if isinstance(output, str):
            return output
        if isinstance(output, dict):
            return "; ".join(f"{k}: {v}" for k, v in output.items())
        return str(output)
