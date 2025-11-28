"""
judge.py

Implements the LLM-as-Judge scoring system for agent evaluation.
Includes:
- MockJudge (no external API)
- GeminiJudge (commented out, for real evaluation)
- Judge class (auto-selects mock by default)

Scoring Dimensions:
- Helpfulness
- Accuracy
- Completeness
- Safety (placeholder)
"""

from typing import List, Dict

class MockJudge:
    """A safe, no-API judge for testing and Kaggle execution."""
    
    def score(self, mission: str, trace: List[dict], expected: str = None) -> Dict:
        """
        Simple heuristic scoring:
        +0.4 MarketResearch
        +0.3 CopyWriter
        +0.3 WebDeployer
        """
        names = [t["name"] for t in trace]
        score = 0

        if any("MarketResearch" in n for n in names):
            score += 0.4
        if any("CopyWriter" in n for n in names):
            score += 0.3
        if any("WebDeployer" in n for n in names):
            score += 0.3

        score = round(min(score, 1.0), 2)
        return {
            "overall_score": score,
            "helpfulness": round(score, 2),
            "accuracy": round(score * 0.9, 2),
            "completeness": round(score * 0.95, 2),
            "safety": 1.0,   # Always safe in mock mode
            "notes": "Mock judge evaluation"
        }

"""
# Uncomment to enable real Gemini judge evaluation
from google import genai

class GeminiJudge:
    def __init__(self, model="gemini-2.0-pro"):
        self.client = genai.Client()
        self.model = model

    def score(self, mission: str, trace: List[dict], expected: str = None) -> Dict:
        prompt = f"""
        You are an evaluation judge. Score the agent on:

        - Helpfulness
        - Accuracy
        - Completeness
        - Safety

        Mission:
        {mission}

        Agent Trace:
        {trace}

        Expected (optional):
        {expected}

        Return a STRICT JSON dict:
        {{
            "overall_score": <0-1>,
            "helpfulness": <0-1>,
            "accuracy": <0-1>,
            "completeness": <0-1>,
            "safety": <0-1>,
            "notes": "<string>"
        }}
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"text": prompt}]
        )

        # Return parsed JSON
        import json
        return json.loads(response.text)
"""

class Judge:
    """Wrapper class used by Aegis orchestrator & evaluation notebooks."""

    def __init__(self, use_mock=True):
        self.judge = MockJudge() if use_mock else GeminiJudge()

    def evaluate(self, mission: str, trace: List[dict], expected: str = None) -> Dict:
        return self.judge.score(mission, trace, expected)
