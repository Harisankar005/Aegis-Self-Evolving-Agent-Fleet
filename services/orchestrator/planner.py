"""
planner.py
----------
Planning component for the Aegis multi-agent system.

The Planner is responsible for:
- Interpreting a high-level mission string.
- Decomposing it into a sequence of actionable agent steps.
- Returning a normalised plan list for the Orchestrator to execute.

Each plan step has the structure:
    {
        "step":  "<label>",
        "agent": "<AgentName>",
        "args":  { ... }
    }

FIX LOG (v2):
- create_plan() added as an alias for generate_plan() — the v1 orchestrator
  called self.planner.create_plan() but the Planner only defined generate_plan(),
  causing an AttributeError on every mission run.
- AnalyticsAgent added to the default pipeline so that the AnalyticsAgent
  registered at startup actually gets exercised by the planner.
- Keyword-based mission routing added so that missions mentioning "analytics",
  "monitor", "email", etc. include the matching specialist step automatically.
- llm_generate_plan() documented and kept as an opt-in Gemini pathway.
"""

from typing import Any, Callable, Dict, List, Optional


class Planner:
    """
    High-level task decomposition engine.

    Converts a natural-language mission into a structured list of agent steps.
    The default implementation is deterministic (rule-based) for reproducibility;
    it can be upgraded to a real LLM call via llm_generate_plan().
    """

    # Default pipeline executed for every mission
    DEFAULT_PIPELINE: List[tuple] = [
        ("research",    "MarketResearchAgent"),
        ("copywriting", "CopyAgent"),
        ("analytics",   "AnalyticsAgent"),
        ("deployment",  "WebDevAgent"),
    ]

    # Optional keyword → extra step mappings for richer missions
    KEYWORD_STEPS: Dict[str, tuple] = {
        "monitor":    ("monitoring",    "MonitoringAgent"),
        "sentiment":  ("sentiment",     "SentimentAnalysisAgent"),
        "email":      ("email-outreach","EmailOutreachAgent"),
        "seo":        ("seo",           "SeoOptimizationAgent"),
    }

    def __init__(self):
        pass

    # ------------------------------------------------------------------ #
    # Primary public method (canonical name)
    # ------------------------------------------------------------------ #

    def generate_plan(self, mission_text: str) -> List[Dict[str, Any]]:
        """
        Return a deterministic sequence of agent steps for the given mission.

        Parameters
        ----------
        mission_text : str
            The high-level objective provided by the user.

        Returns
        -------
        list of dict — normalised plan steps.
        """
        mission_lower = mission_text.lower()
        plan: List[Dict[str, Any]] = []

        # ── Core pipeline ────────────────────────────────────────────────
        for step_label, agent_name in self.DEFAULT_PIPELINE:
            args = self._build_args(step_label, mission_text)
            plan.append({
                "step":  step_label,
                "agent": agent_name,
                "args":  args,
            })

        # ── Keyword-triggered extras ─────────────────────────────────────
        for keyword, (extra_step, extra_agent) in self.KEYWORD_STEPS.items():
            if keyword in mission_lower:
                plan.append({
                    "step":  extra_step,
                    "agent": extra_agent,
                    "args":  {"input": mission_text},
                })

        return plan

    def create_plan(self, mission_text: str) -> List[Dict[str, Any]]:
        """
        Alias for generate_plan() — kept for backward compatibility.

        The v1 Orchestrator called self.planner.create_plan() but the method
        was named generate_plan(). This alias ensures both names work.
        """
        return self.generate_plan(mission_text)

    # ------------------------------------------------------------------ #
    # Argument builder
    # ------------------------------------------------------------------ #

    def _build_args(self, step_label: str, mission_text: str) -> Dict[str, Any]:
        """Map a step label to its agent's expected argument dict."""
        mapping = {
            "research":    {"query":    mission_text},
            "copywriting": {"brief":    mission_text},
            "analytics":   {"campaign": mission_text},
            "deployment":  {"brief":    mission_text},
        }
        return mapping.get(step_label, {"input": mission_text})

    # ------------------------------------------------------------------ #
    # Optional: Gemini LLM planning pathway
    # ------------------------------------------------------------------ #

    def llm_generate_plan(
        self,
        mission_text: str,
        llm_callable: Callable,
    ) -> List[Dict[str, Any]]:
        """
        Generate a dynamic plan using a Gemini or compatible LLM.

        Parameters
        ----------
        mission_text : str
            The user mission.
        llm_callable : Callable
            A function wrapping a Gemini call; must return a parsed list of
            plan-step dicts (same schema as generate_plan output).

        Returns
        -------
        list of dict — LLM-generated plan, or the deterministic fallback on error.

        Usage example (local dev only — do not commit API keys):
            from google import genai
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            plan = planner.llm_generate_plan(
                mission,
                lambda p: json.loads(client.models.generate_content("gemini-2.0-pro", p).text)
            )
        """
        prompt = (
            "You are an advanced planning agent for a multi-agent marketing system.\n"
            "Decompose the mission below into 3–6 steps. Each step must map to one of:\n"
            "  MarketResearchAgent, CopyAgent, AnalyticsAgent, WebDevAgent.\n\n"
            f"Mission: {mission_text}\n\n"
            "Return ONLY a JSON array with this schema per element:\n"
            '  [{"step": "...", "agent": "...", "args": {...}}]'
        )
        try:
            plan = llm_callable(prompt)
            if isinstance(plan, list) and plan:
                return plan
            raise ValueError("LLM returned empty or invalid plan.")
        except Exception:
            # Fallback to deterministic plan
            return self.generate_plan(mission_text)
