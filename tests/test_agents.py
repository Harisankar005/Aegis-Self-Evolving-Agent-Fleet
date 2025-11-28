import pytest
from services.agents.market_research_agent import market_research_agent
from services.agents.copy_agent import copy_agent
from services.agents.webdev_agent import webdev_agent
from services.agents.analytics_agent import analytics_agent  # if present

@pytest.fixture
def ctx():
    return {}

def test_market_research_agent(ctx):
    args = {"query": "Product X for students"}
    out = market_research_agent(args, ctx)

    assert "insights" in out
    assert isinstance(out["insights"], str)
    assert out["confidence"] > 0

def test_copy_agent(ctx):
    args = {"brief": "Launch a micro campaign"}
    out = copy_agent(args, ctx)

    assert "copy" in out
    assert isinstance(out["copy"], str)
    assert out["confidence"] > 0

def test_webdev_agent(ctx):
    args = {"brief": "Create landing page"}
    out = webdev_agent(args, ctx)

    assert "artifact" in out
    assert "url" in out["artifact"]
    assert out["confidence"] > 0

@pytest.mark.optional
def test_analytics_agent_optional(ctx):
    # Only run if this agent exists in your repo
    try:
        args = {"campaign": "Product X"}
        out = analytics_agent(args, ctx)

        assert "report" in out
        assert out["confidence"] > 0
    except ImportError:
        pytest.skip("AnalyticsAgent not available in repo")
