#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optuna Hyperparameter Search for Optimus Price
Optimizes: GradientBoosting, XGBoost, LightGBM, CatBoost
Objective: Minimize RMSE via TimeSeriesSplit
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
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import optuna

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

TARGET = "avg_price_per_room"
N_TRIALS = 50
N_SPLITS = 5


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


def objective_gradient_boosting(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 20),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
    }

    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", GradientBoostingRegressor(**params, random_state=42)),
        ])
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))

    return float(np.mean(scores))


def objective_random_forest(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 5, 25),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 20),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", 0.5, 0.8]),
    }

    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(**params, random_state=42, n_jobs=-1)),
        ])
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))

    return float(np.mean(scores))


def objective_xgboost(trial, X, y):
    try:
        import xgboost as xgb
    except ImportError:
        return float("inf")

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 0, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0, 10),
    }

    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", xgb.XGBRegressor(**params, random_state=42, verbosity=0)),
        ])
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))

    return float(np.mean(scores))


def objective_lightgbm(trial, X, y):
    try:
        import lightgbm as lgb
    except ImportError:
        return float("inf")

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
        "reg_alpha": trial.suggest_float("reg_alpha", 0, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0, 10),
    }

    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", lgb.LGBMRegressor(**params, random_state=42, verbose=-1)),
        ])
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))

    return float(np.mean(scores))


def objective_catboost(trial, X, y):
    try:
        from catboost import CatBoostRegressor
    except ImportError:
        return float("inf")

    params = {
        "iterations": trial.suggest_int("iterations", 100, 500),
        "depth": trial.suggest_int("depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 0, 10),
        "random_strength": trial.suggest_float("random_strength", 0, 10),
        "bagging_temperature": trial.suggest_float("bagging_temperature", 0, 10),
    }

    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", CatBoostRegressor(**params, random_seed=42, verbose=0)),
        ])
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, y_pred)))

    return float(np.mean(scores))


def run_optuna_search():
    print("=" * 60)
    print("OPTUNA HYPERPARAMETER SEARCH")
    print(f"Trials: {N_TRIALS}, CV Folds: {N_SPLITS}")
    print("=" * 60)

    X, y = load_data()
    print(f"Data: {X.shape[0]} rows, {X.shape[1]} features")

    objectives = {
        "GradientBoosting": objective_gradient_boosting,
        "RandomForest": objective_random_forest,
        "XGBoost": objective_xgboost,
        "LightGBM": objective_lightgbm,
        "CatBoost": objective_catboost,
    }

    all_results = {}

    for model_name, objective_fn in objectives.items():
        print(f"\n{'='*50}")
        print(f"Optimizing: {model_name}")
        print(f"{'='*50}")

        study = optuna.create_study(
            direction="minimize",
            study_name=f"{model_name}_optimization",
        )

        try:
            study.optimize(
                lambda trial: objective_fn(trial, X, y),
                n_trials=N_TRIALS,
                show_progress_bar=True,
            )
        except Exception as e:
            print(f"  Error: {e}")
            continue

        best = study.best_trial
        print(f"  Best RMSE: {best.value:.4f}")
        print(f"  Best params: {best.params}")

        all_results[model_name] = {
            "best_rmse": round(float(best.value), 4),
            "best_params": {k: (round(float(v), 6) if isinstance(v, float) else v) for k, v in best.params.items()},
            "n_trials": len(study.trials),
        }

        # Plot optimization history
        try:
            fig, ax = plt.subplots(figsize=(10, 4))
            trials = study.trials
            values = [t.value for t in trials if t.value is not None and t.value < float("inf")]
            if values:
                ax.plot(values, "o-", alpha=0.5, markersize=3)
                ax.axhline(y=best.value, color="r", linestyle="--", label=f"Best: {best.value:.4f}")
                ax.set_xlabel("Trial")
                ax.set_ylabel("RMSE")
                ax.set_title(f"{model_name} - Optuna Optimization History")
                ax.legend()
                plt.tight_layout()
                fig.savefig(str(REPORTS_DIR / f"optuna_history_{model_name.lower()}.png"), dpi=150, bbox_inches="tight")
                plt.close(fig)
                print(f"  Saved: optuna_history_{model_name.lower()}.png")
        except Exception:
            pass

    # Summary
    print("\n" + "=" * 60)
    print("OPTUNA RESULTS SUMMARY (sorted by RMSE)")
    print("=" * 60)
    sorted_results = sorted(all_results.items(), key=lambda x: x[1]["best_rmse"])

    for name, r in sorted_results:
        print(f"\n{name}:")
        print(f"  Best RMSE: {r['best_rmse']}")
        print(f"  Best params: {json.dumps(r['best_params'], indent=4)}")

    # Save results
    output_path = REPORTS_DIR / "optuna_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {output_path}")

    # Retrain best model with best params and save
    if sorted_results:
        best_name, best_result = sorted_results[0]
        print(f"\nRetraining best model ({best_name}) with optimized params...")
        _retrain_best(best_name, best_result["best_params"], X, y)

    return all_results


def _retrain_best(model_name, params, X, y):
    """Retrain best model with optimized params and save."""
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    if model_name == "GradientBoosting":
        from sklearn.ensemble import GradientBoostingRegressor
        model = GradientBoostingRegressor(**params, random_state=42)
    elif model_name == "RandomForest":
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
    elif model_name == "XGBoost":
        import xgboost as xgb
        model = xgb.XGBRegressor(**params, random_state=42, verbosity=0)
    elif model_name == "LightGBM":
        import lightgbm as lgb
        model = lgb.LGBMRegressor(**params, random_state=42, verbose=-1)
    elif model_name == "CatBoost":
        from catboost import CatBoostRegressor
        model = CatBoostRegressor(**params, random_seed=42, verbose=0)
    else:
        print(f"  Unknown model: {model_name}")
        return

    pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    test_r2 = float(r2_score(y_test, y_pred))
    test_mae = float(mean_absolute_error(y_test, y_pred))

    print(f"  Test RMSE: {test_rmse:.4f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test MAE: {test_mae:.4f}")

    # Save
    import joblib
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = BASE_DIR / "models" / f"pipeline_optuna_{model_name.lower()}_{ts}.pkl"
    joblib.dump(pipe, path)
    print(f"  Saved: {path}")


if __name__ == "__main__":
    run_optuna_search()
