"""
services/agents/__init__.py
============================
Exposes all agent entry-points for the Aegis multi-agent system.

Each agent module exports a top-level callable with the MCP handler signature:
    fn(args: dict, context: Any) -> dict

They are registered into the MCPRegistry by the Orchestrator at startup.

FIX LOG (v2):
- Imports now match the *function* names actually exported by each module.
  v1 imported "market_research_agent" expecting a function but the module's
  primary export was named "agent_entrypoint" → ImportError at startup.
- analytics_agent is now imported directly (no longer wrapped in try/except
  as "optional") because the module ships with the repository from day one.
"""

from .market_research_agent import market_research_agent
from .copy_agent             import copy_agent
from .webdev_agent           import webdev_agent
from .analytics_agent        import analytics_agent
from .agent_creator          import AgentCreator

__all__ = [
    "market_research_agent",
    "copy_agent",
    "webdev_agent",
    "analytics_agent",
    "AgentCreator",
]
