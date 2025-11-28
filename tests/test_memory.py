import pytest
from services.memory.session_service import SessionService
from services.memory.memory_bank import MemoryBank

def test_session_creation():
    ss = SessionService()
    session = ss.get_or_create()
    assert session.id is not None
    assert isinstance(session.events, list)

def test_session_event_append():
    ss = SessionService()
    session = ss.get_or_create()
    session.append_event("TestAgent", {"data": 123})

    assert len(session.events) == 1
    assert session.events[0]["agent"] == "TestAgent"

def test_memory_bank_write_read():
    mb = MemoryBank()
    mb.store("user_pref", "product_interest", "AI agents are cool")

    memories = mb.retrieve("user_pref")
    assert len(memories) >= 1

    latest = memories[-1]
    assert latest["value"] == "AI agents are cool"

def test_memory_provenance():
    mb = MemoryBank()
    mb.store("mission", "campaign_insight", "Students prefer low-budget plans")

    memories = mb.retrieve("mission")
    last_item = memories[-1]

    assert "timestamp" in last_item
    assert "key" in last_item
    assert last_item["key"] == "campaign_insight"
