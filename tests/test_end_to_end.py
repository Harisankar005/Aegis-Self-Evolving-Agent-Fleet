import os
import pytest

from services.orchestrator.orchestrator import Orchestrator
from services.agents.market_research_agent import MarketResearchAgent
from services.agents.copy_agent import CopyAgent
from services.agents.webdev_agent import WebDevAgent


@pytest.fixture(scope="module")
def orchestrator():
    """
    Creates an orchestrator instance and registers core agents.
    Gemini API key must be available in environment variables for these tests to run.
    """
    assert "GEMINI_API_KEY" in os.environ, "GEMINI_API_KEY environment variable is required."

    orch = Orchestrator()
    orch.registry.register("MarketResearchAgent", MarketResearchAgent())
    orch.registry.register("CopyAgent", CopyAgent())
    orch.registry.register("WebDevAgent", WebDevAgent())
    return orch


def test_mission_execution(orchestrator):
    """
    Validates that the orchestrator runs a full mission and produces outputs
    from each agent in the generated plan.
    """
    mission = "Launch a campaign for a student-focused smartwatch."
    result = orchestrator.run_mission(mission)

    assert "results" in result
    assert "score" in result
    assert "trace" in result

    # Ensure output exists for all initial agents
    outputs = result["results"]
    assert "market_research" in outputs
    assert "copy" in outputs
    assert "deploy" in outputs

    # Output from each agent must include text content
    assert outputs["market_research"]["output"]
    assert outputs["copy"]["output"]
    assert outputs["deploy"]["output"]


def test_score_range(orchestrator):
    """
    Ensures judge score is always within valid [0, 1] bounds.
    """
    mission = "Create landing page and campaign for a new mobile app."
    result = orchestrator.run_mission(mission)

    score = result["score"]
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_auto_agent_creation(orchestrator):
    """
    Runs two missions: if the first mission scores low, the system should
    automatically create a new agent (e.g., AnalyticsAgent) before the second run.
    """
    mission = "Test analytics workflow for marketing insights."
    result = orchestrator.run_mission(mission)

    low_score = result["score"] < 0.75

    if low_score:
        # After a low score, an auto-generated agent should appear
        registry_list = orchestrator.registry.list()
        assert any("AnalyticsAgent" in name for name in registry_list)


def test_session_persistence(orchestrator):
    """
    Ensures session handling is consistent between runs.
    """
    mission = "Generate promotional material for a fitness tracker."
    run1 = orchestrator.run_mission(mission)
    session_id = run1["trace"][0].get("session_id") if run1["trace"] else None

    # Ensure session exists
    assert orchestrator.sessions.get_or_create(session_id)

    # Re-run with same session
    run2 = orchestrator.run_mission(mission, session_id=session_id)

    assert run2["results"]
    assert run2["trace"]
