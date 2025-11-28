"""
run_eval.py — CLI evaluation tool for Aegis.

Usage:
    python evaluation/run_eval.py --gold evaluation/golden_dataset.json
"""

import json
import argparse
from evaluation.judge import Judge
from evaluation.metrics import compute_summary_metrics, detect_regression

# Import orchestrator (update path according to your repo structure)
from services.orchestrator.orchestrator import Orchestrator


def run_evaluation(golden_path: str):
    # Load golden dataset
    with open(golden_path, "r") as f:
        golden = json.load(f)

    orchestrator = Orchestrator()
    judge = Judge()

    rows = []

    for item in golden:
        mission = item["mission"]

        # Run mission through orchestrator
        output = orchestrator.run_mission(mission)
        score = output["score"]

        rows.append({
            "mission": mission,
            "score": score,
            "spans": len(output["trace"])
        })

        print(f"Mission: {mission}")
        print(f"Score: {score}")
        print("-" * 50)

    # Compute summary
    summary = compute_summary_metrics(rows)
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))

    # Regression detection
    regressed, message = detect_regression(summary)
    print("\n=== REGRESSION CHECK ===")
    print(message)

    # Save results
    with open("eval_results.json", "w") as f:
        json.dump({"rows": rows, "summary": summary}, f, indent=2)

    print("\nSaved results → eval_results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=str, required=True,
                        help="Path to golden_dataset.json")
    args = parser.parse_args()

    run_evaluation(args.gold)
