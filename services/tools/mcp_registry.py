# services/tools/mcp_registry.py
"""
MCP-style registry for agents and tools.

This module provides a thread-safe registry that stores agent/tool implementations
and metadata. Each registered entry must expose a `call(args: dict, session)` method
or be a callable with signature `fn(args: dict, session) -> dict`.

Usage:
    registry = MCPRegistry()
    registry.register("MyAgent", my_agent_instance, description="Does X")
    impl = registry.get("MyAgent")
    impl.call({"param": "value"}, session)
"""

from typing import Any, Callable, Dict, Iterable, List, Optional
import threading
import logging
import json
import inspect

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RegistryEntry:
    def __init__(self, name: str, impl: Any, description: str = "", metadata: Optional[Dict] = None):
        self.name = name
        self.impl = impl
        self.description = description or ""
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "callable": _is_callable(self.impl),
        }


def _is_callable(obj: Any) -> bool:
    """Return True if obj appears to be a valid callable for registry use."""
    if callable(obj):
        # Accept either a function/callable or an object with a .call method
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            # signature should accept (args, session) or a single args
            try:
                sig = inspect.signature(obj)
                params = list(sig.parameters.values())
                return len(params) >= 1
            except Exception:
                return True
        # object with .call method
        if hasattr(obj, "call") and callable(getattr(obj, "call")):
            return True
        return True
    return False


class MCPRegistry:
    """
    Thread-safe registry for agent/tool implementations.

    Methods:
        register(name, impl, description="", metadata=None)
        get(name)
        list()
        unregister(name)
        register_from_spec(spec_dict, impl)
        export_manifest() -> str
        import_manifest(manifest_str)
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._entries: Dict[str, RegistryEntry] = {}

    def register(self, name: str, impl: Any, description: str = "", metadata: Optional[Dict] = None) -> None:
        """
        Register an implementation under the given name.

        Args:
            name: Unique string identifier for the agent/tool.
            impl: Implementation object or callable. Should either be callable(fn) or have a .call method.
            description: Optional human-readable description.
            metadata: Optional dictionary for arbitrary metadata (version, author, schema, etc).

        Raises:
            ValueError: If name is empty or impl is not callable-like.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Registry name must be a non-empty string")

        if not _is_callable(impl):
            raise ValueError("Implementation must be callable or provide a callable .call method")

        with self._lock:
            entry = RegistryEntry(name=name, impl=impl, description=description, metadata=metadata)
            self._entries[name] = entry
            logger.debug("Registered '%s' in MCPRegistry", name)

    def get(self, name: str) -> Any:
        """
        Retrieve the implementation for a given name.

        Raises:
            KeyError: If the name is not found.
        """
        with self._lock:
            entry = self._entries.get(name)
            if entry is None:
                logger.error("Attempted to get unknown registry entry '%s'", name)
                raise KeyError(f"'{name}' not found in registry")
            return entry.impl

    def list(self) -> List[str]:
        """Return a sorted list of registered names."""
        with self._lock:
            return sorted(self._entries.keys())

    def unregister(self, name: str) -> None:
        """Remove a registry entry. Raises KeyError if not present."""
        with self._lock:
            if name not in self._entries:
                raise KeyError(f"'{name}' not found in registry")
            del self._entries[name]
            logger.debug("Unregistered '%s' from MCPRegistry", name)

    def register_from_spec(self, spec: Dict[str, Any], impl: Any) -> None:
        """
        Register an implementation from a spec dictionary.

        Spec example:
            {
                "name": "MyAgent",
                "description": "Does X",
                "metadata": {"version": "v1", "schema": {...}}
            }
        """
        name = spec.get("name")
        description = spec.get("description", "")
        metadata = spec.get("metadata", {})
        self.register(name=name, impl=impl, description=description, metadata=metadata)

    def export_manifest(self) -> str:
        """
        Export a JSON manifest describing the registry entries (without implementations).

        Returns:
            JSON string listing names, descriptions, and metadata.
        """
        with self._lock:
            manifest = {name: entry.to_dict() for name, entry in self._entries.items()}
            return json.dumps(manifest, indent=2, sort_keys=True)

    def import_manifest(self, manifest_str: str) -> List[str]:
        """
        Import a manifest (JSON string) describing entries to be present.
        Note: this does not register implementations; it only validates names/metadata.

        Returns:
            List of entry names parsed from manifest.
        """
        parsed = json.loads(manifest_str)
        if not isinstance(parsed, dict):
            raise ValueError("Manifest must be a JSON object mapping names to metadata")
        with self._lock:
            missing = []
            for name in parsed.keys():
                if name not in self._entries:
                    missing.append(name)
            return missing

    def get_entry_info(self, name: str) -> Dict[str, Any]:
        """Return metadata dictionary for a registry entry."""
        with self._lock:
            entry = self._entries.get(name)
            if entry is None:
                raise KeyError(f"'{name}' not found in registry")
            return entry.to_dict()
