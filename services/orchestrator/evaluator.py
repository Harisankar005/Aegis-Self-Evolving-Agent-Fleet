"""
Evaluator module for Aegis: Self-Evolving Agent Fleet

This module is responsible for:
- Evaluating agent trajectories using an LLM-as-Judge (mock or real)
- Assigning quality scores (helpfulness, accuracy, completeness)
- Running regression checks using a golden dataset
- Providing summary metrics for AgentOps and CI pipelines

NOTE: This implementation is fully safe for public repos.
No API keys, credentials, or secrets should ever be included here.
"""

from typing import List, Dict, Any, Optional
import statistics
import json
import os


class Evaluator:
    """
    High-level entrypoint for evaluating the behavior of the multi-agent system.
    This class supports multiple evaluation modes:
    - Single mission evaluation
    - Batch evaluation over golden dataset
    - Automatic regression detection
    """

    def __init__(self, judge=None, min_score_threshold: float = 0.75):
        """
        judge: an instance of JudgeInterface (mock or real LLM judge)
        min_score_threshold: threshold for pass/fail regression checks
        """
        self.judge = judge
        self.min_score_threshold = min_score_threshold

    # -------------------------------------------------------------------------
    # Single Mission Evaluation
    # -------------------------------------------------------------------------
    def evaluate_mission(self, mission_text: str, trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a single mission by passing its trajectory to the LLM-as-Judge.
        """
        if not self.judge:
            raise RuntimeError("Evaluator requires a judge instance.")

        score = self.judge.score(mission_text, trace)

        return {
            "mission": mission_text,
            "score": score,
            "num_spans": len(trace)
        }

    # -------------------------------------------------------------------------
    # Batch Evaluation (Golden Dataset)
    # -------------------------------------------------------------------------
    def evaluate_golden_dataset(
        self,
        golden_dataset: List[Dict[str, str]],
        mission_runner
    ) -> Dict[str, Any]:
        """
        Evaluate multiple missions using a golden dataset.

        golden_dataset: list of dicts -> { "mission": "...", "expected": "..." }
        mission_runner: a function that accepts mission_text and returns (outputs, trace)

        Returns a summary dict.
        """
        results = []

        for item in golden_dataset:
            mission = item["mission"]

            outputs, trace = mission_runner(mission)

            # Score using LLM-as-Judge
            score = self.judge.score(mission, trace)

            results.append({
                "mission": mission,
                "expected": item.get("expected"),
                "score": score,
                "num_spans": len(trace)
            })

        # Compute metrics
        scores = [r["score"] for r in results]
        summary = {
            "mean_score": round(statistics.mean(scores), 4),
            "median_score": round(statistics.median(scores), 4),
            "min_score": min(scores),
            "max_score": max(scores),
            "missions_evaluated": len(scores),
            "passed_regression": statistics.mean(scores) >= self.min_score_threshold,
            "threshold": self.min_score_threshold,
            "details": results
        }

        return summary

    # -------------------------------------------------------------------------
    # Utility — Save Evaluation Output
    # -------------------------------------------------------------------------
    @staticmethod
    def save_results(results: Dict[str, Any], filepath: str = "evaluation_results.json"):
        """
        Saves evaluation results to disk (for CI or human reviewers).
        """
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

    # -------------------------------------------------------------------------
    # Utility — Load Golden Dataset from Path
    # -------------------------------------------------------------------------
    @staticmethod
    def load_golden_dataset(path: str) -> List[Dict[str, str]]:
        """
        Load golden dataset from a JSON file.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Golden dataset not found at {path}")

        with open(path) as f:
            return json.load(f)


# -----------------------------------------------------------------------------
# JudgeInterface (Adaptable for Mock or Real LLM)
# -----------------------------------------------------------------------------

class JudgeInterface:
    """
    Interface for judge modules. Ensures both mock and real judges
    implement the same scoring API.
    """
    def score(self, mission_text: str, trace: List[Dict[str, Any]]) -> float:
        raise NotImplementedError


# -----------------------------------------------------------------------------
# MockJudge — safe for public demos & Kaggle notebooks
# -----------------------------------------------------------------------------

class MockJudge(JudgeInterface):
    """
    A deterministic, safe mock evaluator used for:
    - Kaggle submissions
    - GitHub repos
    - Testing without API keys

    The scoring heuristic:
    +0.4 if MarketResearch agent appears
    +0.3 if Copy agent appears
    +0.3 if WebDev/Deploy agent appears
    Capped at 1.0
    """

    def score(self, mission_text: str, trace: List[Dict[str, Any]]) -> float:
        agent_names = [span["name"] for span in trace]
        score = 0.0

        if any("MarketResearch" in n for n in agent_names):
            score += 0.4
        if any("Copy" in n for n in agent_names):
            score += 0.3
        if any("WebDev" in n or "Deploy" in n for n in agent_names):
            score += 0.3

        return round(min(score, 1.0), 2)


# -----------------------------------------------------------------------------
# Stub for Real Gemini Judge (Optional Bonus Points)
# -----------------------------------------------------------------------------

class GeminiJudge(JudgeInterface):
    """
    This judge uses Gemini to evaluate trajectories.

    Safe for public repos: API call is left commented out.
    The developer can uncomment locally and add API keys via environment variables.
    """

    def __init__(self, client=None, model_name="gemini-2.0-pro"):
        self.client = client
        self.model = model_name

    def score(self, mission_text: str, trace: List[Dict[str, Any]]) -> float:
        """
        Scoring prompt (conceptual):
        Ask Gemini to rate the agent’s trajectory on:
        - Helpfulness
        - Accuracy
        - Completeness
        - Safety

        Return an overall score between 0 and 1.
        """

        # ------------------------
        # REAL GEMINI CALL (safe)
        # ------------------------
        # Uncomment in private, NEVER in public repos:
        #
        # prompt = f"""
        # Mission: {mission_text}
        # Trace: {json.dumps(trace, indent=2)}
        #
        # Rate the trajectory from 0 to 1 on overall effectiveness.
        # Only output a JSON: {{"score": <float>}}
        # """
        #
        # response = self.client.models.generate_content(
        #     model=self.model,
        #     contents=prompt
        # )
        #
        # parsed = json.loads(response.candidates[0].content.parts[0].text)
        # return float(parsed["score"])

        # --- Fallback for public safety ---
        return 0.5  # Neutral placeholder score
