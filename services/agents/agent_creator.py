"""
agent_creator.py
----------------
A meta-agent that generates new agent specifications when the evaluation
pipeline detects missing capabilities.

Supports:
- Agent spec generation (schema + metadata)
- Python callable construction
- Registration into the MCP gateway
- Optional LLM-based spec generation (stub)

FIX LOG (v2):
- generate_new_agent(capability: str) now takes a string, not a dict.
  In v1 it accepted judge_feedback: dict and called .get("notes", "") on it,
  but the orchestrator was passing a plain string → AttributeError.
- Uses self.registry.register_agent() which now exists in MCPRegistry (v2).
  In v1 register_agent() did not exist → AttributeError on every self-evolution.
- detect_missing_capabilities() is removed — capability detection is the Judge's
  responsibility (suggest_missing_capability). AgentCreator only builds.
- save_spec_to_file() kept but made optional (does not crash if path is read-only).
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

try:
    from rich import print as rprint
except ImportError:
    rprint = print  # graceful fallback when rich is not installed


class AgentCreator:
    """
    AgentCreator dynamically generates and registers new agents.

    It produces:
    - Agent name and description
    - JSON input/output schemas (MCP-compatible)
    - A Python callable implementing the new agent
    - Registration in the MCP tool registry

    Parameters
    ----------
    registry   : MCPRegistry instance — the live registry to register into.
    llm_client : Optional LLM client for future spec generation via Gemini.
    """

    def __init__(self, registry, llm_client=None):
        self.registry = registry
        self.llm      = llm_client

    # ------------------------------------------------------------------ #
    # 1. Agent Spec Generation
    # ------------------------------------------------------------------ #

    def generate_agent_spec(self, capability: str) -> Dict[str, Any]:
        """
        Create a new agent specification from a capability label string.

        In production this would call an LLM; here it uses deterministic
        templates so the project remains API-key-free and fully runnable.

        Parameters
        ----------
        capability : str
            Short capability label, e.g. "analytics", "monitoring".

        Returns
        -------
        dict — full agent specification.
        """
        agent_name = f"{capability.replace('-', '_').capitalize()}Agent"
        unique_id  = uuid.uuid4().hex[:6]

        spec: Dict[str, Any] = {
            "id":          f"{agent_name}-{unique_id}",
            "name":        agent_name,
            "description": f"Auto-generated agent for {capability} tasks.",
            "capability":  capability,
            "created_at":  datetime.now(timezone.utc).isoformat(),
            "input_schema": {
                "type": "object",
                "properties": {
                    "input": {
                        "type":        "string",
                        "description": f"Input data for {agent_name}",
                    }
                },
                "required": ["input"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {
                        "type":        "string",
                        "description": f"Output produced by {agent_name}",
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
            },
            "examples": {
                "input":  {"input": f"Run {capability} on campaign metrics"},
                "output": {"result": f"Mock {capability} insights", "confidence": 0.92},
            },
        }
        return spec

    # ------------------------------------------------------------------ #
    # 2. Python Implementation Builder
    # ------------------------------------------------------------------ #

    def build_python_implementation(self, capability: str) -> Callable:
        """
        Return a Python callable that implements the new agent.

        The function signature matches the MCP handler convention:
            fn(args: dict, context: Any) -> dict

        Parameters
        ----------
        capability : str
            Capability label used to personalise the mock response.
        """

        def dynamic_agent_fn(args: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
            text = args.get("input", args.get("query", args.get("brief", "")))
            return {
                "result":     f"[Auto-generated {capability} analysis] Processed: '{text}'",
                "confidence": 0.92,
                "agent":      f"{capability.capitalize()}Agent",
            }

        # Give the function a recognisable __name__ for logging
        dynamic_agent_fn.__name__ = f"{capability}_agent_fn"
        return dynamic_agent_fn

    # ------------------------------------------------------------------ #
    # 3. Full Pipeline: CAPABILITY → SPEC → IMPL → REGISTER
    # ------------------------------------------------------------------ #

    def generate_new_agent(self, capability: str) -> Dict[str, Any]:
        """
        End-to-end agent creation invoked by the orchestrator.

        Parameters
        ----------
        capability : str
            Short capability label (e.g. "analytics") produced by
            Judge.suggest_missing_capability().

        Returns
        -------
        dict — the full agent spec that was registered.
        """
        rprint(f"[yellow]AgentCreator:[/] building agent for capability '{capability}'")

        spec  = self.generate_agent_spec(capability)
        impl  = self.build_python_implementation(capability)

        # Register in the MCP registry with a lean schema
        self.registry.register_agent(
            name=spec["name"],
            description=spec["description"],
            schema={"input": str},   # simple schema for auto-agents
            handler=impl,
        )

        rprint(f"[green]Registered new agent:[/] {spec['name']} ({spec['id']})")
        return spec

    # ------------------------------------------------------------------ #
    # 4. Optional: Export Spec to Disk
    # ------------------------------------------------------------------ #

    def save_spec_to_file(self, spec: Dict[str, Any], path: str) -> bool:
        """
        Persist the generated agent spec to a JSON file on disk.

        Returns True on success, False if the write fails (e.g. read-only fs).
        """
        try:
            with open(path, "w") as fh:
                json.dump(spec, fh, indent=4)
            rprint(f"[blue]Saved agent spec →[/] {path}")
            return True
        except OSError as exc:
            rprint(f"[red]Could not save spec to {path}:[/] {exc}")
            return False
