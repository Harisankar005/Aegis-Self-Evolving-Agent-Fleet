"""
orchestrator.py
----------------

The Orchestrator is the central controller of the Aegis multi-agent system.
It takes a mission, decomposes it using the Planner, calls agents using the
MCP-style registry, manages session state, collects traces, runs evaluation,
and triggers the AgentCreator if new capabilities are needed.

This file demonstrates:
- Multi-agent orchestration
- Tool/agent delegation (MCP registry)
- Session & memory integration
- Observability (trace emission)
- Judge evaluation workflow
- Self-evolution via AgentCreator

All models & tools are mocked for safe and self-contained execution.
"""

from typing import Dict, Any, Optional

from services.orchestrator.planner import Planner
from services.memory.session_service import SessionService
from services.tools.mcp_gateway import MCPRegistry
from services.evaluation.judge import Judge
from services.agents.agent_creator import AgentCreator


class Orchestrator:
    """
    The Orchestrator coordinates the entire agentic workflow:
    1. Accepts a mission
    2. Generates a plan via Planner
    3. Delegates tasks to agents using MCPRegistry
    4. Stores events in SessionService
    5. Emits traces for observability
    6. Runs LLM-as-Judge evaluation
    7. Triggers AgentCreator if score is low
    """

    def __init__(self):
        self.planner = Planner()
        self.sessions = SessionService()
        self.registry = MCPRegistry()
        self.judge = Judge()
        self.creator = AgentCreator(self.registry)

        # judge threshold for triggering self-evolution
        self.EVOLUTION_THRESHOLD = 0.85

    # ---------------------------------------------------------
    # INTERNAL: agent call wrapper
    # ---------------------------------------------------------
    def _invoke_agent(self, step: Dict[str, Any], session):
        """
        Executes a single step of the plan by calling the correct agent,
        stores outputs in the session, and returns agent response.
        """

        agent_name = step["agent"]
        args = step.get("args", {})

        # Retrieve agent/tool from the MCP-style registry
        agent_entry = self.registry.get(agent_name)

        # Observability: log + trace
        session.trace_event(
            f"Calling agent: {agent_name}",
            {"args": args}
        )

        response = agent_entry["callable"](args, session)

        # Add agent's output to the session event log
        session.append_event(agent_name, response)

        return response

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT: run a mission
    # ---------------------------------------------------------
    def run_mission(
        self,
        mission_text: str,
        session_id: Optional[str] = None,
        auto_evolve: bool = True
    ) -> Dict[str, Any]:
        """
        Process a mission end-to-end:
        - Create or load session
        - Plan the mission
        - Execute each step with agents
        - Collect results & traces
        - Evaluate with judge
        - Optionally self-evolve

        Args:
            mission_text: str
            session_id: optional existing session
            auto_evolve: whether to trigger AgentCreator when score is low

        Returns:
            dict containing plan, results, score, trace, session_id
        """

        # Get new or existing session
        session = self.sessions.get_or_create(session_id)
        session.trace_event("Mission started", {"mission": mission_text})

        # PLAN
        plan = self.planner.create_plan(mission_text)
        session.trace_event("Plan generated", {"plan": plan})

        # EXECUTE AGENTS
        results = {}
        for step in plan:
            out = self._invoke_agent(step, session)
            results[step["step"]] = out

        # EVALUATE
        score = self.judge.evaluate(mission_text, session.trace)
        session.trace_event("Judge score computed", {"score": score})

        # SELF-EVOLUTION (optional)
        if auto_evolve and score < self.EVOLUTION_THRESHOLD:
            # The Planner + Judge examine session to infer missing capability
            missing_capability = self.judge.suggest_missing_capability(
                mission_text, session.trace
            )

            session.trace_event(
                "Capability gap detected",
                {"capability": missing_capability}
            )

            new_agent_spec = self.creator.generate_new_agent(missing_capability)
            session.trace_event(
                "New agent generated",
                {"spec": new_agent_spec}
            )

            # Register the new agent in the MCP tool registry
            self.registry.register(new_agent_spec)

        # PACKAGE RESPONSE
        response = {
            "session_id": session.id,
            "plan": plan,
            "results": results,
            "score": score,
            "trace": session.trace,
        }

        session.trace_event("Mission completed", {"status": "success"})
        return response


# ---------------------------------------------------------
# Example direct CLI-style usage:
# (This block won't run inside Kaggle but useful for local dev)
# ---------------------------------------------------------
if __name__ == "__main__":
    o = Orchestrator()
    result = o.run_mission("Launch campaign for Product X")
    print("Final result:")
    print(result)
