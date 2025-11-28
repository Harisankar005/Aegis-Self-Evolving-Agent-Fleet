"""
run_eval.py

Runs bulk evaluation over the Golden Dataset using the Aegis
multi-agent orchestrator and LLM-as-Judge system.

Used by:
- GitHub Actions (ci/premerge-eval.yml)
- Local evaluation
"""

import json
import argparse
from services.evaluation.judge import Judge
from services.evaluation.metrics import compute_metrics

# Import orchestrator from core project
from services.orchestrator.orchestrator import Orchestrator

def main(golden_path: str):
    # Load dataset
    with open(golden_path) as f:
        golden = json.load(f)

    orchestrator = Orchestrator()
    judge = Judge(use_mock=True)

    all_results = []

    for item in golden:
        mission = item["mission"]
        expected = item.get("expected", "")

        out = orchestrator.run_mission(mission)
        trace = out["trace"]

        scores = judge.evaluate(mission, trace, expected)

        all_results.append({
            "mission": mission,
            **scores
        })

    metrics, df = compute_metrics(all_results)

    print("\n=== Evaluation Summary ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    # Save raw results
    df.to_csv("evaluation_results.csv", index=False)
    print("\nSaved evaluation_results.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", type=str, required=True,
        help="Path to golden_dataset.json")
    args = parser.parse_args()
    main(args.golden)
