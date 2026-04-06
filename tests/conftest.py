import pytest

def test_planner_generates_plan(planner, sample_task):
    plan = planner.create_plan(sample_task)

    assert isinstance(plan, list)
    assert len(plan) > 0

    for step in plan:
        assert "agent" in step
        assert "action" in step or "step" in step


def test_planner_no_cycles(planner, sample_task):
    plan = planner.create_plan(sample_task)

    seen = set()
    for step in plan:
        identifier = step.get("step")
        assert identifier not in seen, "Cycle detected in plan"
        seen.add(identifier)


def test_planner_handles_empty_input(planner):
    with pytest.raises(Exception):
        planner.create_plan({})
