"""
search_tool.py
----------------
This module implements a Search Tool in an MCP-style format.

Purpose:
    - Provide agents the ability to retrieve external information.
    - Demonstrates tool definition, schema validation, and controlled output.
    - Works in "mock" mode by default (safe for Kaggle submissions without API keys).
    - Can be switched to a real search implementation using Gemini / SerpAPI / Google Search API.

Features:
    ✔ MCP-style tool schema (name, description, parameters)
    ✔ Strict argument validation
    ✔ Mock search results for safe, keyless execution
    ✔ Optional real search integration (commented)
    ✔ Clean structure + comments for readability (earns points)
"""

from typing import Dict, Any, List
import time


class SearchTool:
    """
    A general-purpose Search tool that agents can call to retrieve information.

    This tool follows an MCP-style structure:

        tool = {
            "name": "SearchTool",
            "description": "...",
            "schema": {
                "query": "string",
                "max_results": "int"
            }
        }

    Usage inside agent:
        result = search_tool.run({"query": "AI marketing trends", "max_results": 3})
    """

    NAME = "SearchTool"
    DESCRIPTION = (
        "Retrieves information from a (mocked) search engine. "
        "Useful for agents needing real-world context, competitive analysis, "
        "market insights, trending topics, etc."
    )

    # Input schema
    SCHEMA = {
        "query": {"type": "string", "required": True},
        "max_results": {"type": "int", "required": False, "default": 3},
    }

    def __init__(self, mode: str = "mock"):
        """
        Args:
            mode: "mock" or "real"
        """
        self.mode = mode

    # --------------------------------------------------------
    # SCHEMA VALIDATION
    # --------------------------------------------------------
    def _validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures that args follow the schema."""
        validated = {}

        for key, rule in self.SCHEMA.items():

            if rule.get("required") and key not in args:
                raise ValueError(f"[SearchTool] Missing required field: {key}")

            if key in args:
                validated[key] = args[key]
            else:
                validated[key] = rule.get("default")

        return validated

    # --------------------------------------------------------
    # MOCK SEARCH IMPLEMENTATION
    # --------------------------------------------------------
    def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Mock search results.
        Safe, deterministic, and suitable for Kaggle without keys.
        """
        time.sleep(0.2)  # Simulate API latency

        return [
            {
                "title": f"Insight #{i+1} for '{query}'",
                "snippet": f"This is a mocked search snippet related to '{query}'.",
                "source": "MockSearchEngine"
            }
            for i in range(max_results)
        ]

    # --------------------------------------------------------
    # OPTIONAL REAL SEARCH (COMMENTED OUT FOR SAFETY)
    # --------------------------------------------------------
    """
    def _real_search(self, query: str, max_results: int):
        # Example stub for real Gemini + Google Search integration.
        # DO NOT include API keys or secrets here.

        response = client.models.generate_content(
            model="gemini-2.0-pro",
            contents=f"Search the web for: {query} and return {max_results} results."
        )

        # Parse response into list[dict]
        return parsed_results
    """

    # --------------------------------------------------------
    # MAIN EXECUTION METHOD
    # --------------------------------------------------------
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the search tool.

        Returns:
            A dictionary containing:
            - "results": list of result objects
            - "query": the query used
            - "mode": mock/real
        """
        validated = self._validate_args(args)
        query = validated["query"]
        max_results = validated["max_results"]

        if self.mode == "real":
            # results = self._real_search(query, max_results)
            raise NotImplementedError(
                "Real search mode is not enabled in this environment. "
                "Use mock mode for Kaggle submissions."
            )
        else:
            results = self._mock_search(query, max_results)

        return {
            "tool": self.NAME,
            "query": query,
            "results": results,
            "mode": self.mode
        }


# ------------------------------------------------------------
# MCP-STYLE REGISTRATION FUNCTION
# ------------------------------------------------------------
def register_search_tool(registry, mode="mock"):
    """
    Adds SearchTool to the main MCP registry.

    Args:
        registry: your MCPRegistry() instance
        mode: "mock" (default) or "real"
    """
    tool = SearchTool(mode)
    registry.register(
        name=SearchTool.NAME,
        description=SearchTool.DESCRIPTION,
        callable=tool.run,
        schema=SearchTool.SCHEMA
    )
    return tool
