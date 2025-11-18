# services/agents/market_research_agent.py

from typing import Dict, Any
from services.tools.gemini_client import GeminiClient

class MarketResearchAgent:
    name = "MarketResearchAgent"
    description = "Provides market research insights for a given query."

    def __init__(self):
        self.llm = GeminiClient()

    def call(self, args: Dict[str, Any], session: Any) -> Dict[str, Any]:
        query = args.get("query", "")

        prompt = f"""
        Conduct a concise market research analysis for the topic:
        "{query}"

        Include:
        - Major competitors
        - Key audience demographics
        - Relevant keywords
        - Market opportunities or risks

        Format results in clear bullet points.
        """

        output = self.llm.generate(prompt)

        return {
            "agent": self.name,
            "output": output
        }
