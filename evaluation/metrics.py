"""
metrics.py — Evaluation metrics for Aegis.

Includes:
- Aggregate score metrics
- Minimum/maximum statistics
- Regression detection
"""

from typing import List, Dict
import numpy as np

def compute_summary_metrics(rows: List[Dict]):
    """
    rows = [
        {"mission": "...", "score": 0.85, "spans": 3},
        ...
    ]
    """
    scores = [r["score"] for r in rows]

    summary = {
        "mean_score": float(np.mean(scores)),
        "median_score": float(np.median(scores)),
        "min_score": float(np.min(scores)),
        "max_score": float(np.max(scores)),
        "missions_evaluated": len(rows),
        "scores": scores
    }

    return summary


def detect_regression(summary: Dict, threshold: float = 0.75):
    """
    Detects whether mean performance falls below threshold.

    Returns: (bool, message)
    """
    mean_score = summary["mean_score"]

    if mean_score < threshold:
        return (True, f"Regression detected: mean score {mean_score:.2f} < {threshold}")
    return (False, f"No regression: mean score {mean_score:.2f} ≥ {threshold}")
