import json
from services.tools.gemini_client import GeminiClient

class Planner:
    """
    Planner generates a structured multi-agent plan for a mission using Gemini.
    The output must be a list of steps, each containing:
      - step (string)
      - agent (string)
      - args (dict)
    """

    def __init__(self):
        self.llm = GeminiClient()

    def generate_plan(self, mission_text: str):
        """
        Generate a JSON execution plan for the orchestrator.
        """

        prompt = f"""
        You are an agent planner. Break the mission into 3–5 ordered steps.
        Use only these agents:
          - MarketResearchAgent
          - CopyAgent
          - WebDevAgent

        Mission:
        "{mission_text}"

        Return ONLY valid JSON in this exact Python list format:
        [
          {{"step": "...", "agent": "...", "args": {{"key":"value"}}}},
          ...
        ]
        """

        response = self.llm.generate(prompt)

        try:
            plan = json.loads(response)
        except Exception:
            raise ValueError(f"Invalid JSON plan generated: {response}")

        if not isinstance(plan, list):
            raise ValueError("Planner output must be a list.")

        return plan
