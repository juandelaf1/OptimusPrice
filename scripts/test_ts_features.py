#!/usr/bin/env python3
"""
Phase 3: Test Time-Series Features Impact
Compares model performance with and without time-series features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.optimus_price.training import load_processed_data, MODEL_REGISTRY
from src.optimus_price.time_series_enricher import enrich_features_v2


def train_and_evaluate(X_train, y_train, X_test, y_test, name="Model"):
    """Train ElasticNet and return metrics."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000, random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100
    
    return {'name': name, 'rmse': rmse, 'r2': r2, 'mape': mape, 'n_features': X_train.shape[1]}


def main():
    print("=" * 60)
    print("PHASE 3: Time-Series Features Impact Test")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    X, y = load_processed_data()
    print(f"Original features: {X.shape[1]}")
    
    # Temporal split
    split_idx = int(len(X) * 0.8)
    X_train_orig, X_test_orig = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Baseline (without time-series features)
    print("\n--- Baseline (without time-series features) ---")
    baseline = train_and_evaluate(X_train_orig, y_train, X_test_orig, y_test, "Baseline")
    print(f"  Features: {baseline['n_features']}")
    print(f"  RMSE: {baseline['rmse']:.2f}")
    print(f"  R²: {baseline['r2']:.4f}")
    print(f"  MAPE: {baseline['mape']:.2f}%")
    
    # Add time-series features
    print("\n--- With Time-Series Features ---")
    X_train_enriched = enrich_features_v2(X_train_orig.copy())
    X_test_enriched = enrich_features_v2(X_test_orig.copy())
    
    # Remove non-numeric columns
    for col in X_train_enriched.columns:
        if X_train_enriched[col].dtype == 'object':
            X_train_enriched = X_train_enriched.drop(columns=[col])
            X_test_enriched = X_test_enriched.drop(columns=[col])
    
    print(f"  Enriched features: {X_train_enriched.shape[1]}")
    
    enriched = train_and_evaluate(X_train_enriched, y_train, X_test_enriched, y_test, "Enriched")
    print(f"  RMSE: {enriched['rmse']:.2f}")
    print(f"  R²: {enriched['r2']:.4f}")
    print(f"  MAPE: {enriched['mape']:.2f}%")
    
    # Compare
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    rmse_change = (baseline['rmse'] - enriched['rmse']) / baseline['rmse'] * 100
    r2_change = enriched['r2'] - baseline['r2']
    
    print(f"  RMSE: {baseline['rmse']:.2f} -> {enriched['rmse']:.2f} ({rmse_change:+.1f}%)")
    print(f"  R²:   {baseline['r2']:.4f} -> {enriched['r2']:.4f} ({r2_change:+.4f})")
    print(f"  Features: {baseline['n_features']} -> {enriched['n_features']} (+{enriched['n_features'] - baseline['n_features']})")
    
    if rmse_change > 1:
        print("\n[OK] Time-series features IMPROVE model performance")
    elif rmse_change > -1:
        print("\n[~] Time-series features have MARGINAL impact")
    else:
        print("\n[!] Time-series features HURT performance — investigate")


if __name__ == "__main__":
    main()
