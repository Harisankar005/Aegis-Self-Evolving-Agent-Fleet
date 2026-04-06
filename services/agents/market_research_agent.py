"""
market_research_agent.py
-------------------------
MarketResearchAgent — Specialist agent for market analysis.

Responsibilities:
- Analyse a product/mission brief.
- Return structured market insights, target audience, and competitors.
- Optionally write findings to the session state for downstream agents.
- Use mocked logic by default (no API key required).

MCP handler signature:
    market_research_agent(args: dict, context: Any) -> dict

FIX LOG (v2):
- Top-level function market_research_agent() added as the primary export.
  The v1 module only exported agent_entrypoint() (an alias) but __init__.py
  imported market_research_agent (the class name), causing an ImportError
  because Python treats it as the class, not a callable with the right signature.
- _store_memory() now writes into session.state (via context) when context is a
  dict, making memory available to downstream agents in the same mission.
- agent_entrypoint kept as a backward-compatible alias.
"""

from typing import Any, Dict


# ─── Internal class (domain logic) ───────────────────────────────────────────

class _MarketResearchAgent:
    """
    Internal implementation class.

    Public interface is the module-level market_research_agent() function.
    """

    name: str        = "MarketResearchAgent"
    description: str = (
        "Analyses a product or mission brief and returns high-level market "
        "insights, target audience, and competitor signals."
    )

    def __call__(
        self,
        args:    Dict[str, Any],
        context: Any,
    ) -> Dict[str, Any]:
        query = args.get("query", "").strip()
        if not query:
            return {"error": "Missing required field: 'query'", "confidence": 0.0}

        competitors = self._mock_competitors(query)
        audience    = self._mock_audience(query)

        insights = (
            f"For the mission '{query}', the target market is {audience}. "
            f"Key competitors include: {', '.join(competitors)}. "
            "Opportunities: strong digital demand, low-cost channel experiments, "
            "rapid iteration potential. (Mocked research output)"
        )

        output = {
            "insights":    insights,
            "competitors": competitors,
            "audience":    audience,
            "confidence":  0.85,
        }

        self._store_memory(output, context)
        return output

    # ── Mock helpers ──────────────────────────────────────────────────────

    def _mock_competitors(self, query: str) -> list:
        q = query.lower()
        if any(w in q for w in ("student", "education", "campus")):
            return ["CampusHub", "StudyPro", "EduLaunch"]
        if "fitness" in q:
            return ["FitTrack", "HealthGo", "GymWave"]
        if any(w in q for w in ("food", "delivery", "restaurant")):
            return ["FoodRush", "QuickEats", "UrbanBite"]
        return ["CompetitorA", "CompetitorB", "CompetitorC"]

    def _mock_audience(self, query: str) -> str:
        q = query.lower()
        if "student" in q:
            return "urban college students aged 18–24"
        if "professional" in q:
            return "working professionals aged 25–40"
        if "fitness" in q:
            return "health-conscious individuals aged 18–35"
        return "general consumer audience"

    def _store_memory(self, output: Dict[str, Any], context: Any) -> None:
        """Persist key findings into session state for downstream agents."""
        if isinstance(context, dict):
            context.setdefault("memory", []).append({
                "type":   "market_research",
                "data":   output,
                "source": self.name,
            })


# ─── Module-level singleton ───────────────────────────────────────────────────

_agent_instance = _MarketResearchAgent()


# ─── Public callable (imported by orchestrator and __init__.py) ───────────────

def market_research_agent(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """
    Primary MCP handler for MarketResearchAgent.

    Parameters
    ----------
    args    : dict — must contain {"query": "..."}.
    context : Any — session state dict or Session object (may be None).

    Returns
    -------
    dict
        {
            "insights":    str,
            "competitors": list[str],
            "audience":    str,
            "confidence":  float,
        }
    """
    return _agent_instance(args, context)


# Backward-compatible alias
agent_entrypoint = market_research_agent


# ─── Agent metadata for MCP registry / documentation ─────────────────────────

AGENT_METADATA: Dict[str, Any] = {
    "name":        "MarketResearchAgent",
    "description": _MarketResearchAgent.description,
    "input_schema": {
        "query": "string — mission text or product brief",
    },
    "output_schema": {
        "insights":    "string",
        "competitors": "list of strings",
        "audience":    "string",
        "confidence":  "float",
    },
}
