"""
metrics.py

Provides quantitative metrics for evaluating agent performance.
Used in:
- run_eval.py
- Kaggle evaluation notebook
"""

import numpy as np
import pandas as pd

def compute_metrics(results):
    """
    results = list of dict:
    {
        "mission": str,
        "overall_score": float,
        "helpfulness": float,
        "accuracy": float,
        "completeness": float,
        "safety": float
    }
    """
    df = pd.DataFrame(results)

    metrics = {
        "missions_evaluated": len(df),
        "mean_overall_score": df["overall_score"].mean(),
        "min_overall_score": df["overall_score"].min(),
        "max_overall_score": df["overall_score"].max(),
        "mean_helpfulness": df["helpfulness"].mean(),
        "mean_accuracy": df["accuracy"].mean(),
        "mean_completeness": df["completeness"].mean(),
        "mean_safety": df["safety"].mean()
    }
    return metrics, df
