"""
evaluation/run_eval.py
-----------------------
CLI evaluation tool for Aegis.

Runs every mission in the golden dataset through the live Orchestrator,
scores each trajectory with the Judge, computes summary metrics, and
checks for regression.

Usage:
    python evaluation/run_eval.py --gold evaluation/golden_dataset.json

Options:
    --gold       Path to golden_dataset.json        (default: evaluation/golden_dataset.json)
    --threshold  Regression fail threshold 0–1      (default: 0.75)
    --output     Path to save results JSON          (default: eval_results.json)
    --no-evolve  Disable AgentCreator during eval   (flag)

FIX LOG (v2):
- Orchestrator imported from the correct path (services.orchestrator.orchestrator).
- run_mission() output is now a dict with "score" and "trace" keys — unpacked
  correctly instead of assuming a tuple return.
- Judge imported from evaluation.judge (correct path).
- format_summary_table() called for richer CLI output.
"""

import argparse
import json
import sys

from services.orchestrator.orchestrator import Orchestrator
from evaluation.judge                   import Judge
from evaluation.metrics                 import (
    compute_summary_metrics,
    detect_regression,
    format_summary_table,
)


def run_evaluation(
    golden_path: str,
    threshold:   float = 0.75,
    output_path: str   = "eval_results.json",
    auto_evolve: bool  = True,
) -> dict:
    """
    Run the full evaluation pipeline against a golden dataset.

    Parameters
    ----------
    golden_path : str — path to golden_dataset.json.
    threshold   : float — regression detection cut-off.
    output_path : str — where to write eval_results.json.
    auto_evolve : bool — whether to allow self-evolution during eval.

    Returns
    -------
    dict — {"rows": [...], "summary": {...}}
    """
    with open(golden_path) as fh:
        golden = json.load(fh)

    orchestrator = Orchestrator()
    rows         = []

    print(f"\nRunning evaluation on {len(golden)} missions…\n" + "-" * 50)

    for item in golden:
        mission = item["mission"]
        print(f"Mission: {mission}")

        output = orchestrator.run_mission(mission, auto_evolve=auto_evolve)
        score  = output["score"]     # already computed by Judge inside orchestrator
        spans  = len(output["trace"])

        rows.append({
            "mission":  mission,
            "expected": item.get("expected", ""),
            "score":    score,
            "spans":    spans,
        })

        status = "✅" if score >= threshold else "❌"
        print(f"  Score: {score:.2f}  Spans: {spans}  {status}")
        print("-" * 50)

    summary = compute_summary_metrics(rows, threshold=threshold)

    print("\n" + format_summary_table(summary))

    regressed, message = detect_regression(summary, threshold=threshold)
    print(f"\n{message}\n")

    result = {"rows": rows, "summary": summary}

    with open(output_path, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"Results saved → {output_path}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Aegis Golden Dataset Evaluation")
    parser.add_argument(
        "--gold",
        type=str,
        default="evaluation/golden_dataset.json",
        help="Path to golden_dataset.json",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Regression detection threshold (default: 0.75)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval_results.json",
        help="Output path for results JSON",
    )
    parser.add_argument(
        "--no-evolve",
        action="store_true",
        help="Disable AgentCreator self-evolution during evaluation",
    )
    args = parser.parse_args()

    result = run_evaluation(
        golden_path=args.gold,
        threshold=args.threshold,
        output_path=args.output,
        auto_evolve=not args.no_evolve,
    )

    # Exit with non-zero code if regression detected (useful for CI)
    if not result["summary"]["passed_threshold"]:
        sys.exit(1)
