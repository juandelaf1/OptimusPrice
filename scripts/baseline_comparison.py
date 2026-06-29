#!/usr/bin/env python3
"""
Baseline Comparison — Phase 2 Deliverable
Compares ML model against simple baselines to validate real value.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from src.optimus_price.training import load_processed_data, build_pipeline, evaluate_model, MODEL_REGISTRY


def mean_baseline(y_train, y_test):
    """Predict the mean of training set for all test samples."""
    mean_val = y_train.mean()
    predictions = np.full(len(y_test), mean_val)
    return predictions


def median_baseline(y_train, y_test):
    """Predict the median of training set for all test samples."""
    median_val = y_train.median()
    predictions = np.full(len(y_test), median_val)
    return predictions


def monthly_mean_baseline(X_train, y_train, X_test):
    """Predict the mean price per arrival month."""
    train_df = X_train.copy()
    train_df['target'] = y_train
    monthly_means = train_df.groupby('arrival_month')['target'].mean()
    
    predictions = X_test['arrival_month'].map(monthly_means)
    # Fill missing months with overall mean
    predictions = predictions.fillna(y_train.mean())
    return predictions.values


def seasonal_baseline(X_train, y_train, X_test):
    """Predict based on season (high/shoulder/low)."""
    train_df = X_train.copy()
    train_df['target'] = y_train
    
    # Define seasons
    def get_season(month):
        if month in [6, 7, 8, 12]:
            return 'peak'
        elif month in [4, 5, 9, 10, 11]:
            return 'shoulder'
        else:
            return 'low'
    
    train_df['season'] = train_df['arrival_month'].apply(get_season)
    season_means = train_df.groupby('season')['target'].mean()
    
    X_test_copy = X_test.copy()
    X_test_copy['season'] = X_test_copy['arrival_month'].apply(get_season)
    predictions = X_test_copy['season'].map(season_means)
    predictions = predictions.fillna(y_train.mean())
    return predictions.values


def room_type_baseline(X_train, y_train, X_test):
    """Predict based on room_type_value."""
    train_df = X_train.copy()
    train_df['target'] = y_train
    room_means = train_df.groupby('room_type_value')['target'].mean()
    
    predictions = X_test['room_type_value'].map(room_means)
    predictions = predictions.fillna(y_train.mean())
    return predictions.values


def main():
    print("=" * 60)
    print("BASELINE COMPARISON — Phase 2 Deliverable")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    X, y = load_processed_data()
    print(f"Dataset: {X.shape[0]} rows, {X.shape[1]} features")
    
    # Temporal split (no shuffle)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"Train: {len(X_train)} samples")
    print(f"Test:  {len(X_test)} samples")
    
    # Evaluate baselines
    baselines = {
        'Mean Baseline': mean_baseline(y_train, y_test),
        'Median Baseline': median_baseline(y_train, y_test),
        'Monthly Mean': monthly_mean_baseline(X_train, y_train, X_test),
        'Seasonal': seasonal_baseline(X_train, y_train, X_test),
        'Room Type': room_type_baseline(X_train, y_train, X_test),
    }
    
    print("\n" + "-" * 60)
    print(f"{'Model':<25} {'RMSE':>8} {'MAE':>8} {'R²':>8} {'MAPE':>8}")
    print("-" * 60)
    
    results = []
    for name, preds in baselines.items():
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        mape = np.mean(np.abs((y_test - preds) / y_test)) * 100
        
        print(f"{name:<25} {rmse:>8.2f} {mae:>8.2f} {r2:>8.4f} {mape:>7.2f}%")
        results.append({'model': name, 'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape})
    
    # Train ML model (ElasticNet)
    print("\nTraining ElasticNet (champion)...")
    en_model = MODEL_REGISTRY['ElasticNet']()
    pipeline = build_pipeline(en_model)
    pipeline.fit(X_train, y_train)
    ml_preds = pipeline.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, ml_preds))
    mae = mean_absolute_error(y_test, ml_preds)
    r2 = r2_score(y_test, ml_preds)
    mape = np.mean(np.abs((y_test - ml_preds) / y_test)) * 100
    
    print(f"{'ElasticNet (ML)':<25} {rmse:>8.2f} {mae:>8.2f} {r2:>8.4f} {mape:>7.2f}%")
    results.append({'model': 'ElasticNet (ML)', 'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape})
    
    print("-" * 60)
    
    # Find best baseline
    best_baseline = min([r for r in results if r['model'] != 'ElasticNet (ML)'], key=lambda x: x['rmse'])
    ml_result = [r for r in results if r['model'] == 'ElasticNet (ML)'][0]
    
    improvement_rmse = (best_baseline['rmse'] - ml_result['rmse']) / best_baseline['rmse'] * 100
    improvement_r2 = ml_result['r2'] - best_baseline['r2']
    
    print(f"\n{'ANALYSIS':=^60}")
    print(f"Best baseline: {best_baseline['model']} (RMSE={best_baseline['rmse']:.2f})")
    print(f"ML model:       ElasticNet (RMSE={ml_result['rmse']:.2f})")
    print(f"\nRMSE improvement over best baseline: {improvement_rmse:+.1f}%")
    print(f"R² improvement over best baseline:   {improvement_r2:+.4f}")
    
    if improvement_rmse > 5:
        print("\n[OK] ML model provides SIGNIFICANT improvement over baselines")
    elif improvement_rmse > 0:
        print("\n[~] ML model provides MARGINAL improvement over baselines")
    else:
        print("\n[!] ML model does NOT outperform baselines - investigate")
    
    # Save results
    df_results = pd.DataFrame(results)
    output_path = Path("docs/baseline_comparison.csv")
    df_results.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
