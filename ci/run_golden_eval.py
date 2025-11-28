"""
Golden Dataset Evaluation Script
Used by GitHub Actions CI pipeline.
"""

import argparse
import json
import sys
from pathlib import Path

# ------------------------------
# Mocked agent system (safe for CI)
# ------------------------------

import time, uuid

TRACES = []

def trace_start(name):
    span = {"id": str(uuid.uuid4()), "name": name, "start": time.time(), "events": []}
    TRACES.append(span)
    return span

def trace_end(span, result):
    span["end"] = time.time()
    span["duration"] = span["end"] - span["start"]
    span["result"] = result

AGENTS = {}

def register_agent(name, func):
    AGENTS[name] = func

def call_agent(name, args):
    span = trace_start(f"call:{name}")
    res = AGENTS[name](args)
    trace_end(span, res)
    return res

# Example agents
def market_agent(args): return {"insights": f"Research for {args.get('query')}"}
def copy_agent(args): return {"copy": f"Copy for {args.get('brief')}"}
def deploy_agent(args): return {"url": "https://example.com/demo"}

# Register agents
register_agent("MarketResearch", market_agent)
register_agent("CopyWriter", copy_agent)
register_agent("WebDeployer", deploy_agent)

# Planner
def planner(mission):
    return [
        ("MarketResearch", {"query": mission}),
        ("CopyWriter", {"brief": mission}),
        ("WebDeployer", {"brief": mission})
    ]

# Mission runner
def run_mission(mission):
    global TRACES
    TRACES = []
    outputs = {}
    for name, args in planner(mission):
        outputs[name] = call_agent(name, args)
    return outputs, TRACES

# Judge scoring
def judge_score(trace):
    names = [t["name"] for t in trace]
    score = 0
    if any("MarketResearch" in n for n in names): score += 0.4
    if any("CopyWriter" in n for n in names): score += 0.3
    if any("WebDeployer" in n for n in names): score += 0.3
    return round(min(score, 1.0), 2)


# ------------------------------
# Golden set evaluation
# ------------------------------

def evaluate(golden_path, threshold):
    with open(golden_path) as f:
        golden = json.load(f)

    scores = []

    for item in golden:
        mission = item["mission"]
        _, trace = run_mission(mission)
        score = judge_score(trace)
        scores.append(score)

    mean_score = sum(scores) / len(scores)

    print(f"\nGolden Dataset Evaluated:")
    print(f"  Missions evaluated: {len(scores)}")
    print(f"  Mean judge score:   {mean_score:.2f}")
    print(f"  Threshold:          {threshold:.2f}\n")

    if mean_score < threshold:
        print("❌ Evaluation failed: Mean score below threshold.")
        sys.exit(1)
    else:
        print("✅ Evaluation passed: Mean score meets threshold.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Golden Dataset Evaluation")
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument("--golden", type=str,
                        default="evaluation/golden_dataset.json")
    args = parser.parse_args()

    evaluate(args.golden, args.threshold)
