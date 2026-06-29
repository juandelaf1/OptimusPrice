#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature Enricher for Optimus Price - FIXED VERSION
Generates competitor features from REAL scraped data, NOT from target variable.
This eliminates the target leakage that caused R2=0.9998.
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CLEAN_PATH = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
ENRICHED_PATH = DATA_DIR / "processed" / "hotel_reservations_enriched.csv"
SCRAPED_DIR = DATA_DIR / "scraped"


class FeatureEnricher:
    """Enriches ML features with REAL competitor pricing data from scraping."""

    def __init__(self, competitor_cache: Optional[Dict] = None):
        """
        Args:
            competitor_cache: Dict with competitor prices from real scraping.
                             Structure: {hotel_id: {date: {competitor: price}}}
                             If None, uses placeholder values (no leakage).
        """
        self.competitor_cache = competitor_cache or {}

    def load_scraped_data(self, tag: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load scraped competitor data from data/scraped directory.

        Args:
            tag: Filter files by tag (e.g., 'real'). If None, loads all CSV files.

        Returns:
            DataFrame with scraped competitor data, or None if no data found.
        """
        if not SCRAPED_DIR.exists():
            print(f"Scraped data directory not found: {SCRAPED_DIR}")
            return None

        csv_files = sorted(SCRAPED_DIR.glob("*.csv"))
        if tag:
            csv_files = [f for f in csv_files if tag in f.name]

        if not csv_files:
            print(f"No CSV files found in {SCRAPED_DIR}")
            return None

        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if len(df) > 0:
                    dfs.append(df)
                    print(f"  Loaded {len(df)} records from {csv_file.name}")
            except Exception as e:
                print(f"  Error loading {csv_file.name}: {e}")

        if not dfs:
            print("No valid data loaded from scraped files")
            return None

        combined = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal scraped records loaded: {len(combined)}")

        required_cols = ["hotel_id", "ota", "price", "check_in_date"]
        missing = [c for c in required_cols if c not in combined.columns]
        if missing:
            print(f"Warning: Missing columns: {missing}")

        return combined

    def aggregate_scraped_by_date(
        self, scraped_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate scraped data by check_in_date to get market-level stats.

        Args:
            scraped_df: Raw scraped data with columns [hotel_id, ota, price, check_in_date]

        Returns:
            DataFrame indexed by date with aggregated competitor stats.
        """
        if "check_in_date" not in scraped_df.columns:
            print("Warning: check_in_date column not found, using all data as single date")
            stats = {
                "competitor_avg_price": [scraped_df["price"].mean()],
                "competitor_min_price": [scraped_df["price"].min()],
                "competitor_max_price": [scraped_df["price"].max()],
                "competitor_price_std": [scraped_df["price"].std()],
                "competitor_count": [len(scraped_df)],
                "competitor_median_price": [scraped_df["price"].median()],
            }
            return pd.DataFrame(stats)

        daily = scraped_df.groupby("check_in_date").agg(
            competitor_avg_price=("price", "mean"),
            competitor_min_price=("price", "min"),
            competitor_max_price=("price", "max"),
            competitor_price_std=("price", "std"),
            competitor_count=("price", "count"),
            competitor_median_price=("price", "median"),
        ).reset_index()

        daily["competitor_price_std"] = daily["competitor_price_std"].fillna(0)
        return daily

    def generate_competitor_features_from_real_data(
        self,
        df: pd.DataFrame,
        competitor_prices: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Generate competitor features from REAL scraped prices.

        Args:
            df: Hotel booking data
            competitor_prices: DataFrame with columns:
                [date, hotel_id, competitor_name, price]
                If None, logs a warning (no synthetic fallback).

        Returns:
            DataFrame with added competitor features
        """
        result = df.copy()

        if competitor_prices is not None and len(competitor_prices) > 0:
            result = self._merge_real_competitor_data(result, competitor_prices)
        else:
            print("Warning: No competitor price data available. Features will not include market context.")

        return result

    def _merge_real_competitor_data(
        self, df: pd.DataFrame, competitor_prices: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge real competitor data into hotel records."""
        # competitor_prices should have: date, competitor_name, price
        # We need to match by date and room type

        # Calculate market-level aggregates
        daily_market = competitor_prices.groupby("date").agg(
            competitor_avg_price=("price", "mean"),
            competitor_min_price=("price", "min"),
            competitor_max_price=("price", "max"),
            competitor_price_std=("price", "std"),
            competitor_count=("price", "count"),
        ).reset_index()

        # Merge on date (using arrival info)
        if "arrival_date" in df.columns and "arrival_year" in df.columns:
            df["booking_date"] = pd.to_datetime(
                dict(
                    year=df["arrival_year"],
                    month=df["arrival_month"],
                    day=df["arrival_date"],
                ),
                errors="coerce",
            )
            df["date_str"] = df["booking_date"].dt.strftime("%Y-%m-%d")

            result = df.merge(daily_market, left_on="date_str", right_on="date", how="left")
            result = result.drop(columns=["date", "date_str", "booking_date"], errors="ignore")
        else:
            # Fallback: use mean values
            for col in ["competitor_avg_price", "competitor_min_price",
                        "competitor_max_price", "competitor_price_std", "competitor_count"]:
                result[col] = daily_market[col].mean()

        # Fill missing with market averages
        for col in ["competitor_avg_price", "competitor_min_price",
                    "competitor_max_price", "competitor_price_std", "competitor_count"]:
            if col in result.columns:
                result[col] = result[col].fillna(result[col].mean())

        return result

    def enrich_and_save(
        self,
        input_path: str = str(CLEAN_PATH),
        output_path: str = str(ENRICHED_PATH),
        competitor_prices: Optional[pd.DataFrame] = None,
    ) -> str:
        """Load clean data, enrich with competitor features, save."""
        df = pd.read_csv(input_path)
        print(f"Loaded {len(df)} rows from {os.path.basename(input_path)}")

        enriched = self.generate_competitor_features_from_real_data(
            df, competitor_prices
        )
        enriched.to_csv(output_path, index=False)

        new_features = [c for c in enriched.columns if c not in df.columns]
        print(f"Enriched data saved to {os.path.basename(output_path)}")
        print(f"New features ({len(new_features)}): {new_features}")
        return output_path


def retrain_without_leakage():
    """Full pipeline: enrich (without leakage), split, train, evaluate."""
    print("=" * 60)
    print("RETRAINING WITHOUT TARGET LEAKAGE")
    print("=" * 60)

    enricher = FeatureEnricher()
    enriched_path = enricher.enrich_and_save()

    df = pd.read_csv(enriched_path)
    target = "avg_price_per_room"
    X = df.drop(columns=[target])
    y = df[target]

    print(f"\nFeatures: {X.shape[1]}, Rows: {len(X)}")
    print(f"Feature names: {list(X.columns)}")

    from src.optimus_price.training import (
        train_test_split_temporal,
        train_all_models,
        select_best_model,
        save_model,
        evaluate_model,
        get_feature_importance,
    )

    X_train, X_test, y_train, y_test = train_test_split_temporal(X, y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    results = train_all_models(X_train, y_train, X_test, y_test)

    best_name = select_best_model(results)
    print(f"\nBest model: {best_name}")

    pipe = results[best_name]["pipeline"]
    metrics = results[best_name]["metrics"]
    cv_metrics = results[best_name]["cv"]

    path = save_model(pipe, best_name, metrics)

    # Feature importance analysis
    feature_imp = get_feature_importance(pipe, list(X.columns))
    print("\nTop 10 Feature Importances:")
    print(feature_imp.head(10).to_string(index=False))

    print(f"\nFINAL METRICS (NO LEAKAGE):")
    print(f"  RMSE:  {metrics['rmse']:.4f}")
    print(f"  MAE:   {metrics['mae']:.4f}")
    print(f"  R2:    {metrics['r2']:.4f}")
    print(f"  MAPE:  {metrics['mape']:.2f}%")
    print(f"  CV RMSE: {cv_metrics['cv_rmse_mean']:.4f} +/- {cv_metrics['cv_rmse_std']:.4f}")

    if metrics['r2'] > 0.95:
        print("\n  WARNING: R2 still very high - check for remaining leakage!")
    elif metrics['r2'] > 0.5:
        print("\n  OK: R2 is in realistic range for synthetic data")
    else:
        print("\n  NOTE: R2 is low - model may need more features or tuning")

    return path


if __name__ == "__main__":
    retrain_without_leakage()
