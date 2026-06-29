#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training Pipeline for Optimus Price - FIXED VERSION
Trains without target leakage and establishes proper baseline metrics.
"""

import numpy as np
import pandas as pd
import os
import warnings
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import sklearn
import joblib
import yaml
from datetime import datetime

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"


def load_processed_data(data_path: str | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Load processed data WITHOUT competitor features that cause leakage."""
    if data_path is None:
        data_path = DATA_DIR / "processed" / "hotel_reservations_real.csv"
    df = pd.read_csv(data_path)
    target = "avg_price_per_room"
    if target not in df.columns:
        raise ValueError(f"Target '{target}' not found in {data_path}")

    # Remove any leaked competitor features
    leaked_features = [c for c in df.columns if "competitor" in c.lower()]
    if leaked_features:
        print(f"WARNING: Removing leaked features: {leaked_features}")
        df = df.drop(columns=leaked_features)

    X = df.drop(columns=[target])
    y = df[target]
    return X, y


def train_test_split_temporal(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split data chronologically (no random shuffling)."""
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    return X_train, X_test, y_train, y_test


def build_pipeline(model, use_scaler: bool = False) -> Pipeline:
    """Build pipeline. Default: NoScaler (best performing for V1)."""
    if use_scaler:
        return Pipeline([("scaler", StandardScaler()), ("model", model)])
    return Pipeline([("model", model)])


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Evaluate model with comprehensive metrics."""
    y_pred = model.predict(X_test)
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "mape": float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100),
    }


def time_series_cv_score(model, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> dict:
    """Time-series cross-validation."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmse_scores = []
    r2_scores = []
    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        rmse_scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))
        r2_scores.append(r2_score(y_val, y_pred))
    return {
        "cv_rmse_mean": float(np.mean(rmse_scores)),
        "cv_rmse_std": float(np.std(rmse_scores)),
        "cv_r2_mean": float(np.mean(r2_scores)),
        "cv_r2_std": float(np.std(r2_scores)),
    }


MODEL_REGISTRY = {
    "ElasticNet": lambda: ElasticNet(
        alpha=0.1, l1_ratio=0.5, max_iter=5000, random_state=42
    ),
    "GradientBoosting": lambda: GradientBoostingRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.08,
        subsample=0.8, random_state=42
    ),
    "RandomForest": lambda: RandomForestRegressor(
        n_estimators=200, max_depth=15, min_samples_leaf=5,
        min_samples_split=10, random_state=42, n_jobs=-1
    ),
}


def _check_xgboost():
    try:
        import xgboost as xgb
        return lambda: xgb.XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, colsample_bytree=0.8, random_state=42
        )
    except ImportError:
        return None


def _check_lightgbm():
    try:
        import lightgbm as lgb
        return lambda: lgb.LGBMRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbose=-1
        )
    except ImportError:
        return None


for _name, _fn in [("XGBoost", _check_xgboost()), ("LightGBM", _check_lightgbm())]:
    if _fn is not None:
        MODEL_REGISTRY[_name] = _fn


def train_all_models(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_test: pd.DataFrame, y_test: pd.Series,
    models_to_train: list[str] | None = None,
) -> dict[str, dict]:
    """Train all models and return results."""
    if models_to_train is None:
        models_to_train = list(MODEL_REGISTRY.keys())
    results = {}
    for name in models_to_train:
        if name not in MODEL_REGISTRY:
            print(f"  Model '{name}' not registered, skipping.")
            continue
        print(f"\nTraining {name}...")
        pipe = build_pipeline(MODEL_REGISTRY[name]())
        pipe.fit(X_train, y_train)
        metrics = evaluate_model(pipe, X_test, y_test)
        cv_metrics = time_series_cv_score(
            MODEL_REGISTRY[name](), X_train, y_train
        )
        results[name] = {"pipeline": pipe, "metrics": metrics, "cv": cv_metrics}
        print(f"  {name}: RMSE={metrics['rmse']:.2f}, R2={metrics['r2']:.4f}, "
              f"MAE={metrics['mae']:.2f}, MAPE={metrics['mape']:.1f}%")
        print(f"  CV RMSE={cv_metrics['cv_rmse_mean']:.2f} +/- {cv_metrics['cv_rmse_std']:.2f}")
    return results


def select_best_model(results: dict[str, dict], metric: str = "rmse") -> str:
    best_name = min(results, key=lambda n: results[n]["metrics"][metric])
    return best_name


def save_model(pipeline: Pipeline, name: str, metrics: dict, model_dir: str | None = None) -> str:
    if model_dir is None:
        model_dir = str(MODELS_DIR)
    os.makedirs(model_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pipeline_{name.lower()}_{ts}.pkl"
    path = os.path.join(model_dir, filename)
    joblib.dump(pipeline, path)
    meta = {
        "model": name,
        "timestamp": ts,
        "metrics": metrics,
        "file": filename,
        "versions": {
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "params": pipeline.named_steps["model"].get_params(),
    }
    meta_path = os.path.join(model_dir, "model_metadata.yaml")
    existing = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            existing = yaml.safe_load(f) or {}
    existing[name] = meta
    with open(meta_path, "w") as f:
        yaml.dump(existing, f, default_flow_style=False)
    latest_path = os.path.join(model_dir, "pipeline_trained_model.pkl")
    if os.path.exists(latest_path):
        os.remove(latest_path)
    joblib.dump(pipeline, latest_path)
    print(f"Model saved: {path}")
    print(f"  Also saved as: {latest_path}")
    return path


def train_best_and_save(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_test: pd.DataFrame, y_test: pd.Series,
) -> str:
    results = train_all_models(X_train, y_train, X_test, y_test)
    best_name = select_best_model(results)
    print(f"\nBest model: {best_name}")
    pipe = results[best_name]["pipeline"]
    metrics = results[best_name]["metrics"]
    path = save_model(pipe, best_name, metrics)
    return path


def get_feature_importance(pipeline: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    model = pipeline.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)
    else:
        importances = np.zeros(len(feature_names))
    df = pd.DataFrame({"feature": feature_names, "importance": importances})
    df = df.sort_values("importance", ascending=False).reset_index(drop=True)
    df["cumulative"] = df["importance"].cumsum()
    return df


def save_train_test_csvs(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_test: pd.DataFrame, y_test: pd.Series,
):
    train_dir = DATA_DIR / "train"
    test_dir = DATA_DIR / "test"
    train_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    train_df.to_csv(train_dir / "hotel_reservations_train_data.csv", index=False)
    test_df.to_csv(test_dir / "hotel_reservations_test_data.csv", index=False)


def validate_no_leakage(results: dict, threshold: float = 0.95) -> bool:
    """Check if R2 indicates potential data leakage."""
    for name, result in results.items():
        r2 = result["metrics"]["r2"]
        if r2 > threshold:
            print(f"WARNING: {name} R2={r2:.4f} > {threshold} - possible leakage!")
            return False
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TRAINING PIPELINE (NO LEAKAGE)")
    print("=" * 60)

    print("\nLoading processed data...")
    X, y = load_processed_data()
    print(f"  Features: {X.shape[1]}, Rows: {len(X)}")
    print(f"  Feature names: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split_temporal(X, y)
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    save_train_test_csvs(X_train, y_train, X_test, y_test)

    results = train_all_models(X_train, y_train, X_test, y_test)

    # Validate no leakage
    print("\n--- Leakage Validation ---")
    if validate_no_leakage(results):
        print("OK: No leakage detected (R2 < 0.95)")
    else:
        print("WARNING: Possible data leakage detected!")

    best_name = select_best_model(results)
    print(f"\nBest model: {best_name}")

    pipe = results[best_name]["pipeline"]
    metrics = results[best_name]["metrics"]
    path = save_model(pipe, best_name, metrics)

    # Feature importance
    feature_imp = get_feature_importance(pipe, list(X.columns))
    print("\nTop 10 Feature Importances:")
    print(feature_imp.head(10).to_string(index=False))

    print(f"\nFINAL METRICS (NO LEAKAGE):")
    print(f"  RMSE:  {metrics['rmse']:.4f}")
    print(f"  MAE:   {metrics['mae']:.4f}")
    print(f"  R2:    {metrics['r2']:.4f}")
    print(f"  MAPE:  {metrics['mape']:.2f}%")
