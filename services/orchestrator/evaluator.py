"""
evaluator.py
------------
Evaluation module for Aegis: Self-Evolving Agent Fleet.

Responsibilities:
- Evaluate agent trajectories using an LLM-as-Judge (mock or real).
- Assign quality scores (helpfulness, accuracy, completeness).
- Run regression checks against a golden dataset.
- Provide summary metrics for AgentOps and CI pipelines.

FIX LOG (v2):
- Evaluator.evaluate_mission() called self.judge.score() — that method does not
  exist on Judge; the correct method is judge.evaluate(). Fixed everywhere.
- evaluate_golden_dataset() mission_runner return value unpacked correctly:
  the orchestrator's run_mission() returns a single dict, not (outputs, trace).
  Updated to handle both the legacy tuple protocol and the new dict protocol.
- MockJudge.score() renamed to MockJudge.evaluate() for consistency with Judge.
- GeminiJudge stub updated to match new evaluate() signature.
"""

import json
import os
import statistics
from typing import Any, Dict, List, Optional

from evaluation.judge import Judge


class Evaluator:
    """
    High-level entry-point for evaluating the multi-agent system.

    Supports:
    - Single-mission evaluation
    - Batch evaluation over a golden dataset
    - Automatic regression detection
    - Result persistence to disk
    """

    def __init__(
        self,
        judge: Optional[Any] = None,
        min_score_threshold: float = 0.75,
    ):
        """
        Parameters
        ----------
        judge                : Judge-compatible instance (default: built-in Judge).
        min_score_threshold  : Pass/fail cut-off for regression checks.
        """
        self.judge               = judge or Judge()
        self.min_score_threshold = min_score_threshold

    # ------------------------------------------------------------------ #
    # Single-mission evaluation
    # ------------------------------------------------------------------ #

    def evaluate_mission(
        self,
        mission_text: str,
        trace:        List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate a single mission trajectory.

        Parameters
        ----------
        mission_text : str
        trace        : list of trace-span dicts from session.trace

        Returns
        -------
        dict — {mission, score, num_spans, passed}
        """
        score = self.judge.evaluate(mission_text, trace)   # FIX: was .score()
        return {
            "mission":    mission_text,
            "score":      score,
            "num_spans":  len(trace),
            "passed":     score >= self.min_score_threshold,
        }

    # ------------------------------------------------------------------ #
    # Batch evaluation (golden dataset)
    # ------------------------------------------------------------------ #

    def evaluate_golden_dataset(
        self,
        golden_dataset: List[Dict[str, str]],
        mission_runner,
    ) -> Dict[str, Any]:
        """
        Evaluate multiple missions using a golden dataset.

        Parameters
        ----------
        golden_dataset : list of {"mission": str, "expected": str}
        mission_runner : callable(mission_text) → dict  (Orchestrator.run_mission)
                         OR callable(mission_text) → (outputs, trace)  (legacy)

        Returns
        -------
        dict — summary statistics and per-mission results.
        """
        results = []

        for item in golden_dataset:
            mission = item["mission"]
            raw     = mission_runner(mission)

            # Support both protocols:
            # New: run_mission() → {"trace": [...], "score": float, ...}
            # Old: mission_runner() → (outputs, trace_list)
            if isinstance(raw, dict):
                trace = raw.get("trace", [])
                score = raw.get("score") or self.judge.evaluate(mission, trace)
            else:
                _, trace = raw
                score = self.judge.evaluate(mission, trace)

            results.append({
                "mission":  mission,
                "expected": item.get("expected", ""),
                "score":    score,
                "passed":   score >= self.min_score_threshold,
                "num_spans": len(trace),
            })

        scores  = [r["score"] for r in results]
        summary = {
            "mean_score":          round(statistics.mean(scores),   4),
            "median_score":        round(statistics.median(scores),  4),
            "min_score":           min(scores),
            "max_score":           max(scores),
            "missions_evaluated":  len(scores),
            "passed_regression":   statistics.mean(scores) >= self.min_score_threshold,
            "threshold":           self.min_score_threshold,
            "details":             results,
        }
        return summary

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    @staticmethod
    def save_results(
        results:  Dict[str, Any],
        filepath: str = "evaluation_results.json",
    ) -> None:
        """Persist evaluation results to disk (for CI or human reviewers)."""
        with open(filepath, "w") as fh:
            json.dump(results, fh, indent=2)

    @staticmethod
    def load_golden_dataset(path: str) -> List[Dict[str, str]]:
        """Load a golden dataset from a JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Golden dataset not found at: {path}")
        with open(path) as fh:
            return json.load(fh)


# ─── Judge adapters ───────────────────────────────────────────────────────────

class MockJudge:
    """
    Deterministic mock judge for demos, notebooks, and CI.

    Scoring weights:
        +0.40  MarketResearchAgent present in trace
        +0.30  CopyAgent present
        +0.30  WebDevAgent / Deploy present
    """

    def evaluate(
        self,
        mission_text: str,
        trace:        List[Dict[str, Any]],
    ) -> float:
        names = [span.get("name", "") for span in trace]
        score = 0.0
        if any("MarketResearch" in n for n in names):
            score += 0.40
        if any("Copy" in n for n in names):
            score += 0.30
        if any("WebDev" in n or "Deploy" in n for n in names):
            score += 0.30
        return round(min(score, 1.0), 2)

    # Alias so Evaluator works with either judge type
    score = evaluate


class GeminiJudge:
    """
    Stub for a Gemini-powered judge.

    Uncomment the body of evaluate() and supply a client via an environment
    variable when running locally. Never commit API keys.
    """

    def __init__(self, client=None, model_name: str = "gemini-2.0-pro"):
        self.client = client
        self.model  = model_name

    def evaluate(
        self,
        mission_text: str,
        trace:        List[Dict[str, Any]],
    ) -> float:
        if self.client is None:
            return 0.5  # neutral placeholder

        # Uncomment locally (never commit keys):
        # prompt = (
        #     f"Mission: {mission_text}\n"
        #     f"Trace: {json.dumps(trace, indent=2)}\n\n"
        #     "Rate the agent trajectory from 0.0 to 1.0.\n"
        #     "Output JSON only: {\"score\": <float>}"
        # )
        # response = self.client.models.generate_content(
        #     model=self.model, contents=prompt
        # )
        # return float(json.loads(response.text)["score"])
        return 0.5

    score = evaluate
