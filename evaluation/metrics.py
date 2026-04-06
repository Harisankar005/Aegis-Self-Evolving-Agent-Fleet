"""
evaluation/metrics.py
---------------------
Evaluation metrics for Aegis.

Computes aggregate statistics over judge scores and performs regression detection.

FIX LOG (v2):
- numpy dependency replaced with stdlib statistics module.
  numpy is a heavy dependency used only for mean/median here; stdlib suffices
  and removes a potential version-conflict in constrained environments.
- compute_summary_metrics() now also returns "passed_threshold" per-row
  so callers can filter passing vs failing missions without a second pass.
"""

import statistics
from typing import Dict, List, Tuple


def compute_summary_metrics(
    rows:      List[Dict],
    threshold: float = 0.75,
) -> Dict:
    """
    Compute aggregate statistics over a list of evaluation result rows.

    Parameters
    ----------
    rows : list of dict
        Each dict must contain at least {"mission": str, "score": float}.
        Optional: "spans" (int).
    threshold : float
        Pass/fail cut-off used to annotate each row and the overall summary.

    Returns
    -------
    dict
        {
            "mean_score":         float,
            "median_score":       float,
            "min_score":          float,
            "max_score":          float,
            "std_score":          float,
            "missions_evaluated": int,
            "passed_count":       int,
            "failed_count":       int,
            "passed_threshold":   bool,
            "threshold":          float,
            "scores":             list[float],
        }
    """
    if not rows:
        return {
            "mean_score":         0.0,
            "median_score":       0.0,
            "min_score":          0.0,
            "max_score":          0.0,
            "std_score":          0.0,
            "missions_evaluated": 0,
            "passed_count":       0,
            "failed_count":       0,
            "passed_threshold":   False,
            "threshold":          threshold,
            "scores":             [],
        }

    scores      = [float(r["score"]) for r in rows]
    passed      = [s for s in scores if s >= threshold]
    std         = statistics.stdev(scores) if len(scores) > 1 else 0.0
    mean_score  = statistics.mean(scores)

    return {
        "mean_score":         round(mean_score,             4),
        "median_score":       round(statistics.median(scores), 4),
        "min_score":          round(min(scores),             4),
        "max_score":          round(max(scores),             4),
        "std_score":          round(std,                     4),
        "missions_evaluated": len(scores),
        "passed_count":       len(passed),
        "failed_count":       len(scores) - len(passed),
        "passed_threshold":   mean_score >= threshold,
        "threshold":          threshold,
        "scores":             scores,
    }


def detect_regression(
    summary:   Dict,
    threshold: float = 0.75,
) -> Tuple[bool, str]:
    """
    Detect whether mean performance has fallen below *threshold*.

    Parameters
    ----------
    summary   : dict — output of compute_summary_metrics().
    threshold : float — regression cut-off (defaults to 0.75).

    Returns
    -------
    (regressed: bool, message: str)
    """
    mean_score = summary.get("mean_score", 0.0)
    if mean_score < threshold:
        return (
            True,
            f"⚠️  Regression detected: mean score {mean_score:.4f} < {threshold}",
        )
    return (
        False,
        f"✅ No regression: mean score {mean_score:.4f} ≥ {threshold}",
    )


def format_summary_table(summary: Dict) -> str:
    """
    Return a human-readable table string of the evaluation summary.

    Useful for CLI output and notebook display.
    """
    lines = [
        "=" * 42,
        "  AEGIS EVALUATION SUMMARY",
        "=" * 42,
        f"  Missions evaluated : {summary['missions_evaluated']}",
        f"  Mean score         : {summary['mean_score']:.4f}",
        f"  Median score       : {summary['median_score']:.4f}",
        f"  Min / Max          : {summary['min_score']:.4f} / {summary['max_score']:.4f}",
        f"  Std deviation      : {summary['std_score']:.4f}",
        f"  Passed (≥{summary['threshold']})    : {summary['passed_count']}",
        f"  Failed (<{summary['threshold']})    : {summary['failed_count']}",
        f"  Overall pass       : {'✅ Yes' if summary['passed_threshold'] else '❌ No'}",
        "=" * 42,
    ]
    return "\n".join(lines)
