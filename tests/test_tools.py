import pytest
from services.tools.mcp_gateway import MCPRegistry
from services.tools.search_tool import search_tool
from services.tools.http_tool import http_get

@pytest.fixture
def registry():
    return MCPRegistry()

def test_register_tool(registry):
    registry.register("search", search_tool)
    assert "search" in registry.tools

def test_tool_call(registry):
    registry.register("search", search_tool)
    out = registry.call("search", {"query": "hello world"})

    assert "results" in out
    assert isinstance(out["results"], list)

def test_http_tool():
    # Mocked http_tool returns a structured output
    out = http_get("https://example.com/api/test")
    assert "url" in out
    assert out["status"] in ("ok", "mocked")
