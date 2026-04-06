"""
orchestrator.py
---------------
The Orchestrator is the central controller of the Aegis multi-agent system.

It:
1. Accepts a mission string.
2. Decomposes it via the Planner.
3. Pre-registers all specialist agents into the MCP registry.
4. Delegates each plan step to the appropriate agent.
5. Stores outputs in the Session and writes key facts to the MemoryBank.
6. Emits structured trace spans for observability.
7. Evaluates the trajectory with the Judge.
8. Triggers AgentCreator to fill capability gaps when the score is low.

FIX LOG (v2):
- Import path fixed: evaluation.judge → was services.evaluation.judge (non-existent).
- Planner method: generate_plan() — was create_plan() (non-existent in v1 Planner).
- Agent invocation: agent_entry["handler"] — was agent_entry["callable"] → KeyError.
- suggest_missing_capability() call fixed: now returns a string; was passing the
  string directly to generate_new_agent() but v1 AgentCreator expected a dict.
- generate_new_agent() now receives a plain string capability label.
- Agents pre-registered at __init__ time — v1 started with an empty registry so
  every call_agent() raised "Tool not found" immediately.
- MemoryBank wired in: research insights are stored after each step.
- session.trace_event() used consistently (added to Session in v2).
"""

from typing import Any, Dict, List, Optional

from services.orchestrator.planner          import Planner
from services.memory.session_service        import SessionService
from services.memory.memory_bank            import MemoryBank
from services.tools.mcp_gateway             import MCPRegistry
from evaluation.judge                       import Judge
from services.agents.agent_creator          import AgentCreator

# Specialist agent callables
from services.agents.market_research_agent  import market_research_agent
from services.agents.copy_agent             import copy_agent
from services.agents.webdev_agent           import webdev_agent
from services.agents.analytics_agent        import analytics_agent


class Orchestrator:
    """
    Coordinates the entire Aegis agentic workflow end-to-end.

    Attributes
    ----------
    EVOLUTION_THRESHOLD : float
        Judge score below which AgentCreator is triggered (default 0.85).
    """

    EVOLUTION_THRESHOLD: float = 0.85

    def __init__(self):
        self.planner  = Planner()
        self.sessions = SessionService()
        self.memory   = MemoryBank()
        self.registry = MCPRegistry()
        self.judge    = Judge()
        self.creator  = AgentCreator(self.registry)

        # Pre-register all specialist agents so every mission can run
        self._register_core_agents()

    # ------------------------------------------------------------------ #
    # Agent registration
    # ------------------------------------------------------------------ #

    def _register_core_agents(self):
        """
        Register all built-in specialist agents into the MCP registry.

        Called once at construction. AgentCreator may add further entries
        during self-evolution.
        """
        self.registry.register(
            name="MarketResearchAgent",
            description="Analyses a mission brief and returns market insights, audience, and competitors.",
            schema={"query": str},
            handler=market_research_agent,
        )
        self.registry.register(
            name="CopyAgent",
            description="Generates marketing copy for a given brief.",
            schema={"brief": str},
            handler=copy_agent,
        )
        self.registry.register(
            name="WebDevAgent",
            description="Produces a deployable landing-page artifact from a brief.",
            schema={"brief": str},
            handler=webdev_agent,
        )
        self.registry.register(
            name="AnalyticsAgent",
            description="Summarises campaign performance metrics and engagement signals.",
            schema={"campaign": str},
            handler=analytics_agent,
        )

    # ------------------------------------------------------------------ #
    # Internal: single step execution
    # ------------------------------------------------------------------ #

    def _invoke_agent(
        self,
        step:    Dict[str, Any],
        session,
    ) -> Dict[str, Any]:
        """
        Execute one step of the plan.

        1. Resolves the agent from the registry.
        2. Emits a trace span.
        3. Calls the agent handler.
        4. Appends the output to session events.
        5. Writes a summary to MemoryBank for future retrieval.
        """
        agent_name = step["agent"]
        args       = step.get("args", {})

        # Graceful skip: keyword-triggered agents may not be registered yet.
        # AgentCreator can synthesise them on the next self-evolution cycle.
        if not self.registry.exists(agent_name):
            session.trace_event(
                f"Agent not found (skipped): {agent_name}",
                {"agent": agent_name, "reason": "not registered"},
            )
            return {
                "skipped": True,
                "agent":   agent_name,
                "reason":  "not registered — will be created by AgentCreator",
            }

        agent_entry = self.registry.get(agent_name)

        # Observability: trace span
        session.trace_event(
            f"Calling agent: {agent_name}",
            {"args": args},
        )

        # Execute — handler signature: fn(args, context) → dict
        # Pass the session state dict as context so agents can read prior outputs
        response = agent_entry["handler"](args, session.state)

        # Persist event in session history
        session.append_event(agent_name, response)

        # Persist a memory entry for cross-session retrieval
        self.memory.store(
            namespace=session.id,
            key=agent_name,
            value=str(response),
            agent=agent_name,
            session_id=session.id,
            importance=0.6,
        )

        # Carry outputs forward through state so later agents can reference them
        session.set_state(agent_name, response)

        return response

    # ------------------------------------------------------------------ #
    # Public API: run a mission
    # ------------------------------------------------------------------ #

    def run_mission(
        self,
        mission_text: str,
        session_id:   Optional[str] = None,
        auto_evolve:  bool          = True,
    ) -> Dict[str, Any]:
        """
        Process a mission end-to-end.

        Parameters
        ----------
        mission_text : str
            Natural-language description of the task.
        session_id   : str, optional
            Resume an existing session, or start fresh if None.
        auto_evolve  : bool
            If True, trigger AgentCreator when the judge score is below threshold.

        Returns
        -------
        dict
            {
                "session_id": str,
                "plan":       list,
                "results":    dict,
                "score":      float,
                "trace":      list,
            }
        """
        session = self.sessions.get_or_create(session_id)
        session.trace_event("Mission started", {"mission": mission_text})

        # ── PLAN ────────────────────────────────────────────────────────
        plan = self.planner.generate_plan(mission_text)
        session.trace_event("Plan generated", {"steps": [s["step"] for s in plan]})

        # ── EXECUTE ──────────────────────────────────────────────────────
        results: Dict[str, Any] = {}
        for step in plan:
            output = self._invoke_agent(step, session)
            results[step["step"]] = output

        # ── EVALUATE ─────────────────────────────────────────────────────
        score = self.judge.evaluate(mission_text, session.trace)
        session.trace_event("Judge score computed", {"score": score})

        # ── SELF-EVOLUTION (optional) ────────────────────────────────────
        if auto_evolve and score < self.EVOLUTION_THRESHOLD:
            capability = self.judge.suggest_missing_capability(
                mission_text, session.trace
            )
            session.trace_event("Capability gap detected", {"capability": capability})

            new_spec = self.creator.generate_new_agent(capability)
            session.trace_event("New agent generated", {"agent": new_spec["name"]})

        # ── PACKAGE RESPONSE ─────────────────────────────────────────────
        response = {
            "session_id": session.id,
            "plan":       plan,
            "results":    results,
            "score":      score,
            "trace":      session.trace,
        }

        session.trace_event("Mission completed", {"status": "success"})
        return response


# ─── Quick smoke-test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    o = Orchestrator()
    result = o.run_mission("Launch a marketing campaign for Product X")
    print("\n=== Final Result ===")
    print(f"Score  : {result['score']}")
    print(f"Steps  : {[s['step'] for s in result['plan']]}")
    print(f"Traces : {len(result['trace'])} spans")
