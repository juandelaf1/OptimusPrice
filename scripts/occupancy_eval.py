#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Occupancy Model Evaluation for Optimus Price
Metrics: ROC AUC, Precision, Recall, Calibration, Confusion Matrix
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
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    roc_auc_score, roc_curve, precision_score, recall_score,
    f1_score, brier_score_loss, log_loss,
    confusion_matrix, classification_report,
    precision_recall_curve, average_precision_score,
)
from sklearn.calibration import CalibrationDisplay, calibration_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR.mkdir(exist_ok=True)

TARGET = "booking_status_Not_Canceled"


def load_data():
    """Load data for occupancy model."""
    path = DATA_DIR / "processed" / "hotel_reservations_real.csv"
    if not path.exists():
        path = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
    print(f"Loading: {path}")
    df = pd.read_csv(path)

    # Remove target leakage
    leaked = [c for c in df.columns if "competitor" in c.lower()]
    if leaked:
        df = df.drop(columns=leaked)

    print(f"  Rows: {len(df)}, Occupancy rate: {df[TARGET].mean():.3f}")
    return df


def prepare_features(df):
    """Prepare features for occupancy prediction."""
    features = pd.DataFrame()

    features["room_price"] = df.get("avg_price_per_room", 100.0)

    if "avg_price_per_room" in df.columns:
        market_avg = df["avg_price_per_room"].rolling(window=30, min_periods=1).mean()
        features["price_vs_market"] = features["room_price"] / (market_avg + 1)
    else:
        features["price_vs_market"] = 1.0

    if "arrival_month" in df.columns:
        features["month"] = df["arrival_month"]
        season_factor = {
            1: 0.70, 2: 0.65, 3: 0.75, 4: 0.85,
            5: 0.90, 6: 1.25, 7: 1.40, 8: 1.35,
            9: 0.95, 10: 0.85, 11: 0.75, 12: 1.20,
        }
        features["season_factor"] = features["month"].map(season_factor).fillna(1.0)
    else:
        features["month"] = 6
        features["season_factor"] = 1.0

    if "arrival_day_of_week" in df.columns:
        features["is_weekend"] = (df["arrival_day_of_week"] >= 5).astype(int)
    else:
        features["is_weekend"] = 0

    if "lead_time" in df.columns:
        features["lead_time_days"] = df["lead_time"]
        features["is_last_minute"] = (df["lead_time"] < 7).astype(int)
        features["is_early_bird"] = (df["lead_time"] > 60).astype(int)
    else:
        features["lead_time_days"] = 30
        features["is_last_minute"] = 0
        features["is_early_bird"] = 0

    features["total_guests"] = df.get("total_guests", 2)
    features["total_nights"] = df.get("total_nights", 1)
    features["special_requests"] = df.get("no_of_special_requests", 0)
    features["is_repeated_guest"] = df.get("repeated_guest", 0)

    if "market_segment_type_Online" in df.columns:
        features["is_online_booking"] = df["market_segment_type_Online"].astype(int)
    else:
        features["is_online_booking"] = 1

    meal_cols = [c for c in df.columns if c.startswith("type_of_meal_plan_")]
    if meal_cols:
        features["has_meal_plan"] = (df[meal_cols].sum(axis=1) > 0).astype(int)
    else:
        features["has_meal_plan"] = 0

    room_cols = [c for c in df.columns if c.startswith("room_type_reserved_")]
    if room_cols:
        room_values = {col: i + 1 for i, col in enumerate(sorted(room_cols))}
        features["room_type_value"] = sum(
            df[col].astype(int) * val for col, val in room_values.items()
        )
    else:
        features["room_type_value"] = 1

    features["requires_parking"] = df.get("required_car_parking_space", 0)

    return features


def evaluate_occupancy(y_test, y_pred, y_prob, y_prob_cal=None):
    """Compute comprehensive occupancy metrics."""
    metrics = {
        "accuracy": round(float((y_pred == y_test).mean()), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "brier_score": round(float(brier_score_loss(y_test, y_prob)), 4),
        "log_loss": round(float(log_loss(y_test, y_prob)), 4),
        "avg_precision": round(float(average_precision_score(y_test, y_prob)), 4),
    }

    if y_prob_cal is not None:
        metrics["calibrated_roc_auc"] = round(float(roc_auc_score(y_test, y_prob_cal)), 4)
        metrics["calibrated_brier"] = round(float(brier_score_loss(y_test, y_prob_cal)), 4)

    return metrics


def plot_roc_curve(y_test, y_prob, save_path=None):
    """Plot ROC curve."""
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color="#2196F3", linewidth=2, label=f"ROC (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve - Occupancy Model")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_precision_recall(y_test, y_prob, save_path=None):
    """Plot precision-recall curve."""
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    ap = average_precision_score(y_test, y_prob)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(recall, precision, color="#4CAF50", linewidth=2, label=f"PR (AP = {ap:.4f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve - Occupancy Model")
    ax.legend(loc="lower left")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_calibration(y_test, y_prob, y_prob_cal=None, save_path=None):
    """Plot calibration curves."""
    fig, ax = plt.subplots(figsize=(7, 6))

    # Uncalibrated
    fraction_pos, mean_pred = calibration_curve(y_test, y_prob, n_bins=10)
    ax.plot(mean_pred, fraction_pos, "s-", color="#2196F3", linewidth=2, label="Uncalibrated")

    # Calibrated
    if y_prob_cal is not None:
        fraction_pos_cal, mean_pred_cal = calibration_curve(y_test, y_prob_cal, n_bins=10)
        ax.plot(mean_pred_cal, fraction_pos_cal, "o-", color="#F44336", linewidth=2, label="Calibrated")

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5, label="Perfect")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title("Calibration Curve - Occupancy Model")
    ax.legend(loc="upper left")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_confusion_matrix(y_test, y_pred, save_path=None):
    """Plot confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix")
    plt.colorbar(im, ax=ax)

    classes = ["Canceled", "Not Canceled"]
    tick_marks = [0, 1]
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(classes)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")

    ax.set_ylabel("True Label")
    ax.set_xlabel("Predicted Label")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_threshold_analysis(y_test, y_prob, save_path=None):
    """Analyze metrics at different probability thresholds."""
    thresholds = np.arange(0.1, 0.9, 0.05)
    results = []

    for t in thresholds:
        y_pred_t = (y_prob >= t).astype(int)
        results.append({
            "threshold": round(float(t), 2),
            "precision": round(float(precision_score(y_test, y_pred_t, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred_t, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_pred_t, zero_division=0)), 4),
        })

    fig, ax = plt.subplots(figsize=(8, 5))
    thresholds_list = [r["threshold"] for r in results]
    ax.plot(thresholds_list, [r["precision"] for r in results], "o-", label="Precision", color="#2196F3")
    ax.plot(thresholds_list, [r["recall"] for r in results], "s-", label="Recall", color="#F44336")
    ax.plot(thresholds_list, [r["f1"] for r in results], "^-", label="F1", color="#4CAF50")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("Score")
    ax.set_title("Threshold Analysis - Occupancy Model")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)

    # Find optimal F1 threshold
    best = max(results, key=lambda x: x["f1"])
    return {"thresholds": results, "best_f1_threshold": best}


def run_evaluation():
    print("=" * 60)
    print("OCCUPANCY MODEL EVALUATION")
    print("=" * 60)

    df = load_data()
    X = prepare_features(df)
    y = df[TARGET].astype(int)

    # Temporal split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"  Train occupancy: {y_train.mean():.3f}, Test occupancy: {y_test.mean():.3f}")

    # Train model
    print("\nTraining occupancy model...")
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", GradientBoostingClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            subsample=0.8, random_state=42
        )),
    ])
    model.fit(X_train, y_train)

    # Calibrate
    print("Calibrating probabilities...")
    calibrated = CalibratedClassifierCV(model, cv=3, method="sigmoid")
    calibrated.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    y_prob_cal = calibrated.predict_proba(X_test)[:, 1]

    # Evaluate
    print("\nComputing metrics...")
    metrics = evaluate_occupancy(y_test, y_pred, y_prob, y_prob_cal)
    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    # Classification report
    report = classification_report(y_test, y_pred, target_names=["Canceled", "Not Canceled"])
    print(f"\nClassification Report:\n{report}")

    # Plots
    print("\nGenerating plots...")
    plot_roc_curve(y_test, y_prob, save_path=str(REPORTS_DIR / "occupancy_roc_curve.png"))
    plot_precision_recall(y_test, y_prob, save_path=str(REPORTS_DIR / "occupancy_pr_curve.png"))
    plot_calibration(y_test, y_prob, y_prob_cal, save_path=str(REPORTS_DIR / "occupancy_calibration.png"))
    plot_confusion_matrix(y_test, y_pred, save_path=str(REPORTS_DIR / "occupancy_confusion_matrix.png"))
    threshold_analysis = plot_threshold_analysis(
        y_test, y_prob, save_path=str(REPORTS_DIR / "occupancy_threshold_analysis.png")
    )

    # Cross-validation
    print("\nRunning TimeSeriesSplit CV...")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = {"accuracy": [], "auc": [], "f1": []}

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(
                n_estimators=150, max_depth=5, learning_rate=0.1,
                subsample=0.8, random_state=42
            )),
        ])
        pipe.fit(X_tr, y_tr)
        y_pred_cv = pipe.predict(X_val)
        y_prob_cv = pipe.predict_proba(X_val)[:, 1]

        cv_scores["accuracy"].append(float((y_pred_cv == y_val).mean()))
        cv_scores["auc"].append(float(roc_auc_score(y_val, y_prob_cv)))
        cv_scores["f1"].append(float(f1_score(y_val, y_pred_cv)))

    cv_summary = {
        "cv_accuracy_mean": round(float(np.mean(cv_scores["accuracy"])), 4),
        "cv_accuracy_std": round(float(np.std(cv_scores["accuracy"])), 4),
        "cv_auc_mean": round(float(np.mean(cv_scores["auc"])), 4),
        "cv_auc_std": round(float(np.std(cv_scores["auc"])), 4),
        "cv_f1_mean": round(float(np.mean(cv_scores["f1"])), 4),
        "cv_f1_std": round(float(np.std(cv_scores["f1"])), 4),
    }
    print(f"\nCV Summary:")
    for k, v in cv_summary.items():
        print(f"  {k}: {v}")

    # Save all results
    results = {
        "holdout_metrics": metrics,
        "cv_summary": cv_summary,
        "threshold_analysis": threshold_analysis,
        "classification_report": report,
    }

    output_path = REPORTS_DIR / "occupancy_evaluation.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")

    return results


if __name__ == "__main__":
    run_evaluation()
