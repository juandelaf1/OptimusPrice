import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports"


def feature_importance_df(model, feature_names: list[str]) -> pd.DataFrame:
    importances = model.named_steps["model"].feature_importances_
    df = pd.DataFrame({"feature": feature_names, "importance": importances})
    df = df.sort_values("importance", ascending=False).reset_index(drop=True)
    df["cumulative"] = df["importance"].cumsum()
    return df


def plot_feature_importance(df: pd.DataFrame, top_n: int = 15, title: str = "Feature Importance"):
    top = df.head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(top)))
    ax.barh(range(len(top)), top["importance"], color=colors[::-1])
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["feature"])
    ax.set_xlabel("Importance")
    ax.set_title(title)
    ax.invert_yaxis()
    plt.tight_layout()
    return fig


def plot_residuals(y_true: np.ndarray, y_pred: np.ndarray):
    residuals = y_true - y_pred
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].scatter(y_pred, residuals, alpha=0.4, s=10)
    axes[0].axhline(y=0, color="red", linestyle="--", linewidth=1)
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Residuals")
    axes[0].set_title("Residuals vs Predicted")
    axes[1].hist(residuals, bins=50, color="steelblue", edgecolor="white")
    axes[1].set_xlabel("Residual")
    axes[1].set_ylabel("Frequency")
    axes[1].set_title("Residual Distribution")
    plt.tight_layout()
    return fig


def plot_predicted_vs_actual(y_true: np.ndarray, y_pred: np.ndarray):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.3, s=8)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1)
    ax.set_xlabel("Actual Price")
    ax.set_ylabel("Predicted Price")
    ax.set_title("Predicted vs Actual")
    plt.tight_layout()
    return fig


def save_metrics_report(
    model_name: str,
    metrics: dict,
    cv_metrics: dict | None = None,
    feature_imp: pd.DataFrame | None = None,
    path: str | None = None,
):
    if path is None:
        path = REPORTS_DIR / "metrics_report.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        f"# Model Evaluation Report: {model_name}",
        f"\n**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "\n## Test Metrics",
        f"| Metric | Value |",
        "|--------|-------|",
        f"| RMSE | {metrics.get('rmse', 'N/A'):.2f} |",
        f"| MAE | {metrics.get('mae', 'N/A'):.2f} |",
        f"| R² | {metrics.get('r2', 'N/A'):.4f} |",
        f"| MAPE | {metrics.get('mape', 'N/A'):.1f}% |",
    ]
    if cv_metrics:
        lines += [
            "\n## Time-Series Cross-Validation",
            f"| Metric | Mean ± Std |",
            "|--------|-----------|",
            f"| CV RMSE | {cv_metrics.get('cv_rmse_mean', 'N/A'):.2f} ± {cv_metrics.get('cv_rmse_std', 'N/A'):.2f} |",
            f"| CV R² | {cv_metrics.get('cv_r2_mean', 'N/A'):.4f} ± {cv_metrics.get('cv_r2_std', 'N/A'):.4f} |",
        ]
    if feature_imp is not None:
        lines += ["\n## Feature Importance (Top 10)", "", "| Feature | Importance | Cumulative |", "|---------|-----------|------------|"]
        for _, row in feature_imp.head(10).iterrows():
            lines.append(f"| {row['feature']} | {row['importance']:.4f} | {row['cumulative']:.4f} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Reporte guardado: {path}")


if __name__ == "__main__":
    print("Módulo de evaluación cargado correctamente.")
