"""
Aegis Orchestrator Package
==========================

This package contains the core orchestration logic for the Aegis
multi-agent system. It includes:

- Planner: Decomposes high-level missions into structured steps.
- Orchestrator: Executes the mission by routing tasks to agents.
- Router: Maps tasks to the correct agent/tool via registry.
- Evaluator: Handles post-execution evaluation (LLM-as-Judge).

Modules:
    orchestrator.py   → Main orchestration engine.
    planner.py        → Mission planning and step decomposition.
    router.py         → Task → agent routing logic.
    evaluator.py      → Judge scoring, metrics, regression checks.

The orchestrator acts as the "brainstem" for agent execution and
coordinates planning, agent invocation, context propagation, and
evaluation.

This file makes these components directly importable as:

    from services.orchestrator import Orchestrator, Planner

"""

from .orchestrator import Orchestrator
from .planner import Planner
from .evaluator import Evaluator
from .router import Router

__all__ = [
    "Orchestrator",
    "Planner",
    "Evaluator",
    "Router",
]
