"""
tests/test_memory.py
--------------------
Unit tests for the session and long-term memory subsystems.

Tests verify:
- Session creation, state management, trace events.
- MemoryBank store/retrieve round-trips.
- Memory provenance fields (timestamp, key, namespace).
- Memory consolidation and deduplication.

FIX LOG (v2):
- session.events entries are now plain dicts (not SessionEvent objects) so
  subscript access like events[0]["role"] works directly.
- MemoryBank.store()/retrieve() API used — v1 tests called mb.store() and
  mb.retrieve("namespace") but only add_memory() existed → AttributeError.
- test_memory_provenance checks "key" and "timestamp" which are now guaranteed
  fields in every stored item's to_dict() output.
- Added Session.trace_event() tests since the method was missing in v1.
"""

import pytest

from services.memory.session_service      import SessionService, Session
from services.memory.memory_bank          import MemoryBank
from services.memory.memory_consolidation import MemoryConsolidation


# ─── SessionService ───────────────────────────────────────────────────────────

class TestSessionService:

    def test_create_session(self):
        ss      = SessionService()
        session = ss.create_session()
        assert session.id is not None
        assert isinstance(session.events, list)
        assert len(session.events) == 0

    def test_get_or_create_new(self):
        ss      = SessionService()
        session = ss.get_or_create()
        assert session.id is not None

    def test_get_or_create_existing(self):
        ss       = SessionService()
        original = ss.create_session()
        retrieved = ss.get_or_create(original.id)
        assert retrieved.id == original.id

    def test_session_event_append(self):
        ss      = SessionService()
        session = ss.get_or_create()
        session.append_event("TestAgent", {"data": 123})

        assert len(session.events) == 1
        event = session.events[0]
        # Events are stored as plain dicts — no object unpacking needed
        assert event["role"]    == "TestAgent"
        assert event["content"] == {"data": 123}

    def test_session_state_set_get(self):
        ss      = SessionService()
        session = ss.get_or_create()
        session.set_state("key1", "value1")
        assert session.get_state("key1") == "value1"
        assert session.get_state("missing", "default") == "default"

    def test_session_state_update(self):
        ss      = SessionService()
        session = ss.get_or_create()
        session.update_state({"a": 1, "b": 2})
        assert session.state["a"] == 1
        assert session.state["b"] == 2


class TestSessionTrace:
    """Trace events are used by the Judge — critical to test."""

    def test_trace_event_appended(self):
        session = Session()
        session.trace_event("Mission started", {"mission": "test"})
        assert len(session.trace) == 1

    def test_trace_event_has_name(self):
        session = Session()
        session.trace_event("Calling agent: CopyAgent", {})
        span = session.trace[0]
        assert span["name"] == "Calling agent: CopyAgent"

    def test_trace_event_has_timestamp(self):
        session = Session()
        session.trace_event("step", {})
        assert "timestamp" in session.trace[0]

    def test_trace_accumulates(self):
        session = Session()
        for i in range(5):
            session.trace_event(f"event_{i}", {})
        assert len(session.trace) == 5

    def test_trace_property_returns_list(self):
        session = Session()
        assert isinstance(session.trace, list)


# ─── MemoryBank ───────────────────────────────────────────────────────────────

class TestMemoryBank:

    def test_store_and_retrieve_by_namespace(self):
        mb = MemoryBank()
        mb.store("user_pref", "product_interest", "AI agents are cool")

        memories = mb.retrieve("user_pref")
        assert len(memories) >= 1
        values = [m["value"] for m in memories]
        assert "AI agents are cool" in values

    def test_retrieve_latest_value(self):
        mb = MemoryBank()
        mb.store("user_pref", "product_interest", "AI agents are cool")
        latest = mb.retrieve("user_pref")[-1]
        assert latest["value"] == "AI agents are cool"

    def test_memory_provenance(self):
        mb = MemoryBank()
        mb.store("mission", "campaign_insight", "Students prefer low-budget plans")

        memories  = mb.retrieve("mission")
        last_item = memories[-1]
        assert "timestamp" in last_item
        assert "key"       in last_item
        assert last_item["key"] == "campaign_insight"

    def test_namespace_isolation(self):
        mb = MemoryBank()
        mb.store("ns_a", "k1", "value in A")
        mb.store("ns_b", "k2", "value in B")

        ns_a = mb.retrieve("ns_a")
        assert all(m["namespace"] == "ns_a" for m in ns_a)

    def test_full_text_retrieval(self):
        mb = MemoryBank()
        mb.store("facts", "market", "AI market is growing fast", importance=0.8)
        mb.store("facts", "other",  "Unrelated fact about fish",  importance=0.2)

        results = mb.retrieve("AI market growing", top_k=1)
        assert len(results) == 1
        assert "AI market" in results[0]["content"]

    def test_add_memory_low_level(self):
        mb = MemoryBank()
        item = mb.add_memory(
            content="Research finding",
            memory_type="fact",
            importance=0.7,
            agent="MarketResearchAgent",
            session_id="sess-1",
        )
        assert item.content    == "Research finding"
        assert item.importance == 0.7

    def test_clear(self):
        mb = MemoryBank()
        mb.store("ns", "k", "v")
        mb.clear()
        assert len(mb) == 0

    def test_consolidate_memories(self):
        mb = MemoryBank()
        mb.add_memory("Important insight A", "fact", 0.8, "AgentA", "sess-x")
        mb.add_memory("Important insight B", "fact", 0.9, "AgentB", "sess-x")

        summary = mb.consolidate_memories("sess-x")
        assert "summary" in summary
        assert "sess-x"  in summary["summary"]

    def test_consolidate_empty_session(self):
        mb      = MemoryBank()
        summary = mb.consolidate_memories("nonexistent-session")
        assert summary == {}


# ─── MemoryConsolidation ──────────────────────────────────────────────────────

class TestMemoryConsolidation:

    def test_consolidate_returns_list(self):
        mc     = MemoryConsolidation()
        events = [{"agent": "CopyAgent", "output": {"copy": "Great headline!"}}]
        result = mc.consolidate(events)
        assert isinstance(result, list)

    def test_deduplication_removes_exact_duplicates(self):
        mc     = MemoryConsolidation()
        events = [
            {"agent": "A", "output": "identical text here for testing"},
            {"agent": "B", "output": "identical text here for testing"},
        ]
        result = mc.consolidate(events)
        assert len(result) == 1

    def test_summary_fields_present(self):
        mc     = MemoryConsolidation()
        events = [{"agent": "MarketResearchAgent",
                   "output": "Market insight about competitive landscape."}]
        result = mc.consolidate(events)
        if result:
            item = result[0]
            assert "id"        in item
            assert "summary"   in item
            assert "source"    in item
            assert "tags"      in item
            assert "hash"      in item
            assert "timestamp" in item

    def test_low_relevance_filtered_out(self):
        mc     = MemoryConsolidation(relevance_threshold=0.9)
        events = [{"agent": "A", "output": "hi"}]  # very short → low relevance
        result = mc.consolidate(events)
        assert result == []
