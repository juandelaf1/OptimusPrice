#!/usr/bin/env python3
"""
Feature Builder for Optimus Price
Sprint 5: Feature Engineering Implementation - Phase 1

Generates temporal and booking behavior features.
No target leakage. No synthetic data.
"""

import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

TARGET = "avg_price_per_room"


def load_raw_data() -> pd.DataFrame:
    """Load raw data without target leakage."""
    df = pd.read_csv(DATA_DIR / "processed" / "hotel_reservations_real.csv")
    leaked = [c for c in df.columns if "competitor" in c.lower()]
    if leaked:
        df = df.drop(columns=leaked)
    return df


def build_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate temporal features from arrival columns.
    
    Features:
    - month_sin, month_cos: Cyclical month encoding
    - week_sin, week_cos: Cyclical week encoding
    - quarter: Quarter of year (1-4)
    - season: Season (0=winter, 1=spring, 2=summer, 3=fall)
    - is_high_season: Whether arrival is in high season (Nov-Mar)
    - is_weekend_arrival: Whether arrival is on weekend
    - days_until_peak: Days until next peak period
    """
    result = df.copy()
    
    # Cyclical month encoding
    result["month_sin"] = np.sin(2 * np.pi * result["arrival_month"] / 12)
    result["month_cos"] = np.cos(2 * np.pi * result["arrival_month"] / 12)
    
    # Cyclical week encoding
    result["week_sin"] = np.sin(2 * np.pi * result["arrival_week_number"] / 52)
    result["week_cos"] = np.cos(2 * np.pi * result["arrival_week_number"] / 52)
    
    # Quarter
    result["quarter"] = ((result["arrival_month"] - 1) // 3) + 1
    
    # Season (0=winter, 1=spring, 2=summer, 3=fall)
    month_to_season = {12: 0, 1: 0, 2: 0,  # Winter
                       3: 1, 4: 1, 5: 1,    # Spring
                       6: 2, 7: 2, 8: 2,    # Summer
                       9: 3, 10: 3, 11: 3}  # Fall
    result["season"] = result["arrival_month"].map(month_to_season)
    
    # High season (Nov-Mar for beach resorts, varies by location)
    result["is_high_season"] = result["arrival_month"].isin([11, 12, 1, 2, 3]).astype(int)
    
    # Weekend arrival
    result["is_weekend_arrival"] = result["arrival_day_of_week"].isin([5, 6]).astype(int)
    
    # Days until peak (simplified: peak = July-August)
    peak_months = [7, 8]
    result["days_until_peak"] = result["arrival_month"].apply(
        lambda m: min([(pm - m) % 12 for pm in peak_months])
    )
    
    return result


def build_booking_behavior_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate booking behavior features.
    
    Features:
    - lead_time_bin: Lead time categorized (0-4)
    - lead_time_category: Lead time label
    - short_stay: Stay <= 1 night
    - medium_stay: Stay 2-6 nights
    - long_stay: Stay >= 7 nights
    - stay_bucket: Stay length bucket (0-4)
    - booking_window: Lead time / total_nights ratio
    - guest_density: Guests per night
    - room_intensity: Room utilization metric
    """
    result = df.copy()
    
    # Lead time bins
    result["lead_time_bin"] = pd.cut(
        result["lead_time"],
        bins=[-1, 7, 30, 90, 180, 737],
        labels=[0, 1, 2, 3, 4]
    ).fillna(4).astype(int)
    
    # Lead time category (for interpretability)
    conditions = [
        result["lead_time"] <= 7,
        result["lead_time"] <= 30,
        result["lead_time"] <= 90,
        result["lead_time"] <= 180,
    ]
    choices = ["last_minute", "short_term", "medium_term", "long_term"]
    result["lead_time_category"] = np.select(conditions, choices, default="very_long_term")
    
    # Stay length indicators
    total_nights = result["total_nights"].clip(lower=1)  # Avoid division by zero
    result["short_stay"] = (result["total_nights"] <= 1).astype(int)
    result["medium_stay"] = ((result["total_nights"] >= 2) & (result["total_nights"] <= 6)).astype(int)
    result["long_stay"] = (result["total_nights"] >= 7).astype(int)
    
    # Stay bucket
    result["stay_bucket"] = pd.cut(
        result["total_nights"],
        bins=[-1, 1, 3, 7, 14, 39],
        labels=[0, 1, 2, 3, 4]
    ).fillna(4).astype(int)
    
    # Booking window (lead time relative to stay)
    result["booking_window"] = result["lead_time"] / (result["total_nights"] + 1)
    
    # Guest density (guests per night)
    result["guest_density"] = result["total_guests"] / (result["total_nights"] + 1)
    
    # Room intensity (rooms needed per guest)
    result["room_intensity"] = result["total_guests"] / (result["adults"] + 1)
    
    return result


def build_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build all Phase 1 features."""
    result = df.copy()
    result = build_temporal_features(result)
    result = build_booking_behavior_features(result)
    return result


def validate_features(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
    """
    Validate generated features.
    
    Checks:
    - Row count preserved
    - No null explosion
    - No target leakage
    - Feature ranges valid
    """
    validation = {
        "row_count_preserved": len(df_before) == len(df_after),
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "null_check": {},
        "leakage_check": {},
        "range_check": {},
    }
    
    # Null check
    new_features = [c for c in df_after.columns if c not in df_before.columns]
    for feat in new_features:
        null_count = int(df_after[feat].isnull().sum())
        null_pct = null_count / len(df_after) * 100
        validation["null_check"][feat] = {
            "null_count": null_count,
            "null_pct": round(null_pct, 4),
            "status": "PASS" if null_pct < 1 else "WARN" if null_pct < 5 else "FAIL",
        }
    
    # Leakage check (no feature should be the target)
    validation["leakage_check"]["target_in_features"] = TARGET in new_features
    
    # Range check
    range_checks = {
        "month_sin": (-1.0, 1.0),
        "month_cos": (-1.0, 1.0),
        "week_sin": (-1.0, 1.0),
        "week_cos": (-1.0, 1.0),
        "quarter": (1, 4),
        "season": (0, 3),
        "is_high_season": (0, 1),
        "is_weekend_arrival": (0, 1),
        "lead_time_bin": (0, 4),
        "short_stay": (0, 1),
        "medium_stay": (0, 1),
        "long_stay": (0, 1),
        "stay_bucket": (0, 4),
        "guest_density": (0, 7),
        "room_intensity": (0, 7),
    }
    
    for feat, (min_val, max_val) in range_checks.items():
        if feat in df_after.columns:
            actual_min = float(df_after[feat].min())
            actual_max = float(df_after[feat].max())
            valid = actual_min >= min_val and actual_max <= max_val
            validation["range_check"][feat] = {
                "min": actual_min,
                "max": actual_max,
                "expected_min": min_val,
                "expected_max": max_val,
                "status": "PASS" if valid else "FAIL",
            }
    
    return validation


def main():
    """Main execution."""
    print("=" * 60)
    print("SPRINT 5: Feature Engineering Implementation - Phase 1")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    df_before = load_raw_data()
    print(f"  Original shape: {df_before.shape}")
    print(f"  Original features: {list(df_before.columns)}")
    
    # Build features
    print("\nBuilding features...")
    df_after = build_all_features(df_before)
    print(f"  New shape: {df_after.shape}")
    
    # List new features
    new_features = [c for c in df_after.columns if c not in df_before.columns]
    print(f"  New features ({len(new_features)}): {new_features}")
    
    # Validate
    print("\nValidating features...")
    validation = validate_features(df_before, df_after)
    
    # Print validation results
    print(f"\n  Row count preserved: {validation['row_count_preserved']}")
    print(f"  Rows: {validation['rows_before']} -> {validation['rows_after']}")
    
    print("\n  Null check:")
    for feat, check in validation["null_check"].items():
        print(f"    {feat}: {check['status']} ({check['null_count']} nulls, {check['null_pct']}%)")
    
    print("\n  Leakage check:")
    print(f"    Target in features: {validation['leakage_check']['target_in_features']}")
    
    print("\n  Range check:")
    for feat, check in validation["range_check"].items():
        print(f"    {feat}: {check['status']} (min={check['min']}, max={check['max']})")
    
    # Summary
    all_pass = all(
        check["status"] == "PASS"
        for checks in [validation["null_check"], validation["range_check"]]
        for check in checks.values()
    )
    no_leakage = not validation["leakage_check"]["target_in_features"]
    
    print("\n" + "=" * 60)
    if validation["row_count_preserved"] and all_pass and no_leakage:
        print("STATUS: PASS")
        print("All features generated successfully.")
        print(f"  - {len(new_features)} new features added")
        print(f"  - {validation['rows_after']} rows preserved")
        print(f"  - No null explosion detected")
        print(f"  - No target leakage detected")
    else:
        print("STATUS: FAIL")
        if not validation["row_count_preserved"]:
            print("  - Row count not preserved")
        if not all_pass:
            print("  - Null or range check failed")
        if not no_leakage:
            print("  - Target leakage detected")
    
    print("=" * 60)
    
    return validation


if __name__ == "__main__":
    validation = main()
