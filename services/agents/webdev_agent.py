"""
webdev_agent.py
---------------
WebDevAgent — Specialist agent for the deployment step of a mission.

Responsibilities:
- Accept a brief and optional prior copy from the orchestrator.
- Produce a deployable artifact (mocked landing-page URL + metadata).
- Return structured output with a confidence score.

MCP handler signature:
    webdev_agent(args: dict, context: Any) -> dict

In production this would integrate with Cloud Run, GitHub Pages, or a
headless CMS. For the demo it returns a deterministic mock artifact.
"""

import time
import uuid
from typing import Any, Dict


def _build_artifact(brief: str, copy_text: str = "") -> Dict[str, Any]:
    """
    Construct a mock deployment artifact.

    In a real system this function would:
    - Render an HTML template from the copy.
    - Upload to Cloud Storage or deploy via Cloud Run.
    - Return a real public URL.
    """
    page_id = uuid.uuid4().hex[:10]
    return {
        "url":          f"https://aegis-demo.pages.dev/{page_id}",
        "type":         "landing_page",
        "title":        "Auto-Generated Marketing Page",
        "copy_excerpt": (copy_text[:120] + "…") if copy_text else "No copy provided.",
        "timestamp":    time.time(),
    }


def webdev_agent(
    args:    Dict[str, Any],
    context: Any = None,
) -> Dict[str, Any]:
    """
    Deploy a landing page artifact for the given brief.

    Parameters
    ----------
    args    : dict
        Must contain ``"brief"`` (str).
        Optional ``"copy"`` (str) — copy text to embed in the page.
    context : Any
        Session state dict. Copy is read from context["CopyAgent"] if present
        and not supplied directly in *args*.

    Returns
    -------
    dict
        {
            "artifact":   dict,
            "confidence": float,
            "agent":      str,
        }
    """
    brief = args.get("brief", "").strip()
    if not brief:
        return {"error": "Missing required field: 'brief'", "confidence": 0.0}

    # ── Pull copy from prior CopyAgent output (if available) ─────────────
    copy_text = args.get("copy", "")
    if not copy_text and isinstance(context, dict):
        copy_result = context.get("CopyAgent", {})
        copy_text   = copy_result.get("copy", "")

    artifact = _build_artifact(brief, copy_text)

    return {
        "artifact":   artifact,
        "confidence": 0.90,
        "agent":      "WebDevAgent",
    }


# ─── Agent metadata ───────────────────────────────────────────────────────────

AGENT_METADATA: Dict[str, Any] = {
    "name":        "WebDevAgent",
    "description": "Deploys a landing-page artifact from a brief and optional copy.",
    "input_schema": {
        "brief": "string — mission text or product description",
        "copy":  "string (optional) — marketing copy to embed",
    },
    "output_schema": {
        "artifact":   "dict — URL, type, title, copy_excerpt, timestamp",
        "confidence": "float",
        "agent":      "string",
    },
}
