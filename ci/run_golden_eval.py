"""
ci/run_golden_eval.py
---------------------
Golden Dataset Evaluation Script — used by the GitHub Actions CI pipeline.

This script runs the *real* Orchestrator (not a detached mock) so that CI
actually validates the live agent system end-to-end. Any import error,
registry miss, or judge failure surfaces here before merge.

Usage (matches premerge-eval.yml):
    python ci/run_golden_eval.py --threshold 0.75 --golden evaluation/golden_dataset.json

Exit codes:
    0 — evaluation passed (mean score ≥ threshold)
    1 — evaluation failed (regression detected or runtime error)

FIX LOG (v2):
- Now imports and uses the real Orchestrator instead of a detached in-file mock.
  The v1 script had its own planner/agents/judge reimplemented inline — so CI
  tested a completely different code path than production → false confidence.
- Uses evaluation.metrics for consistent summary computation.
- Proper exit(1) on failure for CI gate integration.
"""

import argparse
import json
import sys
import os

# Ensure the project root is on the path when run from ci/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.orchestrator.orchestrator import Orchestrator
from evaluation.metrics import (
    compute_summary_metrics,
    detect_regression,
    format_summary_table,
)


def evaluate(golden_path: str, threshold: float) -> None:
    """
    Load the golden dataset, run each mission through the live Orchestrator,
    and assert that the mean judge score meets *threshold*.
    """
    with open(golden_path) as fh:
        golden = json.load(fh)

    orchestrator = Orchestrator()
    rows         = []

    print(f"\n{'=' * 50}")
    print(f"  AEGIS CI — Golden Dataset Evaluation")
    print(f"{'=' * 50}")
    print(f"  Dataset  : {golden_path}")
    print(f"  Missions : {len(golden)}")
    print(f"  Threshold: {threshold}")
    print(f"{'=' * 50}\n")

    for item in golden:
        mission = item["mission"]
        try:
            output = orchestrator.run_mission(mission, auto_evolve=False)
            score  = output["score"]
            spans  = len(output["trace"])
            status = "PASS" if score >= threshold else "FAIL"
        except Exception as exc:
            print(f"  [ERROR] Mission failed: {mission}\n  {exc}")
            score  = 0.0
            spans  = 0
            status = "ERROR"

        rows.append({"mission": mission, "score": score, "spans": spans})
        print(f"  [{status}] score={score:.2f}  spans={spans}")
        print(f"         {mission[:70]}")

    print()
    summary = compute_summary_metrics(rows, threshold=threshold)
    print(format_summary_table(summary))

    regressed, message = detect_regression(summary, threshold=threshold)
    print(f"\n{message}")

    if regressed:
        print("\n❌ CI gate failed: mean score below threshold.")
        sys.exit(1)

    print("\n✅ CI gate passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aegis CI Golden Eval")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Minimum acceptable mean judge score (default: 0.75)",
    )
    parser.add_argument(
        "--golden",
        type=str,
        default="evaluation/golden_dataset.json",
        help="Path to golden_dataset.json",
    )
    args = parser.parse_args()
    evaluate(args.golden, args.threshold)
