#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Explainability for Optimus Price
Implements: Permutation Importance, SHAP Values, Partial Dependence Plots
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
import warnings
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance, partial_dependence
import shap
import joblib

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR.mkdir(exist_ok=True)
PDP_DIR = REPORTS_DIR / "partial_dependence"
PDP_DIR.mkdir(exist_ok=True)

TARGET = "avg_price_per_room"


def load_data():
    path = DATA_DIR / "processed" / "hotel_reservations_real.csv"
    if not path.exists():
        path = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
    df = pd.read_csv(path)
    leaked = [c for c in df.columns if "competitor" in c.lower()]
    if leaked:
        df = df.drop(columns=leaked)
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    return X, y


def train_model(X_train, y_train):
    """Train a GradientBoosting model for explainability."""
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, random_state=42
        )),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def permutation_importance_analysis(model, X_test, y_test, feature_names):
    """Compute permutation importance."""
    print("\n--- Permutation Importance ---")
    result = permutation_importance(
        model, X_test, y_test,
        n_repeats=10, random_state=42, n_jobs=-1
    )

    df = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std,
    }).sort_values("importance_mean", ascending=False)

    print(df.to_string(index=False))

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    top = df.head(15)
    ax.barh(range(len(top)), top["importance_mean"], xerr=top["importance_std"], capsize=3, color="#2196F3", alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["feature"])
    ax.set_xlabel("Mean Importance (RMSE decrease)")
    ax.set_title("Permutation Importance (Top 15 Features)")
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(str(REPORTS_DIR / "permutation_importance.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: permutation_importance.png")

    return df


def shap_analysis(model, X_test, feature_names):
    """Compute SHAP values."""
    print("\n--- SHAP Analysis ---")
    # Get the underlying model from pipeline
    scaler = model.named_steps["scaler"]
    ml_model = model.named_steps["model"]

    X_scaled = scaler.transform(X_test)

    # Use TreeExplainer for tree-based models
    explainer = shap.TreeExplainer(ml_model)
    shap_values = explainer.shap_values(X_scaled)

    # Summary plot
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test.values, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(str(REPORTS_DIR / "shap_summary.png"), dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: shap_summary.png")

    # Bar plot
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test.values, feature_names=feature_names, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(str(REPORTS_DIR / "shap_bar.png"), dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: shap_bar.png")

    # Mean absolute SHAP values
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    df_shap = pd.DataFrame({
        "feature": feature_names,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False)

    print(df_shap.to_string(index=False))

    # Dependence plots for top features
    top_features = df_shap.head(5)["feature"].tolist()
    for feat in top_features:
        feat_idx = feature_names.index(feat)
        fig, ax = plt.subplots(figsize=(8, 5))
        shap.dependence_plot(
            feat_idx, shap_values, X_test.values,
            feature_names=feature_names, show=False
        )
        plt.tight_layout()
        plt.savefig(str(PDP_DIR / f"shap_dependence_{feat}.png"), dpi=150, bbox_inches="tight")
        plt.close("all")
        print(f"  Saved: shap_dependence_{feat}.png")

    return df_shap


def partial_dependence_analysis(model, X_test, feature_names):
    """Compute Partial Dependence Plots."""
    print("\n--- Partial Dependence Plots ---")

    # Top features by model importance
    ml_model = model.named_steps["model"]
    importances = ml_model.feature_importances_
    top_idx = np.argsort(importances)[::-1][:6]
    top_features = [(feature_names[i], i) for i in top_idx]

    for feat_name, feat_idx in top_features:
        print(f"  Computing PDP for: {feat_name}")
        pdp_result = partial_dependence(
            model, X_test, [feat_idx],
            kind="average", grid_resolution=50
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        grid_values = pdp_result["grid_values"][0]
        avg_values = pdp_result["average"][0]

        ax.plot(grid_values, avg_values, "b-", linewidth=2)
        ax.fill_between(grid_values, avg_values, alpha=0.1, color="blue")
        ax.set_xlabel(feat_name)
        ax.set_ylabel(f"Partial Dependence (avg effect on {TARGET})")
        ax.set_title(f"Partial Dependence Plot: {feat_name}")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig.savefig(str(PDP_DIR / f"pdp_{feat_name}.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"    Saved: pdp_{feat_name}.png")

    # 2D PDP for top 2 features
    if len(top_features) >= 2:
        f1_name, f1_idx = top_features[0]
        f2_name, f2_idx = top_features[1]
        print(f"  Computing 2D PDP for: {f1_name} x {f2_name}")

        pdp_2d = partial_dependence(
            model, X_test, [f1_idx, f2_idx],
            kind="average", grid_resolution=20
        )

        fig, ax = plt.subplots(figsize=(9, 7))
        XX, YY = np.meshgrid(pdp_2d["grid_values"][0], pdp_2d["grid_values"][1])
        Z = pdp_2d["average"]

        contour = ax.contourf(XX, YY, Z, levels=20, cmap="viridis")
        plt.colorbar(contour, ax=ax, label=f"Effect on {TARGET}")
        ax.set_xlabel(f1_name)
        ax.set_ylabel(f2_name)
        ax.set_title(f"2D Partial Dependence: {f1_name} x {f2_name}")
        plt.tight_layout()
        fig.savefig(str(PDP_DIR / f"pdp_2d_{f1_name}_x_{f2_name}.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"    Saved: pdp_2d_{f1_name}_x_{f2_name}.png")


def run_explainability():
    print("=" * 60)
    print("MODEL EXPLAINABILITY ANALYSIS")
    print("=" * 60)

    X, y = load_data()
    print(f"Data: {X.shape[0]} rows, {X.shape[1]} features")

    # Split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    feature_names = list(X.columns)

    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Train model
    print("\nTraining model for explainability...")
    model = train_model(X_train, y_train)
    y_pred = model.predict(X_test)
    from sklearn.metrics import r2_score, mean_squared_error
    print(f"  R²: {r2_score(y_test, y_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

    # 1. Permutation Importance
    perm_imp = permutation_importance_analysis(model, X_test, y_test, feature_names)

    # 2. SHAP Analysis
    shap_df = shap_analysis(model, X_test, feature_names)

    # 3. Partial Dependence
    partial_dependence_analysis(model, X_test, feature_names)

    # Save summary
    summary = {
        "permutation_importance": perm_imp.to_dict(orient="records"),
        "shap_importance": shap_df.to_dict(orient="records"),
    }
    output_path = REPORTS_DIR / "explainability_summary.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary saved: {output_path}")

    return summary


if __name__ == "__main__":
    run_explainability()
