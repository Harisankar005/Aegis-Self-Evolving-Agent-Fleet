"""
mcp_gateway.py
------------------------------------
A MCP-style Tool & Agent Registry used in the Aegis multi-agent system.

This component:
- Registers tools & agent-tools with schemas
- Validates inputs before tool execution
- Provides unified access for the orchestrator
- Supports agent-as-tool functionality (A2A)
- Emits structured metadata captured by traces/logging

FIX LOG (v2):
- register() signature now consistent everywhere: (name, description, schema, handler)
- register_agent() added as an explicit alias used by AgentCreator
- exists() method added (used by Router)
- "callable" key renamed to "handler" everywhere — orchestrator was looking up the
  wrong key and getting KeyError on every agent invocation
- _validate_args() now supports both type objects AND string-type descriptors so
  agents with {"query": "string"} schemas don't raise TypeError
- list_agents() added alongside list_tools() for symmetry
"""

from typing import Callable, Dict, Any
import uuid


class ToolValidationError(Exception):
    """Raised when arguments passed to a tool do not match its schema."""
    pass


# Map string type names → Python types for lightweight validation
_TYPE_MAP: Dict[str, type] = {
    "string": str,
    "str":    str,
    "int":    int,
    "integer": int,
    "float":  float,
    "number": float,
    "bool":   bool,
    "boolean": bool,
    "list":   list,
    "array":  list,
    "dict":   dict,
    "object": dict,
}


class MCPRegistry:
    """
    An MCP-style registry storing tools and agent-tools with schemas.

    All entries are stored under self.tools as:
        {
            "name":        str,
            "description": str,
            "schema":      dict,   # param_name → type or type-string
            "handler":     Callable
        }
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register(
        self,
        name: str,
        description: str,
        schema: Dict[str, Any],
        handler: Callable,
    ) -> Dict[str, Any]:
        """
        Register a tool or agent using MCP-style metadata.

        Args:
            name        : Unique string identifier.
            description : Human/LLM-readable description.
            schema      : Param schema {param_name: type or "type_string"}.
            handler     : The callable that implements the tool/agent.
        """
        self.tools[name] = {
            "name":        name,
            "description": description,
            "schema":      schema,
            "handler":     handler,
        }
        return self.tools[name]

    def register_agent(
        self,
        name: str,
        description: str,
        schema: Dict[str, Any],
        handler: Callable,
    ) -> Dict[str, Any]:
        """Alias for register() — used by AgentCreator for clarity."""
        return self.register(name, description, schema, handler)

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------
    def exists(self, name: str) -> bool:
        """Return True if the named tool/agent is registered."""
        return name in self.tools

    def get(self, name: str) -> Dict[str, Any]:
        """Return the full registry entry for *name*."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in MCP registry.")
        return self.tools[name]

    # ------------------------------------------------------------------
    # Schema validation
    # ------------------------------------------------------------------
    def _validate_args(self, schema: Dict[str, Any], args: Dict[str, Any]):
        """
        Validate *args* against *schema*.

        Schema values may be:
        - A Python type object (e.g. str, int)
        - A string type descriptor (e.g. "string", "int")
        - A dict with a "type" key (e.g. {"type": "string", "required": True})

        Only keys present in the schema are validated; extra keys are allowed
        so agents can pass rich context dicts without triggering errors.
        """
        for key, type_spec in schema.items():
            # Resolve the expected Python type
            if isinstance(type_spec, dict):
                required = type_spec.get("required", False)
                raw_type = type_spec.get("type", "string")
            else:
                required = False
                raw_type = type_spec

            if isinstance(raw_type, str):
                expected_type = _TYPE_MAP.get(raw_type.lower(), str)
            else:
                expected_type = raw_type  # already a Python type

            # Check presence
            if key not in args:
                if required:
                    raise ToolValidationError(
                        f"Missing required argument: '{key}'"
                    )
                continue  # optional — skip

            # Check type
            if not isinstance(args[key], expected_type):
                raise ToolValidationError(
                    f"Argument '{key}' expected {expected_type.__name__}, "
                    f"got {type(args[key]).__name__}"
                )

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------
    def call(
        self,
        name: str,
        args: Dict[str, Any],
        context: Any = None,
    ) -> Dict[str, Any]:
        """
        Execute a registered tool/agent-tool.

        Args:
            name    : Tool name.
            args    : Input arguments dict.
            context : Optional session / orchestrator context.

        Returns:
            dict — contains 'id', 'tool', 'args', 'result'.
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in MCP registry.")

        meta    = self.tools[name]
        handler = meta["handler"]
        schema  = meta["schema"]

        self._validate_args(schema, args)

        try:
            result = handler(args, context)
        except Exception as exc:
            raise RuntimeError(
                f"Tool '{name}' execution error: {exc}"
            ) from exc

        return {
            "id":     str(uuid.uuid4()),
            "tool":   name,
            "args":   args,
            "result": result,
        }

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return name → {description, schema} for all registered entries."""
        return {
            name: {
                "description": meta["description"],
                "schema":      meta["schema"],
            }
            for name, meta in self.tools.items()
        }

    # Alias kept for backward compat
    list_agents = list_tools


# ------------------------------------------------------------------
# Module-level convenience helpers (used by services/tools/__init__.py)
# ------------------------------------------------------------------
_default_registry = MCPRegistry()


def register_tool(
    name: str,
    description: str,
    schema: Dict[str, Any],
    handler: Callable,
) -> None:
    """Register a tool in the module-level default registry."""
    _default_registry.register(name, description, schema, handler)


def get_tool(name: str) -> Callable:
    """Retrieve the handler for *name* from the default registry."""
    return _default_registry.get(name)["handler"]
