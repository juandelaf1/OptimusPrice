#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Space Analysis for Optimus Price
Identifies: correlations, leakage candidates, low-information variables
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def load_data():
    """Load both raw and clean datasets."""
    paths = {
        "real": DATA_DIR / "processed" / "hotel_reservations_real.csv",
        "clean": DATA_DIR / "processed" / "hotel_reservations_clean.csv",
    }
    datasets = {}
    for name, path in paths.items():
        if path.exists():
            datasets[name] = pd.read_csv(path)
            print(f"  {name}: {datasets[name].shape[0]} rows, {datasets[name].shape[1]} cols")
        else:
            print(f"  {name}: NOT FOUND at {path}")
    return datasets


def analyze_correlations(df, target="avg_price_per_room"):
    """Find highly correlated feature pairs."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr_matrix = df[numeric_cols].corr()

    # Get upper triangle (exclude self-correlations)
    pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            r = corr_matrix.iloc[i, j]
            pairs.append({
                "feature_a": numeric_cols[i],
                "feature_b": numeric_cols[j],
                "correlation": round(float(r), 4),
                "abs_correlation": round(float(abs(r)), 4),
            })

    pairs.sort(key=lambda x: x["abs_correlation"], reverse=True)

    # High correlation pairs (|r| > 0.7)
    high_corr = [p for p in pairs if p["abs_correlation"] > 0.7]

    # Target correlations
    target_corr = []
    if target in corr_matrix.columns:
        for col in numeric_cols:
            if col != target:
                r = corr_matrix.loc[col, target]
                target_corr.append({
                    "feature": col,
                    "correlation_with_target": round(float(r), 4),
                    "abs_correlation": round(float(abs(r)), 4),
                })
        target_corr.sort(key=lambda x: x["abs_correlation"], reverse=True)

    return {
        "high_correlation_pairs": high_corr,
        "target_correlations": target_corr,
        "total_pairs": len(pairs),
        "high_corr_count": len(high_corr),
    }


def analyze_leakage(df, target="avg_price_per_room"):
    """Identify potential leakage candidates."""
    if target not in df.columns:
        return {"error": f"Target '{target}' not found"}

    y = df[target]
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target]

    leakage = []
    for col in numeric_cols:
        r = abs(df[col].corr(y))
        if r > 0.9:
            leakage.append({
                "feature": col,
                "abs_correlation": round(float(r), 4),
                "verdict": "HIGH_LEAKAGE_RISK",
            })
        elif r > 0.7:
            leakage.append({
                "feature": col,
                "abs_correlation": round(float(r), 4),
                "verdict": "MODERATE_LEAKAGE_RISK",
            })

    # Check for target-encoded columns
    target衍生 = [c for c in df.columns if target.replace("_", "") in c.lower().replace("_", "")]
    if target衍生:
        for col in target衍生:
            if col not in [l["feature"] for l in leakage]:
                leakage.append({
                    "feature": col,
                    "abs_correlation": None,
                    "verdict": "TARGET_NAME_MATCH",
                })

    return {
        "leakage_candidates": leakage,
        "total_features_checked": len(numeric_cols),
    }


def analyze_low_information(df, target="avg_price_per_room"):
    """Identify low-information variables."""
    results = []
    for col in df.columns:
        if col == target:
            continue

        nunique = df[col].nunique()
        total = len(df)
        missing_pct = df[col].isna().mean() * 100

        # Variance (only for numeric)
        if df[col].dtype in [np.float64, np.int64]:
            var = df[col].var()
            # Normalize variance by mean
            mean_val = df[col].mean()
            cv = np.std(df[col]) / mean_val if mean_val != 0 else 0
        else:
            var = None
            cv = None

        # One-value dominance
        top_pct = df[col].value_counts(normalize=True).iloc[0] * 100 if nunique > 0 else 100

        # Flag low information
        flags = []
        if nunique <= 1:
            flags.append("CONSTANT")
        if nunique == 2:
            flags.append("BINARY")
        if top_pct > 99:
            flags.append("NEAR_CONSTANT")
        if missing_pct > 50:
            flags.append("HIGH_MISSING")
        if cv is not None and cv < 0.01 and nunique > 2:
            flags.append("LOW_VARIANCE")

        results.append({
            "feature": col,
            "dtype": str(df[col].dtype),
            "nunique": int(nunique),
            "missing_pct": round(float(missing_pct), 2),
            "top_value_pct": round(float(top_pct), 2),
            "variance": round(float(var), 4) if var is not None else None,
            "cv": round(float(cv), 4) if cv is not None else None,
            "flags": flags,
        })

    results.sort(key=lambda x: len(x["flags"]), reverse=True)
    flagged = [r for r in results if r["flags"]]

    return {
        "all_features": results,
        "flagged_features": flagged,
        "total_flagged": len(flagged),
    }


def plot_correlation_matrix(df, target="avg_price_per_room", save_path=None):
    """Plot correlation heatmap."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Limit to 20 features for readability
    if len(numeric_cols) > 20:
        target_corr = df[numeric_cols].corr()[target].abs().sort_values(ascending=False)
        numeric_cols = target_corr.head(20).index.tolist()

    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(numeric_cols, fontsize=8)
    plt.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Feature Correlation Matrix (Top 20 by target correlation)")
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def run_analysis():
    print("=" * 60)
    print("FEATURE SPACE ANALYSIS")
    print("=" * 60)

    datasets = load_data()
    all_results = {}

    for name, df in datasets.items():
        print(f"\n--- {name.upper()} dataset ---")
        results = {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        }

        # Correlations
        print("  Computing correlations...")
        results["correlations"] = analyze_correlations(df)

        # Leakage
        print("  Checking leakage...")
        results["leakage"] = analyze_leakage(df)

        # Low information
        print("  Analyzing feature information...")
        results["low_information"] = analyze_low_information(df)

        # Summary
        hc = results["correlations"]["high_corr_count"]
        lk = len(results["leakage"]["leakage_candidates"])
        li = results["low_information"]["total_flagged"]
        print(f"  High correlation pairs: {hc}")
        print(f"  Leakage candidates: {lk}")
        print(f"  Low-information features: {li}")

        all_results[name] = results

        # Plot correlation matrix
        plot_correlation_matrix(
            df,
            save_path=str(REPORTS_DIR / f"correlation_matrix_{name}.png"),
        )

    # Save results
    output_path = REPORTS_DIR / "feature_analysis.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, r in all_results.items():
        print(f"\n{name.upper()}:")
        hc = r["correlations"]["high_corr_count"]
        lk = len(r["leakage"]["leakage_candidates"])
        li = r["low_information"]["total_flagged"]
        print(f"  High correlation pairs (>0.7): {hc}")
        print(f"  Leakage candidates: {lk}")
        print(f"  Low-information features: {li}")

        if r["leakage"]["leakage_candidates"]:
            print("  Top leakage candidates:")
            for l in r["leakage"]["leakage_candidates"][:5]:
                print(f"    {l['feature']}: {l['verdict']} (r={l['abs_correlation']})")

        if r["low_information"]["flagged_features"]:
            print("  Flagged features:")
            for f in r["low_information"]["flagged_features"][:5]:
                print(f"    {f['feature']}: {', '.join(f['flags'])}")


if __name__ == "__main__":
    run_analysis()
