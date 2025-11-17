import pytest
from services.tools.mcp_gateway import MCPRegistry

def dummy_agent(args, ctx):
    return {"ok": True}

def test_register_and_retrieve():
    registry = MCPRegistry()
    registry.register({"name": "DummyAgent", "description": "test", "call": dummy_agent})
    
    tool = registry.get("DummyAgent")
    assert tool is not None
    assert tool.name == "DummyAgent"

def test_call_registered_agent():
    registry = MCPRegistry()
    registry.register({"name": "DummyAgent", "description": "test", "call": dummy_agent})
    
    tool = registry.get("DummyAgent")
    result = tool.call({"x": 1}, {})
    
    assert result == {"ok": True}
