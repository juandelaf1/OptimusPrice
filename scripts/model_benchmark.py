#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Benchmark for Optimus Price
Compares: GradientBoosting, RandomForest, XGBoost, LightGBM, CatBoost, ElasticNet
Metrics: R², MAE, RMSE, MAPE
Validation: TimeSeriesSplit, Holdout, Rolling Window
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import time
import os
import warnings
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR.mkdir(exist_ok=True)

TARGET = "avg_price_per_room"


def load_data():
    """Load real data (117K rows)."""
    path = DATA_DIR / "processed" / "hotel_reservations_real.csv"
    if not path.exists():
        path = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
    print(f"Loading: {path}")
    df = pd.read_csv(path)

    # Remove leaked features
    leaked = [c for c in df.columns if "competitor" in c.lower()]
    if leaked:
        df = df.drop(columns=leaked)
        print(f"  Removed leaked features: {leaked}")

    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    print(f"  Features: {X.shape[1]}, Rows: {len(X)}")
    print(f"  Target: mean={y.mean():.2f}, std={y.std():.2f}, range=[{y.min():.2f}, {y.max():.2f}]")
    return X, y


def temporal_split(X, y, test_size=0.2):
    split_idx = int(len(X) * (1 - test_size))
    return X.iloc[:split_idx], X.iloc[split_idx:], y.iloc[:split_idx], y.iloc[split_idx:]


def evaluate(y_true, y_pred):
    return {
        "r2": round(float(r2_score(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2),
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 2),
        "mape": round(float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100), 2),
    }


def build_model(name):
    models = {
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, random_state=42
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=200, max_depth=15, min_samples_leaf=5,
            min_samples_split=10, random_state=42, n_jobs=-1
        ),
        "ElasticNet": ElasticNet(
            alpha=0.1, l1_ratio=0.5, max_iter=5000, random_state=42
        ),
    }

    try:
        import xgboost as xgb
        models["XGBoost"] = xgb.XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            verbosity=0
        )
    except ImportError:
        print("  XGBoost not installed, skipping")

    try:
        import lightgbm as lgb
        models["LightGBM"] = lgb.LGBMRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbose=-1
        )
    except ImportError:
        print("  LightGBM not installed, skipping")

    try:
        from catboost import CatBoostRegressor
        models["CatBoost"] = CatBoostRegressor(
            iterations=200, depth=6, learning_rate=0.08,
            random_seed=42, verbose=0
        )
    except ImportError:
        print("  CatBoost not installed, skipping")

    return models.get(name)


def time_series_cv(X, y, model_fn, n_splits=5):
    """TimeSeriesSplit cross-validation."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = {"r2": [], "rmse": [], "mae": [], "mape": []}

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("model", model_fn()),
        ])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_val)

        scores["r2"].append(r2_score(y_val, y_pred))
        scores["rmse"].append(np.sqrt(mean_squared_error(y_val, y_pred)))
        scores["mae"].append(mean_absolute_error(y_val, y_pred))
        scores["mape"].append(np.mean(np.abs((y_val - y_pred) / y_val)) * 100)

    return {
        "cv_r2_mean": round(float(np.mean(scores["r2"])), 4),
        "cv_r2_std": round(float(np.std(scores["r2"])), 4),
        "cv_rmse_mean": round(float(np.mean(scores["rmse"])), 2),
        "cv_rmse_std": round(float(np.std(scores["rmse"])), 2),
        "cv_mae_mean": round(float(np.mean(scores["mae"])), 2),
        "cv_mae_std": round(float(np.std(scores["mae"])), 2),
        "cv_mape_mean": round(float(np.mean(scores["mape"])), 2),
        "cv_mape_std": round(float(np.std(scores["mape"])), 2),
    }


def rolling_window_cv(X, y, model_fn, window_pct=0.6, step_pct=0.1, n_windows=5):
    """Rolling window validation."""
    n = len(X)
    window_size = int(n * window_pct)
    step_size = int(n * step_pct)
    scores = {"r2": [], "rmse": [], "mae": [], "mape": []}

    for i in range(n_windows):
        train_end = window_size + i * step_size
        test_end = train_end + int(n * 0.1)

        if test_end > n:
            break

        X_tr = X.iloc[:train_end]
        y_tr = y.iloc[:train_end]
        X_te = X.iloc[train_end:test_end]
        y_te = y.iloc[train_end:test_end]

        if len(X_te) == 0:
            break

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("model", model_fn()),
        ])
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)

        scores["r2"].append(r2_score(y_te, y_pred))
        scores["rmse"].append(np.sqrt(mean_squared_error(y_te, y_pred)))
        scores["mae"].append(mean_absolute_error(y_te, y_pred))
        scores["mape"].append(np.mean(np.abs((y_te - y_pred) / y_te)) * 100)

    if not scores["r2"]:
        return None

    return {
        "rolling_r2_mean": round(float(np.mean(scores["r2"])), 4),
        "rolling_r2_std": round(float(np.std(scores["r2"])), 4),
        "rolling_rmse_mean": round(float(np.mean(scores["rmse"])), 2),
        "rolling_rmse_std": round(float(np.std(scores["rmse"])), 2),
        "rolling_mae_mean": round(float(np.mean(scores["mae"])), 2),
        "rolling_mape_mean": round(float(np.mean(scores["mape"])), 2),
        "n_windows": len(scores["r2"]),
    }


def plot_benchmark(results, save_path=None):
    """Plot benchmark comparison."""
    names = list(results.keys())
    metrics = ["r2", "rmse", "mae", "mape"]
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))

    colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0", "#00BCD4"]

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        values = [results[n]["holdout"][metric] for n in names]
        bars = ax.bar(names, values, color=colors[:len(names)])
        ax.set_title(metric.upper(), fontsize=12, fontweight="bold")
        ax.set_ylabel(metric.upper())

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:.2f}" if metric != "r2" else f"{val:.4f}",
                ha="center", va="bottom", fontsize=9
            )

        ax.tick_params(axis="x", rotation=45)

    plt.suptitle("Model Benchmark Comparison (Holdout Test Set)", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_cv_comparison(results, save_path=None):
    """Plot cross-validation comparison."""
    names = list(results.keys())
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # R2 comparison
    ax = axes[0]
    r2_means = [results[n]["cv"]["cv_r2_mean"] for n in names]
    r2_stds = [results[n]["cv"]["cv_r2_std"] for n in names]
    ax.barh(names, r2_means, xerr=r2_stds, capsize=5, color="#2196F3", alpha=0.8)
    ax.set_xlabel("R²")
    ax.set_title("TimeSeriesSplit CV - R²")

    # RMSE comparison
    ax = axes[1]
    rmse_means = [results[n]["cv"]["cv_rmse_mean"] for n in names]
    rmse_stds = [results[n]["cv"]["cv_rmse_std"] for n in names]
    ax.barh(names, rmse_means, xerr=rmse_stds, capsize=5, color="#F44336", alpha=0.8)
    ax.set_xlabel("RMSE")
    ax.set_title("TimeSeriesSplit CV - RMSE")

    plt.suptitle("Cross-Validation Comparison (5-fold TimeSeriesSplit)", fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def run_benchmark():
    print("=" * 60)
    print("MODEL BENCHMARK")
    print("=" * 60)

    X, y = load_data()
    X_train, X_test, y_train, y_test = temporal_split(X, y)
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    model_names = ["GradientBoosting", "RandomForest", "XGBoost", "LightGBM", "CatBoost", "ElasticNet"]
    all_results = {}

    for name in model_names:
        model_fn = build_model(name)
        if model_fn is None:
            continue

        print(f"\n{'='*40}")
        print(f"Training: {name}")
        print(f"{'='*40}")

        # Holdout evaluation
        t0 = time.time()
        pipe = Pipeline([("scaler", StandardScaler()), ("model", model_fn)])
        pipe.fit(X_train, y_train)
        train_time = round(time.time() - t0, 2)

        y_pred = pipe.predict(X_test)
        holdout = evaluate(y_test, y_pred)
        holdout["train_time_sec"] = train_time
        print(f"  Holdout: R2={holdout['r2']}, RMSE={holdout['rmse']}, MAE={holdout['mae']}, MAPE={holdout['mape']}%")
        print(f"  Train time: {train_time}s")

        # TimeSeriesSplit CV
        print("  Running TimeSeriesSplit CV...")
        cv = time_series_cv(X_train, y_train, lambda: build_model(name))
        print(f"  CV: R2={cv['cv_r2_mean']}+/-{cv['cv_r2_std']}, RMSE={cv['cv_rmse_mean']}+/-{cv['cv_rmse_std']}")

        # Rolling window
        print("  Running rolling window CV...")
        rolling = rolling_window_cv(X_train, y_train, lambda: build_model(name))
        if rolling:
            print(f"  Rolling: R2={rolling['rolling_r2_mean']}+/-{rolling['rolling_r2_std']}")

        all_results[name] = {
            "holdout": holdout,
            "cv": cv,
            "rolling": rolling,
        }

    # Save results
    output_path = REPORTS_DIR / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {output_path}")

    # Plot comparisons
    if all_results:
        plot_benchmark(all_results, save_path=str(REPORTS_DIR / "benchmark_holdout.png"))
        plot_cv_comparison(all_results, save_path=str(REPORTS_DIR / "benchmark_cv.png"))

    # Summary table
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY (sorted by RMSE)")
    print("=" * 80)
    print(f"{'Model':<20} {'R²':>8} {'RMSE':>8} {'MAE':>8} {'MAPE%':>8} {'CV R²':>10} {'Time':>8}")
    print("-" * 80)

    sorted_models = sorted(all_results.items(), key=lambda x: x[1]["holdout"]["rmse"])
    for name, r in sorted_models:
        h = r["holdout"]
        cv = r["cv"]
        print(f"{name:<20} {h['r2']:>8.4f} {h['rmse']:>8.2f} {h['mae']:>8.2f} {h['mape']:>7.2f}% {cv['cv_r2_mean']:>8.4f}  {h['train_time_sec']:>6.1f}s")

    # Best model
    best_name = sorted_models[0][0]
    best_r2 = sorted_models[0][1]["holdout"]["r2"]
    print(f"\nBEST MODEL: {best_name} (R²={best_r2})")

    # Save best model pipeline
    best_fn = build_model(best_name)
    best_pipe = Pipeline([("scaler", StandardScaler()), ("model", best_fn())])
    best_pipe.fit(X_train, y_train)
    best_path = MODELS_DIR / f"pipeline_best_benchmark_{best_name.lower()}.pkl"
    joblib.dump(best_pipe, best_path)
    print(f"Best model saved: {best_path}")

    return all_results


if __name__ == "__main__":
    run_benchmark()
