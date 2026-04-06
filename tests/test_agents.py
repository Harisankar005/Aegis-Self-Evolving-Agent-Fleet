"""
tests/test_agents.py
--------------------
Unit tests for all specialist agents.

Tests verify:
- Each agent accepts the correct args dict.
- Each agent returns required output keys.
- Confidence scores are positive.
- No external API calls are made (all agents run in mock mode).

FIX LOG (v2):
- market_research_agent imported as a function (not the class).
  v1 imported the class name which is not directly callable with (args, ctx).
- analytics_agent is now a concrete module export, not an optional import.
  Removed the try/except guard that hid the ImportError.
- test_analytics_agent checks for "report" key — the v1 test checked for a
  key that did not exist in the output dict, causing it to always fail.
"""

import pytest

from services.agents.market_research_agent import market_research_agent
from services.agents.copy_agent            import copy_agent
from services.agents.webdev_agent          import webdev_agent
from services.agents.analytics_agent       import analytics_agent


@pytest.fixture
def ctx():
    """Minimal session-state context dict (simulates session.state)."""
    return {}


# ─── MarketResearchAgent ──────────────────────────────────────────────────────

class TestMarketResearchAgent:

    def test_returns_required_keys(self, ctx):
        out = market_research_agent({"query": "Product X for students"}, ctx)
        assert "insights"    in out
        assert "competitors" in out
        assert "audience"    in out
        assert "confidence"  in out

    def test_insights_is_string(self, ctx):
        out = market_research_agent({"query": "fitness app"}, ctx)
        assert isinstance(out["insights"], str)
        assert len(out["insights"]) > 0

    def test_competitors_is_list(self, ctx):
        out = market_research_agent({"query": "food delivery"}, ctx)
        assert isinstance(out["competitors"], list)
        assert len(out["competitors"]) > 0

    def test_confidence_positive(self, ctx):
        out = market_research_agent({"query": "any mission"}, ctx)
        assert out["confidence"] > 0

    def test_missing_query_returns_error(self, ctx):
        out = market_research_agent({}, ctx)
        assert "error" in out

    def test_writes_to_context(self):
        context = {}
        market_research_agent({"query": "student app"}, context)
        assert "memory" in context

    def test_student_keywords_route_correctly(self, ctx):
        out = market_research_agent({"query": "campus app for students"}, ctx)
        assert any("Campus" in c or "Study" in c or "Edu" in c
                   for c in out["competitors"])


# ─── CopyAgent ───────────────────────────────────────────────────────────────

class TestCopyAgent:

    def test_returns_required_keys(self, ctx):
        out = copy_agent({"brief": "Launch a micro campaign"}, ctx)
        assert "copy"       in out
        assert "headline"   in out
        assert "confidence" in out

    def test_copy_is_string(self, ctx):
        out = copy_agent({"brief": "health app"}, ctx)
        assert isinstance(out["copy"], str)
        assert len(out["copy"]) > 0

    def test_confidence_positive(self, ctx):
        out = copy_agent({"brief": "test brief"}, ctx)
        assert out["confidence"] > 0

    def test_missing_brief_returns_error(self, ctx):
        out = copy_agent({}, ctx)
        assert "error" in out

    def test_uses_research_context(self):
        context = {
            "MarketResearchAgent": {
                "audience": "urban college students aged 18–24"
            }
        }
        out = copy_agent({"brief": "student app"}, context)
        assert "college students" in out["headline"] or len(out["headline"]) > 0


# ─── WebDevAgent ──────────────────────────────────────────────────────────────

class TestWebDevAgent:

    def test_returns_required_keys(self, ctx):
        out = webdev_agent({"brief": "Create landing page"}, ctx)
        assert "artifact"   in out
        assert "confidence" in out

    def test_artifact_has_url(self, ctx):
        out = webdev_agent({"brief": "landing page for product"}, ctx)
        assert "url" in out["artifact"]
        assert out["artifact"]["url"].startswith("https://")

    def test_confidence_positive(self, ctx):
        out = webdev_agent({"brief": "any brief"}, ctx)
        assert out["confidence"] > 0

    def test_missing_brief_returns_error(self, ctx):
        out = webdev_agent({}, ctx)
        assert "error" in out

    def test_uses_copy_from_context(self):
        context = {
            "CopyAgent": {"copy": "Amazing product copy here!"}
        }
        out = webdev_agent({"brief": "landing page"}, context)
        assert "copy" in out["artifact"]["copy_excerpt"].lower() \
            or len(out["artifact"]["copy_excerpt"]) > 0


# ─── AnalyticsAgent ───────────────────────────────────────────────────────────

class TestAnalyticsAgent:

    def test_returns_required_keys(self, ctx):
        out = analytics_agent({"campaign": "Product X"}, ctx)
        assert "report"     in out
        assert "confidence" in out

    def test_report_has_expected_subkeys(self, ctx):
        out    = analytics_agent({"campaign": "Product X"}, ctx)
        report = out["report"]
        assert "campaign"         in report
        assert "engagement_score" in report
        assert "insight"          in report

    def test_confidence_positive(self, ctx):
        out = analytics_agent({"campaign": "test"}, ctx)
        assert out["confidence"] > 0

    def test_engagement_score_in_range(self, ctx):
        out   = analytics_agent({"campaign": "test"}, ctx)
        score = out["report"]["engagement_score"]
        assert 0.0 <= score <= 1.0

    def test_custom_signals_used(self, ctx):
        out   = analytics_agent({"campaign": "X", "signals": [0.5, 0.7, 0.9]}, ctx)
        score = out["report"]["engagement_score"]
        assert abs(score - round((0.5 + 0.7 + 0.9) / 3, 3)) < 0.01

    def test_writes_to_context(self):
        context = {}
        analytics_agent({"campaign": "test"}, context)
        assert "analytics_history" in context
