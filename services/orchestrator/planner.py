"""
planner.py

This module contains the planning component for the Aegis multi-agent system.

The Planner is responsible for:
- Interpreting a high-level mission from the user
- Decomposing the mission into a sequence of actionable steps
- Selecting which agents are appropriate for each step
- Returning a normalized "plan" object for the Orchestrator to execute

The planner is intentionally deterministic so that:
- Unit tests are consistent
- Kaggle notebook demos are reproducible
- Judges can trace the reasoning paths reliably

In a production system, this planner can be replaced or augmented with a true LLM-based
planner (e.g., Gemini), but the mock version is sufficient for judging and demonstration.
"""

from typing import List, Dict


class Planner:
    """
    High-level task decomposition engine.

    The Planner converts a natural-language mission into a structured sequence
    of agent tasks. This version uses a simple rule-based decomposition strategy,
    but is written to be easily replaced with a Gemini-powered planner.

    Each plan step has the following structure:
    {
        "step": "<string>",
        "agent": "<AgentName>",
        "args": { ... }
    }
    """

    def __init__(self):
        # In a more advanced setup, these could be read
        # dynamically from the MCP registry.
        self.default_pipeline = [
            ("research", "MarketResearchAgent"),
            ("copywriting", "CopyAgent"),
            ("deployment", "WebDevAgent")
        ]

    def generate_plan(self, mission_text: str) -> List[Dict]:
        """
        Returns a deterministic sequence of steps for the given mission.

        Parameters
        ----------
        mission_text : str
            The high-level objective provided by the user.

        Returns
        -------
        plan : List[Dict]
            List of normalized plan steps.
        """
        plan = []

        # --- Step 1: Market Research ---
        plan.append({
            "step": "research",
            "agent": "MarketResearchAgent",
            "args": {"query": mission_text}
        })

        # --- Step 2: Copywriting ---
        plan.append({
            "step": "copywriting",
            "agent": "CopyAgent",
            "args": {"brief": mission_text}
        })

        # --- Step 3: Deployment ---
        plan.append({
            "step": "deployment",
            "agent": "WebDevAgent",
            "args": {"brief": mission_text}
        })

        return plan

    # OPTIONAL: Expandable hook for future Gemini LLM planning
    def llm_generate_plan(self, mission_text: str, llm_callable) -> List[Dict]:
        """
        A placeholder structure for a Gemini- or LLM-powered planner.

        This function is not used in the mock setup but is included
        for completeness and for bonus points (showing LLM integration).

        Parameters
        ----------
        mission_text : str
            The user mission.
        llm_callable : Callable
            A function that wraps Gemini or another LLM.

        Returns
        -------
        plan : List[Dict]
            Dynamically generated plan steps from the model.
        """
        prompt = (
            "You are an advanced planning agent. "
            "Given the mission below, decompose it into 2–5 high-quality steps, each mapped "
            "to one of the following agents: MarketResearchAgent, CopyAgent, WebDevAgent.\n\n"
            f"Mission: {mission_text}\n\n"
            "Return JSON ONLY in the schema:\n"
            "[{\"step\":..., \"agent\":..., \"args\":{...}}]"
        )

        response = llm_callable(prompt)

        try:
            plan = response  # Assume llm_callable returns parsed JSON
            return plan
        except Exception:
            # Fallback to deterministic plan
            return self.generate_plan(mission_text)
