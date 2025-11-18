import json
from services.tools.gemini_client import GeminiClient

class Judge:
    def __init__(self):
        self.llm = GeminiClient()

    def evaluate(self, mission: str, trace):
        prompt = f"""
        You are an evaluation engine. Assess how well the following agent outputs
        complete the mission.

        Mission:
        {mission}

        Trace (list of agent outputs):
        {trace}

        Evaluate the overall performance using:
        - Helpfulness
        - Completeness
        - Correctness
        - Safety

        Return only a JSON object:
        {{"score": 0.0}}
        """

        result = self.llm.generate(prompt)
        try:
            score_data = json.loads(result)
            return float(score_data.get("score", 0.0))
        except Exception:
            return 0.0
