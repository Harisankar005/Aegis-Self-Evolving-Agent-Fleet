from services.orchestrator.planner import Planner
from services.tools.mcp_registry import MCPRegistry
from services.memory.session_service import SessionService
from evaluation.judge import Judge
from services.agents.agent_creator import AgentCreator


class Orchestrator:
    """
    Coordinates mission execution:
    1. Uses Planner to break mission into steps.
    2. Executes each step with the appropriate agent from the registry.
    3. Stores execution details in SessionService.
    4. Scores the output via Judge.
    5. Triggers AgentCreator to fill capability gaps when needed.
    """

    def __init__(self):
        self.registry = MCPRegistry()
        self.sessions = SessionService()
        self.planner = Planner()
        self.judge = Judge()
        self.creator = AgentCreator(self.registry)

    def register_agent(self, name: str, agent_impl, description: str = ""):
        """
        Register an agent into the MCP registry.
        Each agent implementation must expose a `.call(args, session)` method.
        """
        self.registry.register(name, agent_impl, description)

    def run_mission(self, mission: str, session_id: str = None) -> dict:
        """
        Run a full mission end-to-end:
        - Generate plan
        - Execute each agent step
        - Record events in a session
        - Evaluate using the judge
        - Auto-create agents on low score
        """
        session = self.sessions.get_or_create(session_id)

        plan = self.planner.generate_plan(mission)
        results = {}

        for step in plan:
            agent_name = step["agent"]
            agent = self.registry.get(agent_name)
            output = agent.call(step.get("args", {}), session)

            session.append_event(agent_name, output)
            results[step["step"]] = output

        score = self.judge.evaluate(mission, session.trace)

        # Self-improvement: create a new agent if score is low
        if score < 0.75:
            spec, new_agent = self.creator.generate_new_agent("analytics")
            self.registry.register(spec["name"], new_agent, spec.get("description", ""))

        return {
            "mission": mission,
            "results": results,
            "score": score,
            "session_id": session.id,
            "trace": session.trace,
        }
