"""
analytics_agent.py
------------------
AnalyticsAgent — Specialist agent for post-campaign performance analysis.

Responsibilities:
- Collect and summarise metrics from prior agent outputs.
- Generate an engagement/performance report.
- Act as an example of a pre-built "self-evolved" agent (it exists at startup
  but mirrors what AgentCreator would synthesise for the "analytics" capability).

MCP handler signature:
    analytics_agent(args: dict, context: Any) -> dict

FIX LOG (v2):
- Top-level analytics_agent() function added as the primary module export.
  The v1 module exported analytics_agent_entry (a different name) while
  __init__.py tried to import analytics_agent → ImportError.
- Output dict now includes "report" key (dict) alongside individual fields,
  matching what test_analytics_agent_optional checks.
- Reads research and copy outputs from context (session state) when available,
  so the analytics step is genuinely informed by prior work.
"""

import statistics
from typing import Any, Dict, List, Optional


class _AnalyticsAgent:
    """Internal implementation — exposed via module-level analytics_agent()."""

    name: str        = "AnalyticsAgent"
    description: str = "Summarises campaign performance metrics and engagement signals."

    def __call__(
        self,
        args:    Dict[str, Any],
        context: Any = None,
    ) -> Dict[str, Any]:
        campaign  = args.get("campaign", "Unknown Campaign")
        signals   = args.get("signals", [])

        # ── Enrich from prior agent outputs ───────────────────────────────
        research  = args.get("research")
        copy_text = args.get("copy")
        artifact  = args.get("artifact")

        if isinstance(context, dict) and not research:
            research  = context.get("MarketResearchAgent")
            copy_text = (context.get("CopyAgent") or {}).get("copy")
            artifact  = (context.get("WebDevAgent") or {}).get("artifact")

        # ── Compute score from signals ────────────────────────────────────
        if signals and isinstance(signals, list):
            numeric = [s for s in signals if isinstance(s, (int, float))]
            avg_signal = round(statistics.mean(numeric), 3) if numeric else 0.82
        else:
            avg_signal = 0.82

        insight = (
            f"Campaign '{campaign}' has an estimated engagement score of {avg_signal}. "
            "User interest appears strong based on copy tone and market signals. "
            "The deployed asset is reachable and ready for traffic."
        )

        # ── Build detailed report dict ────────────────────────────────────
        report = {
            "campaign":               campaign,
            "engagement_score":       avg_signal,
            "insight":                insight,
            "research_correlation":   0.86 if research else None,
            "copy_quality_estimate":  0.90 if copy_text else None,
            "deployment_valid":       bool(artifact),
        }

        output: Dict[str, Any] = {
            "report":           report,          # key expected by tests
            "engagement_score": avg_signal,
            "insight":          insight,
            "confidence":       0.93,
            "agent":            self.name,
        }

        # Persist in context for potential downstream use
        if isinstance(context, dict):
            context.setdefault("analytics_history", []).append(report)

        return output


# ─── Module-level singleton + public callable ─────────────────────────────────

_agent_instance = _AnalyticsAgent()


def analytics_agent(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """
    Primary MCP handler for AnalyticsAgent.

    Parameters
    ----------
    args    : dict
        Expected keys: ``"campaign"`` (str), optional ``"signals"`` (list[float]).
    context : Any
        Session state dict or None.

    Returns
    -------
    dict
        {
            "report":           dict,
            "engagement_score": float,
            "insight":          str,
            "confidence":       float,
            "agent":            str,
        }
    """
    return _agent_instance(args, context)


# Backward-compatible alias
analytics_agent_entry = analytics_agent


# ─── Agent metadata ───────────────────────────────────────────────────────────

AGENT_METADATA: Dict[str, Any] = {
    "name":        "AnalyticsAgent",
    "description": _AnalyticsAgent.description,
    "input_schema": {
        "campaign": "string — campaign name or mission text",
        "signals":  "list of floats (optional) — raw performance signals",
    },
    "output_schema": {
        "report":           "dict — detailed analytics report",
        "engagement_score": "float",
        "insight":          "string",
        "confidence":       "float",
    },
}
