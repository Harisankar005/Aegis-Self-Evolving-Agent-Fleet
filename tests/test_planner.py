import pytest
from services.orchestrator.planner import generate_plan

def test_generate_plan_basic():
    mission = "Launch a campaign for a smartwatch"
    plan = generate_plan(mission)

    assert isinstance(plan, list)
    assert len(plan) >= 2
    
    # Check structure
    for step in plan:
        assert "step" in step
        assert "agent" in step
        assert "args" in step


def test_generate_plan_contains_core_steps():
    mission = "Launch campaign for fitness app"
    plan = generate_plan(mission)
    
    steps = [s["agent"] for s in plan]
    assert "MarketResearchAgent" in steps
    assert "CopyAgent" in steps
