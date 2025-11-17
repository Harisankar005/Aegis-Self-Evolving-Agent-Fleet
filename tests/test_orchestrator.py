import pytest
from services.orchestrator.orchestrator import Orchestrator

def test_orchestrator_runs_full_mission():
    orch = Orchestrator()
    output = orch.run_mission("Launch campaign for smartwatch")
    
    assert "results" in output
    assert "score" in output
    assert output["score"] >= 0
    
    # Core agents should have produced output
    results = output["results"]
    assert "market_research" in results
    assert "copy" in results
