"""
judge.py — LLM-as-Judge evaluation module for Aegis

This module evaluates full agent trajectories using:
- Task completeness
- Agent participation
- Tool usage
- Mock or real LLM scoring

You can plug in Gemini or any LLM using the provided stub.
"""

from typing import List, Dict, Any

class Judge:
    """
    Mock LLM-as-Judge that assigns a score based on whether
    required agents participated in the trajectory.
    """

    REQUIRED_AGENTS = [
        "MarketResearchAgent",
        "CopyAgent",
        "WebDevAgent"
    ]

    def __init__(self, llm_client=None):
        """
        llm_client can be used to plug in Gemini or other LLMs.
        Keep None for mocked evaluation.
        """
        self.llm = llm_client

    def evaluate(self, mission: str, trace: List[Dict[str, Any]]) -> float:
        """
        Returns a float score between 0 and 1.

        Score formula:
        +0.35 for MarketResearchAgent
        +0.35 for CopyAgent
        +0.25 for WebDevAgent
        """

        agent_names = [span["name"] for span in trace]
        score = 0.0

        if any("MarketResearchAgent" in n for n in agent_names):
            score += 0.35
        if any("CopyAgent" in n for n in agent_names):
            score += 0.35
        if any("WebDevAgent" in n for n in agent_names):
            score += 0.25

        return round(min(score, 1.0), 2)

    def evaluate_with_llm(self, mission: str, trace: List[Dict[str, Any]]) -> float:
        """
        Optional pathway for real LLM evaluation.
        DO NOT include API keys in this file.
        """

        if self.llm is None:
            raise RuntimeError("No LLM client provided")

        # Example Gemini prompt structure (pseudo-code)
        prompt = f"""
        You are an evaluation judge. Score the agent's response 0–1.
        Mission: {mission}
        Trace: {trace}
        """

        response = self.llm.generate_content(prompt)
        score = float(response.text.strip())
        return max(0.0, min(score, 1.0))
