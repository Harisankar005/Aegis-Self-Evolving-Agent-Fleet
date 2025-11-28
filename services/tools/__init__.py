"""
services.tools
==============

This package contains all tool-related modules used by the Aegis agent system.

Tools follow a Model Context Protocol (MCP)-style interface. They expose
functionality (e.g., search, HTTP requests, data retrieval) that agents can call
in a structured and validated way.

This __init__.py file:
- Initializes the MCP tool registry
- Provides convenient import paths
- Exposes helper methods for registering and retrieving tools
- Ensures tools are discoverable by the orchestrator and by AgentCreator

Modules included:
- mcp_gateway.py: Core MCP-style tool registry and schema validation
- search_tool.py: Example custom search tool
- http_tool.py: Example HTTP GET/POST wrapper tool

Usage Example:
--------------
from services.tools import register_tool, get_tool

register_tool("SearchTool", search_function)
tool = get_tool("SearchTool")
result = tool({"query": "AI agents"})
"""

from .mcp_gateway import MCPRegistry, register_tool, get_tool
from .search_tool import search_tool
from .http_tool import http_tool

__all__ = [
    "MCPRegistry",
    "register_tool",
    "get_tool",
    "search_tool",
    "http_tool",
]
