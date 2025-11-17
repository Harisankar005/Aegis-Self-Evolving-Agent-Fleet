"""
orchestrator.py
Main orchestrator that runs the multi-agent workflow.
"""

from services.orchestrator.planner import generate_plan
from services.tools.mcp_gateway import MCPRegistry
from services.memory.session_service import SessionService
from services.agents.agent_creator import AgentCreator
from services.evaluation.judge import Judge
from services.orchestrator.tracing import TRACE


class Orchestrator:
    def __init__(self):
        self.sessions = SessionService()
        self.registry = MCPRegistry()
        self.judge = Judge()
        self.creator = AgentCreator(self.registry)

    def run_mission(self, mission_text: str, session_id=None):
        """
        Orchestrates an entire mission.

        Steps:
        1. Create/restore session
        2. Generate mission plan
        3. Loop through steps → call agents
        4. Record traces + memory
        5. Run judge evaluation
        6. Self-evolve if needed
        """
        # Load or create session
        session = self.sessions.get_or_create(session_id)

        # Build plan
        plan = generate_plan(mission_text)
        results = {}

        for step in plan:
            agent_name = step["agent"]
            args = step["args"]

            # Start trace
            span = TRACE.start(f"agent_call:{agent_name}", {"args": args})

            # Call agent from MCP registry
            agent_tool = self.registry.get(agent_name)
            output = agent_tool.call(args, session)

            # Save to session memory
            session.add_event(agent_name, output)

            # End trace
            TRACE.end(span, output)

            results[step["step"]] = output

        # Judge evaluation on trajectory
        score = self.judge.evaluate(mission_text, TRACE.export())

        # Self-evolution logic
        if score < 0.80:
            print("⚠️ Low score detected — evolving system...")
            new_agent = self.creator.generate_new_agent("analytics")
            self.registry.register(new_agent)

        return {
            "mission": mission_text,
            "results": results,
            "score": score,
            "trace": TRACE.export(),
            "session_id": session.id
        }
