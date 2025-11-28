"""
memory_consolidation.py
-----------------------

This module performs **memory consolidation** for the Aegis agent system.

It extracts relevant signals from:
- Agent outputs
- Trace logs
- Conversation/session context

Then it:
1. Scores relevance
2. Summarizes raw memory chunks
3. Deduplicates similar memories
4. Ensures provenance tracking
5. Returns a clean list of consolidated memories ready for the MemoryBank

This version is fully API-key-free and runs locally.  
You can later extend:
- LLM summarization → Gemini
- Embeddings → vector DB
- Relevance scoring → semantic similarity
"""

import time
import uuid
import hashlib


class MemoryConsolidation:
    """
    Consolidates session data into long-term memory entries.

    Expected input format:
    ----------------------
    session_events = [
        {
            "agent": "MarketResearchAgent",
            "output": {"insights": "...", "confidence": 0.85},
            "timestamp": 1731200301.24
        },
        ...
    ]

    Output format:
    --------------
    [
        {
            "id": "...",
            "summary": "...",
            "source": "MarketResearchAgent",
            "timestamp": 1731200301.24,
            "tags": ["research", "campaign"],
            "hash": "sha256 memory signature"
        }
    ]
    """

    def __init__(self, relevance_threshold=0.2):
        self.relevance_threshold = relevance_threshold

    # -----------------------------------------------------
    # Main API
    # -----------------------------------------------------

    def consolidate(self, session_events):
        """
        Main entry point:
        1) Extract raw memory candidates
        2) Score their relevance
        3) Summarize them
        4) Deduplicate using hashes
        """
        raw_memories = self._extract_raw_memories(session_events)
        filtered = [m for m in raw_memories if m["relevance"] >= self.relevance_threshold]
        summarized = [self._summarize_memory(m) for m in filtered]
        deduped = self._dedupe(summarized)
        return deduped

    # -----------------------------------------------------
    # Step 1: Extract raw memories
    # -----------------------------------------------------

    def _extract_raw_memories(self, events):
        """
        Convert session events into raw memory fragments.
        """
        memories = []
        for evt in events:
            agent = evt.get("agent")
            output = evt.get("output", {})
            ts = evt.get("timestamp", time.time())

            # Convert agent output to raw textual memory
            text_block = self._stringify_output(output)

            relevance = self._estimate_relevance(text_block)

            memories.append({
                "agent": agent,
                "raw_text": text_block,
                "timestamp": ts,
                "relevance": relevance,
            })
        return memories

    # -----------------------------------------------------
    # Step 2: Relevance scoring (simple heuristic)
    # -----------------------------------------------------

    def _estimate_relevance(self, text):
        """
        Simple relevance scoring:
        - Longer text → higher relevance
        - Real version would use an LLM evaluator or embeddings
        """
        if not text:
            return 0.0

        length = len(text)
        # Normalize score between 0 and 1
        score = min(length / 200.0, 1.0)
        return round(score, 3)

    # -----------------------------------------------------
    # Step 3: Summarization (mock/heuristic)
    # -----------------------------------------------------

    def _summarize_memory(self, mem):
        """
        Produce a short summary.
        In production, replace with a real LLM summarizer.
        """
        raw = mem["raw_text"]

        summary = self._simple_summary(raw)

        return {
            "id": str(uuid.uuid4()),
            "summary": summary,
            "source": mem["agent"],
            "timestamp": mem["timestamp"],
            "tags": self._extract_tags(summary),
            "hash": self._compute_hash(summary)
        }

    def _simple_summary(self, text):
        """
        Simple heuristic:
        - Take first sentence or first 120 characters
        """
        if "." in text:
            first_sentence = text.split(".")[0].strip()
            if len(first_sentence) > 20:
                return first_sentence
        return text[:120]

    def _extract_tags(self, text):
        """
        Simple keyword extraction—mocked.
        A real version uses embeddings or LLM extraction.
        """
        tags = []
        lowered = text.lower()

        if "market" in lowered:
            tags.append("market")
        if "insight" in lowered:
            tags.append("insight")
        if "campaign" in lowered:
            tags.append("campaign")
        if "copy" in lowered:
            tags.append("copy")
        if "analysis" in lowered:
            tags.append("analysis")

        return tags or ["general"]

    # -----------------------------------------------------
    # Step 4: Deduplication
    # -----------------------------------------------------

    def _compute_hash(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _dedupe(self, memories):
        """
        Remove duplicates using the hash of the summary.
        """
        seen = set()
        deduped = []

        for mem in memories:
            h = mem["hash"]
            if h not in seen:
                seen.add(h)
                deduped.append(mem)

        return deduped

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _stringify_output(self, output):
        """
        Flatten agent output dictionaries into a text block.
        """
        if isinstance(output, str):
            return output

        if isinstance(output, dict):
            parts = []
            for k, v in output.items():
                parts.append(f"{k}: {v}")
            return "; ".join(parts)

        return str(output)
