"""
copy_agent.py
-------------
CopyAgent — Specialist agent for marketing copywriting.

Responsibilities:
- Accept a brief or mission text from the orchestrator.
- Generate headline copy, taglines, and body text (mocked by default).
- Return structured output with confidence score.

MCP handler signature:
    copy_agent(args: dict, context: Any) -> dict

In production, replace the mock generation block with a Gemini API call.
"""

from typing import Any, Dict


def copy_agent(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """
    Generate marketing copy for a given brief.

    Parameters
    ----------
    args    : dict
        Must contain ``"brief"`` (str) — the mission or product description.
        Optional ``"style"`` (str) — e.g. "formal", "playful", "concise".
    context : Any
        Session state dict (may be None). Prior research insights are
        read from context["MarketResearchAgent"] if available.

    Returns
    -------
    dict
        {
            "copy":       str,
            "headline":   str,
            "style":      str,
            "confidence": float,
        }
    """
    # ── Input validation ──────────────────────────────────────────────────
    brief = args.get("brief", "").strip()
    if not brief:
        return {"error": "Missing required field: 'brief'", "confidence": 0.0}

    style = args.get("style", "concise")

    # ── Optional: enrich copy using prior research ────────────────────────
    audience_hint = ""
    if isinstance(context, dict):
        research = context.get("MarketResearchAgent", {})
        if research:
            audience_hint = research.get("audience", "")

    audience_line = f" — tailored for {audience_hint}" if audience_hint else ""

    # ── Mock copy generation ──────────────────────────────────────────────
    # Replace this block with a real Gemini call in production:
    #
    #   response = client.models.generate_content(
    #       model="gemini-2.0-pro",
    #       contents=f"Write a concise marketing headline for: {brief}"
    #   )
    #   headline = response.text.strip()

    headline = f"Unlock the Future with Aegis{audience_line}"
    body = (
        f"Introducing a smarter way to achieve: {brief}. "
        "Powered by AI-driven insights and expert execution, "
        "Aegis helps you move faster, reach further, and grow smarter. "
        "Ready to launch? Let's go."
    )

    return {
        "copy":       body,
        "headline":   headline,
        "style":      style,
        "confidence": 0.92,
        "agent":      "CopyAgent",
    }


# ─── Agent metadata ───────────────────────────────────────────────────────────

AGENT_METADATA: Dict[str, Any] = {
    "name":        "CopyAgent",
    "description": "Generates creative marketing copy for a given brief.",
    "input_schema": {
        "brief": "string — mission text or product brief",
        "style": "string (optional) — writing style hint",
    },
    "output_schema": {
        "copy":       "string — full body copy",
        "headline":   "string — short headline",
        "style":      "string",
        "confidence": "float",
    },
}
