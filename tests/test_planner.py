"""
tests/test_planner.py
---------------------
Unit tests for the Planner module.

Tests verify:
- generate_plan() / create_plan() return a well-formed plan list.
- Each step has the required "step", "agent", and "args" fields.
- Core agents appear in the default pipeline.
- Keyword-triggered steps are added when mission text contains relevant words.

FIX LOG (v2):
- Tests now import and instantiate the Planner class rather than calling a
  module-level generate_plan() function which did not exist → ImportError.
- create_plan() alias tested explicitly (the bug that broke the orchestrator).
- AnalyticsAgent added to expected agents since it is now in the default pipeline.
- Keyword routing tests added for "monitor" and "sentiment" triggers.
"""

import pytest

from services.orchestrator.planner import Planner


@pytest.fixture
def planner():
    return Planner()


# ─── Basic structure ──────────────────────────────────────────────────────────

class TestPlannerStructure:

    def test_generate_plan_returns_list(self, planner):
        plan = planner.generate_plan("Launch a campaign for Product X")
        assert isinstance(plan, list)

    def test_plan_has_minimum_steps(self, planner):
        plan = planner.generate_plan("Any mission")
        assert len(plan) >= 3

    def test_each_step_has_required_fields(self, planner):
        plan = planner.generate_plan("Campaign plan test")
        for step in plan:
            assert "step"  in step, f"Missing 'step' in {step}"
            assert "agent" in step, f"Missing 'agent' in {step}"
            assert "args"  in step, f"Missing 'args' in {step}"
            assert isinstance(step["args"], dict)

    def test_agent_names_are_strings(self, planner):
        plan = planner.generate_plan("Basic campaign")
        for step in plan:
            assert isinstance(step["agent"], str)
            assert len(step["agent"]) > 0

    def test_args_are_dicts(self, planner):
        plan = planner.generate_plan("Basic campaign")
        for step in plan:
            assert isinstance(step["args"], dict)


# ─── Core agent presence ──────────────────────────────────────────────────────

class TestDefaultPipeline:

    def test_market_research_agent_in_plan(self, planner):
        plan        = planner.generate_plan("Basic campaign")
        agent_names = [s["agent"] for s in plan]
        assert "MarketResearchAgent" in agent_names

    def test_copy_agent_in_plan(self, planner):
        plan        = planner.generate_plan("Basic campaign")
        agent_names = [s["agent"] for s in plan]
        assert "CopyAgent" in agent_names

    def test_webdev_agent_in_plan(self, planner):
        plan        = planner.generate_plan("Basic campaign")
        agent_names = [s["agent"] for s in plan]
        assert "WebDevAgent" in agent_names

    def test_analytics_agent_in_plan(self, planner):
        plan        = planner.generate_plan("Basic campaign")
        agent_names = [s["agent"] for s in plan]
        assert "AnalyticsAgent" in agent_names

    def test_research_step_has_query_arg(self, planner):
        plan         = planner.generate_plan("product mission text")
        research_step = next(s for s in plan if s["agent"] == "MarketResearchAgent")
        assert "query" in research_step["args"]

    def test_copy_step_has_brief_arg(self, planner):
        plan      = planner.generate_plan("campaign brief here")
        copy_step = next(s for s in plan if s["agent"] == "CopyAgent")
        assert "brief" in copy_step["args"]

    def test_analytics_step_has_campaign_arg(self, planner):
        plan           = planner.generate_plan("product X analytics")
        analytics_step = next(s for s in plan if s["agent"] == "AnalyticsAgent")
        assert "campaign" in analytics_step["args"]


# ─── Alias test (the bug that broke the orchestrator) ────────────────────────

class TestCreatePlanAlias:

    def test_create_plan_exists(self, planner):
        assert hasattr(planner, "create_plan"), (
            "create_plan() alias is missing — orchestrator will crash"
        )

    def test_create_plan_returns_same_as_generate(self, planner):
        mission     = "Test alias parity"
        via_generate = planner.generate_plan(mission)
        via_create   = planner.create_plan(mission)
        # Same structure, same step labels and agent names
        assert [s["step"]  for s in via_generate] == [s["step"]  for s in via_create]
        assert [s["agent"] for s in via_generate] == [s["agent"] for s in via_create]


# ─── Keyword routing ─────────────────────────────────────────────────────────

class TestKeywordRouting:

    def test_monitor_keyword_adds_step(self, planner):
        plan        = planner.generate_plan("Monitor campaign performance metrics")
        agent_names = [s["agent"] for s in plan]
        assert "MonitoringAgent" in agent_names

    def test_sentiment_keyword_adds_step(self, planner):
        plan        = planner.generate_plan("Analyse sentiment of customer reviews")
        agent_names = [s["agent"] for s in plan]
        assert "SentimentAnalysisAgent" in agent_names

    def test_no_extra_steps_for_generic_mission(self, planner):
        plan         = planner.generate_plan("Generic product launch")
        default_count = len(Planner.DEFAULT_PIPELINE)
        assert len(plan) == default_count  # no keyword triggers fired
