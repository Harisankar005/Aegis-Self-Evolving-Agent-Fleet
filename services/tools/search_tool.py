"""
search_tool.py
--------------
MCP-style Search Tool for Aegis agents.

Agents call this tool to retrieve external information.

MCP handler signature:
    search_tool(args: dict, context: Any) -> dict

Features:
✔ MCP-compatible schema
✔ Strict argument validation
✔ Mock search results (no API key needed)
✔ Optional real search integration (commented stub)

FIX LOG (v2):
- Module-level search_tool() function added — __init__.py imported
  "search_tool" expecting a callable, but v1 only exported the SearchTool class.
- register_search_tool() fixed: used "callable=" kwarg which is not a parameter
  of MCPRegistry.register() → TypeError. Changed to "handler=".
- run() now also accepts context arg (ignored) to match MCP handler convention.
"""

import time
from typing import Any, Dict, List


class SearchTool:
    """
    General-purpose Search tool following MCP conventions.

    Schema:
        { "query": str, "max_results": int (optional, default 3) }
    """

    NAME        = "SearchTool"
    DESCRIPTION = (
        "Retrieves information from a (mocked) search engine. "
        "Useful for market insights, competitive analysis, trending topics."
    )
    SCHEMA: Dict[str, Any] = {
        "query":       {"type": "string", "required": True},
        "max_results": {"type": "int",    "required": False, "default": 3},
    }

    def __init__(self, mode: str = "mock"):
        self.mode = mode

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    def _validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        validated: Dict[str, Any] = {}
        for key, rule in self.SCHEMA.items():
            if isinstance(rule, dict):
                required = rule.get("required", False)
                default  = rule.get("default")
            else:
                required = False
                default  = None

            if required and key not in args:
                raise ValueError(f"[SearchTool] Missing required field: '{key}'")
            validated[key] = args.get(key, default)
        return validated

    # ------------------------------------------------------------------ #
    # Mock search
    # ------------------------------------------------------------------ #

    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        time.sleep(0.05)  # simulate minimal latency
        return [
            {
                "title":   f"Result #{i + 1}: {query}",
                "snippet": f"Mocked snippet about '{query}' — result {i + 1}.",
                "source":  "MockSearchEngine",
                "rank":    i + 1,
            }
            for i in range(max_results)
        ]

    # ------------------------------------------------------------------ #
    # Main execution
    # ------------------------------------------------------------------ #

    def run(
        self,
        args:    Dict[str, Any],
        context: Any = None,
    ) -> Dict[str, Any]:
        """
        Execute the search.

        Parameters
        ----------
        args    : dict — must include "query"; optionally "max_results".
        context : Any — ignored (kept for MCP handler signature compatibility).
        """
        validated   = self._validate_args(args)
        query       = validated["query"]
        max_results = validated["max_results"] or 3

        if self.mode == "real":
            raise NotImplementedError(
                "Real search mode is not enabled. Use mock mode for demos."
            )

        results = self._mock_search(query, max_results)
        return {
            "tool":    self.NAME,
            "query":   query,
            "results": results,
            "mode":    self.mode,
        }


# ─── Module-level singleton + public callable ─────────────────────────────────

_search_instance = SearchTool(mode="mock")


def search_tool(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """
    Primary MCP handler for SearchTool.

    Parameters
    ----------
    args    : dict — {"query": "...", "max_results": int (optional)}.
    context : Any — session state (ignored by this tool).
    """
    return _search_instance.run(args, context)


# ─── Registry helper ──────────────────────────────────────────────────────────

def register_search_tool(registry, mode: str = "mock") -> SearchTool:
    """
    Register SearchTool in an MCPRegistry instance.

    Parameters
    ----------
    registry : MCPRegistry
    mode     : "mock" (default) or "real"
    """
    tool = SearchTool(mode=mode)
    registry.register(
        name=SearchTool.NAME,
        description=SearchTool.DESCRIPTION,
        schema={"query": str, "max_results": int},
        handler=tool.run,   # FIX: was "callable=" → KeyError in registry
    )
    return tool
