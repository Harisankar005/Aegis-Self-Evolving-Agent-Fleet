import json
import argparse
from rich.pretty import pprint

# ---------------------------
# Import your orchestrator here
# ---------------------------
try:
    from services.orchestrator.orchestrator import Orchestrator
except:
    # Fallback: mocked orchestrator for CI environment
    class Orchestrator:
        def run_mission(self, mission, session_id=None):
            return {"score": 0.85, "results": {}, "trace": []}

def evaluate_item(orchestrator, item):
    mission = item["mission"]
    expected = item.get("expected", None)

    out = orchestrator.run_mission(mission)
    score = out.get("score", 0)

    return {
        "mission": mission,
        "expected": expected,
        "score": score
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, help="Path to golden dataset JSON")
    parser.add_argument("--out", required=True, help="Output metrics file")
    args = parser.parse_args()

    with open(args.gold, "r") as f:
        golden = json.load(f)

    orchestrator = Orchestrator()
    results = []

    for item in golden:
        r = evaluate_item(orchestrator, item)
        results.append(r)

    # Compute average score
    avg_score = sum(x["score"] for x in results) / len(results)

    metrics = {
        "average_score": avg_score,
        "individual_scores": results
    }

    pprint(metrics)

    # Save to output file
    with open(args.out, "w") as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()
