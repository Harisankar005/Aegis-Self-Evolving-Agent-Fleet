import pytest
from services.memory.session_service import SessionService
from services.memory.memory_bank import MemoryBank

def test_session_creation():
    service = SessionService()
    s1 = service.get_or_create(None)
    s2 = service.get_or_create(s1.id)

    assert s1.id == s2.id
    assert isinstance(s1.events, list)

def test_session_add_event():
    service = SessionService()
    session = service.get_or_create(None)
    
    session.add_event("test_agent", {"value": 123})

    assert len(session.events) == 1
    assert session.events[0]["name"] == "test_agent"

def test_memory_bank_store_and_search():
    mb = MemoryBank()
    mb.store("smartwatch analysis", {"text": "Competitors: Apple, Samsung"})
    
    results = mb.search("smartwatch")
    assert len(results) >= 1
    assert "Competitors" in results[0]["data"]["text"]
