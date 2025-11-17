"""
planner.py
Creates a simple plan (sequence of steps) from a mission description.
This is a simplified version of a planner agent.
"""

def generate_plan(mission_text: str):
    """
    Generate a 3-step mission plan for our marketing campaign example.
    Later, this can be replaced with an LLM-based planner.

    Returns a list of steps. Each step maps to an agent in the registry.
    """
    return [
        {
            "step": "market_research",
            "agent": "MarketResearchAgent",
            "args": {"query": mission_text}
        },
        {
            "step": "copywriting",
            "agent": "CopyAgent",
            "args": {"brief": mission_text}
        },
        {
            "step": "deployment",
            "agent": "WebDevAgent",
            "args": {"brief": mission_text}
        }
    ]
