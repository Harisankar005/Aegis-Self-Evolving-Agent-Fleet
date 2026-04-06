"""
services/tools/__init__.py
==========================
Initialises the tools subsystem and provides clean import paths.

All tools follow the MCP handler convention:
    fn(args: dict, context: Any) -> dict

FIX LOG (v2):
- register_tool and get_tool are now real functions defined in mcp_gateway.py.
  In v1 they were imported here but did not exist in the module → ImportError
  at startup (and consequently on every agent invocation).
"""

from .mcp_gateway  import MCPRegistry, register_tool, get_tool
from .search_tool  import search_tool
from .http_tool    import http_tool, http_get

__all__ = [
    "MCPRegistry",
    "register_tool",
    "get_tool",
    "search_tool",
    "http_tool",
    "http_get",
]
