import pytest
from services.agents.market_research_agent import MarketResearchAgent
from services.agents.copy_agent import CopyAgent
from services.agents.webdev_agent import WebDevAgent

class DummyContext:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append({"name": name, "data": data})


def test_market_research_agent():
    ctx = DummyContext()
    agent = MarketResearchAgent()
    output = agent.run({"query": "smartwatch"}, ctx)
    
    assert "insights" in output
    assert isinstance(output["insights"], str)
    assert output["confidence"] > 0.5


def test_copy_agent():
    ctx = DummyContext()
    agent = CopyAgent()
    output = agent.run({"brief": "AI laptop"}, ctx)

    assert "copy" in output
    assert "AI laptop" in output["copy"]
    assert output["confidence"] >= 0.7


def test_webdev_agent():
    ctx = DummyContext()
    agent = WebDevAgent()
    output = agent.run({"brief": "Smartwatch"}, ctx)

    assert "artifact" in output
    assert "url" in output["artifact"]
    assert output["confidence"] >= 0.7
