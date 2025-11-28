"""
mcp_gateway.py
------------------------------------
A MCP-style Tool & Agent Registry used in the Aegis multi-agent system.

This component:
- Registers tools & agent-tools with schemas
- Validates inputs before tool execution
- Provides unified access for orchestrator
- Supports agent-as-tool functionality (A2A)
- Emits structured metadata that can be captured by traces/logging

This is a SAFE component (no external API keys stored).
"""

from typing import Callable, Dict, Any
import uuid


class ToolValidationError(Exception):
    """Raised when arguments passed to a tool do not match its schema."""
    pass


class MCPRegistry:
    """
    An MCP-style registry storing:
        - Tools
        - Agent-tools
        - Schemas (params, types)
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    # -------------------------------------------------------------
    # Register a new tool or agent-tool
    # -------------------------------------------------------------
    def register(
        self,
        name: str,
        description: str,
        schema: Dict[str, Any],
        handler: Callable
    ):
        """
        Register a tool/agent using MCP-style metadata.

        Args:
            name        : str - Unique name identifier
            description : str - Natural language description for LLMs
            schema      : dict - Input schema { param: type }
            handler     : callable - Function implementing the tool

        Example:
            registry.register(
                name="search_web",
                description="Perform web search and return results",
                schema={"query": str},
                handler=search_tool_fn
            )
        """

        self.tools[name] = {
            "name": name,
            "description": description,
            "schema": schema,
            "handler": handler
        }
        return self.tools[name]

    # -------------------------------------------------------------
    # Validate arguments based on schema
    # -------------------------------------------------------------
    def _validate_args(self, schema: Dict[str, Any], args: Dict[str, Any]):
        for key, typ in schema.items():
            if key not in args:
                raise ToolValidationError(f"Missing required argument: '{key}'")

            if not isinstance(args[key], typ):
                raise ToolValidationError(
                    f"Argument '{key}' expected {typ}, got {type(args[key])}"
                )

    # -------------------------------------------------------------
    # Invoke a tool by name
    # -------------------------------------------------------------
    def call(self, name: str, args: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Execute a registered tool/agent-tool.

        Args:
            name    : str - tool name
            args    : dict - validated args
            context : dict - session or orchestrator context

        Returns:
            dict - result of tool execution
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in MCP registry.")

        meta = self.tools[name]
        handler = meta["handler"]
        schema = meta["schema"]

        # Validate schema
        self._validate_args(schema, args)

        # Execute tool function safely
        try:
            result = handler(args, context)
        except Exception as e:
            # Wrap error for debugging and safety
            raise RuntimeError(f"Tool '{name}' execution error: {str(e)}")

        # Attach metadata
        return {
            "id": str(uuid.uuid4()),
            "tool": name,
            "args": args,
            "result": result
        }

    # -------------------------------------------------------------
    # Get tool metadata (useful for inspection or debugging)
    # -------------------------------------------------------------
    def get(self, name: str):
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found.")
        return self.tools[name]

    # -------------------------------------------------------------
    # Return full registry (useful for LLM context injection)
    # -------------------------------------------------------------
    def list_tools(self):
        return {
            name: {
                "description": meta["description"],
                "schema": meta["schema"]
            }
            for name, meta in self.tools.items()
        }
