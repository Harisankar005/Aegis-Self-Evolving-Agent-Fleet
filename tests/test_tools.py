"""
tests/test_tools.py
-------------------
Unit tests for the MCP tool registry, SearchTool, and HttpTool.

Tests verify:
- MCPRegistry.register(), exists(), get(), call().
- SearchTool returns results list.
- HttpTool returns structured output with correct status keys.

FIX LOG (v2):
- registry.register() called with the correct 4-arg signature:
  (name, description, schema, handler). v1 called register("search", search_tool)
  with only 2 args → TypeError.
- search_tool imported as a module-level function (exists in v2); v1 had only
  the SearchTool class → NameError when used as a callable.
- http_get imported directly from services.tools.http_tool (added in v2);
  v1 had no http_get function → ImportError.
- Assertions updated: http_get output has "status" and "url" keys (not "status_code"
  at top level and not an "ok" literal — it's "mocked" in mock mode).
- Schema validation test added for ToolValidationError.
"""

import pytest

from services.tools.mcp_gateway import MCPRegistry, ToolValidationError
from services.tools.search_tool  import search_tool
from services.tools.http_tool    import http_get, http_tool


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def registry():
    return MCPRegistry()


@pytest.fixture
def registry_with_search(registry):
    """Registry pre-loaded with a search tool entry."""
    registry.register(
        name="search",
        description="A mock search tool.",
        schema={"query": str},
        handler=search_tool,
    )
    return registry


# ─── MCPRegistry ──────────────────────────────────────────────────────────────

class TestMCPRegistry:

    def test_register_tool(self, registry):
        registry.register("search", "Search tool.", {"query": str}, search_tool)
        assert "search" in registry.tools

    def test_exists_true(self, registry):
        registry.register("search", "Search.", {"query": str}, search_tool)
        assert registry.exists("search") is True

    def test_exists_false(self, registry):
        assert registry.exists("nonexistent") is False

    def test_get_returns_entry(self, registry_with_search):
        entry = registry_with_search.get("search")
        assert entry["name"]    == "search"
        assert "handler"        in entry
        assert "schema"         in entry
        assert "description"    in entry

    def test_get_unknown_raises(self, registry):
        with pytest.raises(ValueError, match="not found"):
            registry.get("ghost_tool")

    def test_call_returns_structured_output(self, registry_with_search):
        result = registry_with_search.call("search", {"query": "hello world"})
        assert "result" in result
        assert "tool"   in result
        assert result["tool"] == "search"

    def test_call_unknown_tool_raises(self, registry):
        with pytest.raises(ValueError, match="not found"):
            registry.call("ghost_tool", {})

    def test_call_validates_schema_missing_key(self, registry):
        def strict_fn(args, ctx=None):
            return {}

        registry.register(
            "strict",
            "Needs required arg.",
            {"required_key": {"type": "string", "required": True}},
            strict_fn,
        )
        with pytest.raises(ToolValidationError, match="Missing required argument"):
            registry.call("strict", {})

    def test_list_tools(self, registry_with_search):
        tools = registry_with_search.list_tools()
        assert "search" in tools
        assert "description" in tools["search"]

    def test_register_agent_alias(self, registry):
        registry.register_agent("agent_a", "Agent A.", {}, lambda a, c: {})
        assert registry.exists("agent_a")


# ─── SearchTool ───────────────────────────────────────────────────────────────

class TestSearchTool:

    def test_returns_results_key(self):
        out = search_tool({"query": "hello world"})
        assert "results" in out

    def test_results_is_list(self):
        out = search_tool({"query": "AI trends"})
        assert isinstance(out["results"], list)

    def test_results_not_empty(self):
        out = search_tool({"query": "anything"})
        assert len(out["results"]) > 0

    def test_each_result_has_title(self):
        out = search_tool({"query": "test"})
        for r in out["results"]:
            assert "title" in r

    def test_max_results_respected(self):
        out = search_tool({"query": "test", "max_results": 2})
        assert len(out["results"]) <= 2

    def test_missing_query_raises(self):
        with pytest.raises(ValueError, match="Missing required field"):
            search_tool({})

    def test_callable_from_registry(self):
        reg = MCPRegistry()
        reg.register("search", "Search.", {"query": str}, search_tool)
        out = reg.call("search", {"query": "hello world"})
        assert "results" in out["result"]


# ─── HttpTool ─────────────────────────────────────────────────────────────────

class TestHttpTool:

    def test_http_get_returns_dict(self):
        out = http_get("https://example.com/ping")
        assert isinstance(out, dict)

    def test_http_get_has_url_field(self):
        out = http_get("https://example.com/ping")
        assert "url" in out

    def test_http_get_has_status_field(self):
        out = http_get("https://example.com/ping")
        assert "status" in out
        assert out["status"] in ("ok", "mocked", "blocked", "error")

    def test_http_get_allowed_domain(self):
        out = http_get("https://example.com/ping")
        assert out["status"] != "blocked"

    def test_http_get_blocked_domain(self):
        out = http_get("https://evil-site.example.org/api")
        assert out["status"] == "blocked"

    def test_http_tool_callable_with_args(self):
        out = http_tool({"method": "GET", "url": "https://example.com/ping"})
        assert "status" in out

    def test_http_tool_missing_url_returns_error(self):
        out = http_tool({"method": "GET"})
        assert out["status"] == "error"
        assert "error" in out
