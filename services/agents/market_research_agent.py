"""
MarketResearchAgent
-------------------

This agent performs lightweight market research for a given mission or product brief.
It is intentionally written to be compatible with an MCP-style tool registry so that 
the orchestrator can call it as:

    call_agent("MarketResearchAgent", {"query": "..."} , session)

Design Goals:
- Deterministic & testable (mocked logic that can be replaced by Gemini or other LLMs)
- Clean "contract": input args → structured output
- Trace-friendly: return dictionary with clear fields
- Can be extended to use real search (API, Gemini Grounding, or RAG)
- Integrated with SessionService for contextual memory

NOTE:
This version contains MOCKED research output so the notebook can run without API keys.
In production, replace the stub logic with a real LLM call or a search tool via MCP.
"""

from typing import Dict, Any


class MarketResearchAgent:
    """
    MarketResearchAgent encapsulates the logic for gathering high-level,
    structured insights about a target market.

    INPUT SCHEMA (args):
        {
            "query": str   # mission text or product brief
        }

    OUTPUT SCHEMA (dict):
        {
            "insights": str,
            "competitors": list[str],
            "audience": str,
            "confidence": float
        }
    """

    name: str = "MarketResearchAgent"
    description: str = (
        "Analyzes a product or mission brief and returns high-level "
        "market insights, target audience, and competitor signals. "
        "Uses mocked logic by default, but can be upgraded with LLMs or search tools."
    )

    def __init__(self):
        pass

    def __call__(self, args: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent.

        Parameters:
            args: dict containing {"query": "..."}
            session: dict containing session state (conversation + memory hooks)

        Returns:
            Structured dictionary containing research insights.
        """
        query = args.get("query", "").strip()
        if not query:
            return {
                "error": "Missing required field: 'query'",
                "confidence": 0.0
            }

        # --- MOCKED RESEARCH LOGIC ---
        # Replace this section with real calls to:
        # - Gemini (Grounding/Search)
        # - Custom search tools
        # - RAG pipelines
        competitors = self._mock_competitor_lookup(query)
        audience = self._mock_target_audience(query)

        insights = (
            f"Based on the mission '{query}', the target market involves "
            f"{audience}. Key competitors include: {', '.join(competitors)}. "
            "Opportunities detected: strong student demand, low-cost channels, "
            "rapid digital experimentation potential. (Mocked insights)"
        )

        output = {
            "insights": insights,
            "competitors": competitors,
            "audience": audience,
            "confidence": 0.85
        }

        # Optional: write memory
        self._store_memory(output, session)

        return output

    # -------------------------------------------------------------------------
    # Internal mocked helper functions
    # -------------------------------------------------------------------------

    def _mock_competitor_lookup(self, query: str) -> list:
        """
        Mock competitor generation based on simple heuristics.
        """
        query_lower = query.lower()

        if "students" in query_lower or "education" in query_lower:
            return ["CampusHub", "StudyPro", "EduLaunch"]

        if "fitness" in query_lower:
            return ["FitTrack", "HealthGo", "GymWave"]

        if "food" in query_lower or "delivery" in query_lower:
            return ["FoodRush", "QuickEats", "UrbanBite"]

        return ["CompetitorA", "CompetitorB", "CompetitorC"]

    def _mock_target_audience(self, query: str) -> str:
        """
        Mock audience classification.
        """
        query_lower = query.lower()

        if "students" in query_lower:
            return "urban college students aged 18–24"
        if "professionals" in query_lower:
            return "working professionals aged 25–40"
        if "fitness" in query_lower:
            return "health-conscious individuals aged 18–35"

        return "general consumer audience"

    # -------------------------------------------------------------------------
    # Memory writing hook
    # -------------------------------------------------------------------------

    def _store_memory(self, output: Dict[str, Any], session: Dict[str, Any]) -> None:
        """
        Store selected insights into session memory.

        Expected session structure:
            session["memory"] = list of dicts
        """
        if session is None:
            return
        memory_list = session.setdefault("memory", [])
        memory_list.append(
            {
                "type": "market_research",
                "data": output,
                "source": self.name
            }
        )


# -------------------------------------------------------------------------
# Factory function for MCP-style registry compatibility
# -------------------------------------------------------------------------

def agent_entrypoint(args: Dict[str, Any], session: Dict[str, Any]):
    """
    Thin wrapper so the orchestrator can call:
        call_agent("MarketResearchAgent", args, session)
    """
    agent = MarketResearchAgent()
    return agent(args, session)
