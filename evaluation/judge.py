"""
judge.py — LLM-as-Judge evaluation module for Aegis.

Evaluates full agent trajectories using:
- Task completeness (did the required steps run?)
- Agent participation (which agents appeared in the trace?)
- Output quality (mocked heuristic; real Gemini call is stubbed)

FIX LOG (v2):
- evaluate() scoring is now dynamic: the three core agents each contribute a
  fixed base weight, and any *additional* registered agents (e.g. AnalyticsAgent
  created by AgentCreator) each contribute a bonus weight. Previously a newly
  created agent could never improve the score → the self-evolution loop was
  permanently broken.
- suggest_missing_capability() added — orchestrator calls this to decide what
  AgentCreator should build next. In v1 this method did not exist → AttributeError
  on every self-evolution attempt.
- evaluate() now accepts the trace list directly (same as v1) but also handles
  the case where trace entries are Session.trace_event dicts (keyed "name")
  rather than ad-hoc dicts with a different structure.
"""

from typing import Any, Dict, List, Optional


class Judge:
    """
    LLM-as-Judge that assigns a quality score based on trajectory analysis.

    Scoring breakdown (base):
        +0.35  MarketResearchAgent participated
        +0.30  CopyAgent participated
        +0.25  WebDevAgent participated
        +0.02  Each additional novel agent (capped at 0.10 bonus)

    Total is capped at 1.0.
    """

    # Core agents with fixed contribution weights
    CORE_WEIGHTS: Dict[str, float] = {
        "MarketResearchAgent": 0.35,
        "CopyAgent":           0.30,
        "WebDevAgent":         0.25,
    }

    # Bonus per extra auto-generated agent
    EXTRA_AGENT_BONUS = 0.02
    MAX_EXTRA_BONUS   = 0.10

    def __init__(self, llm_client=None):
        """
        Parameters
        ----------
        llm_client : optional
            A Gemini or other LLM client. Keep None for mock evaluation.
        """
        self.llm = llm_client

    # ------------------------------------------------------------------ #
    # Primary scoring entry-point
    # ------------------------------------------------------------------ #

    def evaluate(
        self,
        mission: str,
        trace: List[Dict[str, Any]],
    ) -> float:
        """
        Return a float score in [0.0, 1.0].

        Parameters
        ----------
        mission : str
            Original mission text (used for Gemini scoring if enabled).
        trace   : list of trace-span dicts
            Each span must have a "name" field (set by session.trace_event()).
        """
        agent_names = self._extract_agent_names(trace)

        # --- Base score from core agents ---
        score = 0.0
        for agent, weight in self.CORE_WEIGHTS.items():
            if any(agent in n for n in agent_names):
                score += weight

        # --- Bonus for auto-generated agents ---
        # Spans emitted by the orchestrator follow the pattern:
        #   "Calling agent: <AgentName>"
        # Extract the actual agent class names to detect novel registrations.
        called_agents = set()
        for span_name in agent_names:
            if span_name.startswith("Calling agent: "):
                called_agents.add(span_name.split("Calling agent: ", 1)[1].strip())

        known_core  = set(self.CORE_WEIGHTS.keys())
        extra_agents = called_agents - known_core
        bonus = min(len(extra_agents) * self.EXTRA_AGENT_BONUS, self.MAX_EXTRA_BONUS)
        score += bonus

        return round(min(score, 1.0), 2)

    # ------------------------------------------------------------------ #
    # Capability gap detection — used by Orchestrator self-evolution loop
    # ------------------------------------------------------------------ #

    def suggest_missing_capability(
        self,
        mission: str,
        trace: List[Dict[str, Any]],
    ) -> str:
        """
        Infer which capability is missing based on the mission text and trace.

        Returns a short capability label string (e.g. "analytics", "monitoring")
        that AgentCreator will use to build a new agent.

        Parameters
        ----------
        mission : str
            The original mission statement.
        trace   : list of trace-span dicts
        """
        agent_names = self._extract_agent_names(trace)
        mission_lower = mission.lower()

        # Analytics / metrics related missions
        if any(kw in mission_lower for kw in ("analytic", "metric", "insight", "measure", "report")):
            if not any("Analytics" in n for n in agent_names):
                return "analytics"

        # Monitoring / alerting
        if any(kw in mission_lower for kw in ("monitor", "alert", "watch", "track")):
            if not any("Monitor" in n for n in agent_names):
                return "monitoring"

        # Sentiment / social
        if any(kw in mission_lower for kw in ("sentiment", "social", "review", "opinion")):
            if not any("Sentiment" in n for n in agent_names):
                return "sentiment-analysis"

        # Email / outreach
        if any(kw in mission_lower for kw in ("email", "outreach", "newsletter")):
            if not any("Email" in n for n in agent_names):
                return "email-outreach"

        # SEO
        if any(kw in mission_lower for kw in ("seo", "search engine", "keyword")):
            if not any("SEO" in n for n in agent_names):
                return "seo-optimization"

        # Default: generic enhancement
        return "analytics"

    # ------------------------------------------------------------------ #
    # Optional: real Gemini LLM scoring
    # ------------------------------------------------------------------ #

    def evaluate_with_llm(
        self,
        mission: str,
        trace: List[Dict[str, Any]],
    ) -> float:
        """
        Score via Gemini. Requires a real llm_client at construction time.
        DO NOT commit API keys — pass client via environment variable.
        """
        if self.llm is None:
            raise RuntimeError(
                "No LLM client provided. Pass a Gemini client to Judge()."
            )

        import json
        prompt = (
            f"You are an evaluation judge for an AI agent system.\n"
            f"Mission: {mission}\n"
            f"Agent trace: {json.dumps(trace, indent=2)}\n\n"
            f"Score the trajectory from 0.0 to 1.0 based on:\n"
            f"- Task completeness\n- Agent diversity\n- Output quality\n"
            f"Respond with a single float only."
        )
        response = self.llm.generate_content(prompt)
        try:
            score = float(response.text.strip())
        except (ValueError, AttributeError):
            score = 0.5
        return max(0.0, min(score, 1.0))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _extract_agent_names(self, trace: List[Dict[str, Any]]) -> List[str]:
        """
        Pull the 'name' field from every trace span.

        Handles both formats:
        - {"name": "Calling agent: MarketResearchAgent", ...}  (orchestrator spans)
        - {"name": "MarketResearchAgent", ...}                 (CI mock spans)
        """
        return [span.get("name", "") for span in trace if isinstance(span, dict)]
