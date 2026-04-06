"""
router.py
---------
The Router resolves which agent/tool should handle each plan step.

It maps:
    plan step → agent name → MCPRegistry entry → callable handler

FIX LOG (v2):
- router.resolve_agent() calls registry.exists() which now exists in
  MCPRegistry (v2). In v1 exists() was absent → AttributeError.
- route_step() added as a higher-level convenience used by the Orchestrator
  when it wants the Router to fully resolve and invoke a step in one call.
- Fallback routing logs a warning rather than silently returning None, making
  debugging easier in multi-agent runs.
"""

import warnings
from typing import Any, Callable, Dict, List, Optional


class Router:
    """
    Resolves and optionally invokes agents for plan steps.

    Parameters
    ----------
    registry : MCPRegistry-compatible object.
               Must implement: get(name), exists(name), list_tools().
    """

    def __init__(self, registry):
        self.registry = registry

    # ------------------------------------------------------------------ #
    # 1. Resolve a single agent by name
    # ------------------------------------------------------------------ #

    def resolve_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Look up *agent_name* in the registry.

        Returns the registry entry dict on success, or None if not found.
        """
        if self.registry.exists(agent_name):
            return self.registry.get(agent_name)
        warnings.warn(
            f"[Router] Agent '{agent_name}' not found in registry. "
            "Falling back to None.",
            stacklevel=2,
        )
        return None

    # ------------------------------------------------------------------ #
    # 2. Resolve from a plan step dict
    # ------------------------------------------------------------------ #

    def resolve_step(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve the agent for a plan step dict.

        Parameters
        ----------
        step : dict — {"step": str, "agent": str, "args": dict}
        """
        agent_name = step.get("agent", "")
        return self.resolve_agent(agent_name)

    # ------------------------------------------------------------------ #
    # 3. Automatic fallback routing
    # ------------------------------------------------------------------ #

    def resolve_with_fallback(
        self,
        agent_name:    str,
        fallback_name: str = "MarketResearchAgent",
    ) -> Dict[str, Any]:
        """
        Resolve *agent_name*, falling back to *fallback_name* if absent.

        Useful during self-evolution: if a newly planned agent hasn't been
        registered yet, the orchestrator can degrade gracefully.
        """
        entry = self.resolve_agent(agent_name)
        if entry is not None:
            return entry

        warnings.warn(
            f"[Router] Falling back from '{agent_name}' to '{fallback_name}'.",
            stacklevel=2,
        )
        return self.registry.get(fallback_name)

    # ------------------------------------------------------------------ #
    # 4. Route and invoke in one call
    # ------------------------------------------------------------------ #

    def route_step(
        self,
        step:    Dict[str, Any],
        context: Any = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve the agent for *step* and immediately invoke it.

        Parameters
        ----------
        step    : dict — {"step": str, "agent": str, "args": dict}
        context : Any — session state or None

        Returns
        -------
        dict — agent output, or None if the agent could not be resolved.
        """
        entry = self.resolve_step(step)
        if entry is None:
            return None

        handler = entry["handler"]
        args    = step.get("args", {})
        return handler(args, context)

    # ------------------------------------------------------------------ #
    # 5. A2A delegation (agent-as-tool)
    # ------------------------------------------------------------------ #

    def delegate(
        self,
        from_agent: str,
        to_agent:   str,
        args:       Dict[str, Any],
        context:    Any = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Allow one agent to delegate a sub-task to another.

        Parameters
        ----------
        from_agent : str — name of the calling agent (for logging).
        to_agent   : str — name of the target agent.
        args       : dict — arguments to pass.
        context    : Any — shared session context.
        """
        entry = self.resolve_agent(to_agent)
        if entry is None:
            warnings.warn(
                f"[Router] A2A delegation from '{from_agent}' to '{to_agent}' failed: "
                f"'{to_agent}' not registered.",
                stacklevel=2,
            )
            return None
        return entry["handler"](args, context)

    # ------------------------------------------------------------------ #
    # 6. Inspection helpers
    # ------------------------------------------------------------------ #

    def list_available_agents(self) -> List[str]:
        """Return the names of all currently registered agents/tools."""
        return list(self.registry.list_tools().keys())
