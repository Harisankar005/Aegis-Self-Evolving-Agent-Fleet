import pytest
from services.orchestrator.planner import generate_plan

def test_plan_structure():
    mission = "Launch a campaign for Product X"
    plan = generate_plan(mission)

    assert isinstance(plan, list)
    assert len(plan) >= 3

def test_plan_fields():
    mission = "Campaign plan test"
    plan = generate_plan(mission)

    for step in plan:
        assert "step" in step
        assert "agent" in step
        assert "args" in step
        assert isinstance(step["args"], dict)

def test_agent_names_in_plan():
    mission = "Basic campaign"
    plan = generate_plan(mission)

    agent_names = [s["agent"] for s in plan]
    assert "MarketResearchAgent" in agent_names
    assert "CopyAgent" in agent_names
    assert "WebDevAgent" in agent_names
