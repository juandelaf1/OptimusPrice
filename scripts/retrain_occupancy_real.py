#!/usr/bin/env python3
"""
Retrain Occupancy Model with Real Kaggle Data
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
KAGGLE_PATH = BASE_DIR / "data" / "scraped" / "hotel_bookings_kaggle.csv"


def prepare_occupancy_data(kaggle_path: str) -> pd.DataFrame:
    df = pd.read_csv(kaggle_path)
    print(f"Raw: {len(df)} rows")

    df = df[df["adr"] > 0].copy()
    df = df[df["adr"] < 1000].copy()
    print(f"After filtering: {len(df)} rows")

    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }
    df["month"] = df["arrival_date_month"].map(month_map)
    df["total_guests"] = df["adults"] + df["children"].fillna(0) + df["babies"]
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_nights"] = df["total_nights"].clip(lower=1)

    room_map = {rt: i + 1 for i, rt in enumerate(sorted(df["reserved_room_type"].unique()))}
    df["room_type_value"] = df["reserved_room_type"].map(room_map).fillna(1)

    np.random.seed(42)
    df["arrival_day_of_week"] = np.random.randint(0, 7, len(df))
    df["is_weekend"] = (df["arrival_day_of_week"] >= 5).astype(int)

    season_factor = {
        1: 0.70, 2: 0.65, 3: 0.75, 4: 0.85,
        5: 0.90, 6: 1.25, 7: 1.40, 8: 1.35,
        9: 0.95, 10: 0.85, 11: 0.75, 12: 1.20,
    }
    df["season_factor"] = df["month"].map(season_factor).fillna(1.0)

    df["is_last_minute"] = (df["lead_time"] < 7).astype(int)
    df["is_early_bird"] = (df["lead_time"] > 60).astype(int)

    df["is_online_booking"] = (df["market_segment"] == "Online TA").astype(int)

    meal_cols = {"BB": 0, "HB": 1, "FB": 2, "SC": 3}
    df["has_meal_plan"] = df["meal"].map(meal_cols).fillna(3).apply(lambda x: 0 if x == 3 else 1)

    output = pd.DataFrame({
        "room_price": df["adr"],
        "price_vs_market": 1.0,
        "month": df["month"],
        "season_factor": df["season_factor"],
        "is_weekend": df["is_weekend"],
        "lead_time_days": df["lead_time"],
        "is_last_minute": df["is_last_minute"],
        "is_early_bird": df["is_early_bird"],
        "total_guests": df["total_guests"],
        "total_nights": df["total_nights"],
        "special_requests": df["total_of_special_requests"],
        "is_repeated_guest": df["is_repeated_guest"],
        "is_online_booking": df["is_online_booking"],
        "has_meal_plan": df["has_meal_plan"],
        "room_type_value": df["room_type_value"],
        "requires_parking": df["required_car_parking_spaces"],
        "is_occupied": (df["is_canceled"] == 0).astype(int),
    })

    print(f"Prepared: {len(output)} rows, {len(output.columns)} columns")
    print(f"Occupancy rate: {output['is_occupied'].mean():.3f}")
    return output


def retrain_occupancy(df: pd.DataFrame):
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss, log_loss
    from sklearn.pipeline import Pipeline as SkPipeline
    from sklearn.preprocessing import StandardScaler
    import joblib

    target = "is_occupied"
    feature_cols = [c for c in df.columns if c != target]
    X = df[feature_cols]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    pipeline = SkPipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        )),
    ])

    print("Training occupancy model...")
    pipeline.fit(X_train, y_train)

    print("Calibrating probabilities...")
    calibrated = CalibratedClassifierCV(pipeline, method="sigmoid", cv=3)
    calibrated.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = calibrated.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    brier = brier_score_loss(y_test, y_proba)
    ll = log_loss(y_test, y_proba)

    print(f"\nOccupancy Model Metrics (Real Data):")
    print(f"  accuracy:  {acc:.4f}")
    print(f"  auc_roc:   {auc:.4f}")
    print(f"  brier:     {brier:.4f}")
    print(f"  log_loss:  {ll:.4f}")
    print(f"  train:     {len(X_train)}")
    print(f"  test:      {len(X_test)}")

    model_path = BASE_DIR / "models" / "occupancy_predictor.pkl"
    joblib.dump({
        "model": pipeline,
        "calibrated_model": calibrated,
        "feature_names": list(feature_cols),
        "is_fitted": True,
        "metrics": {"accuracy": acc, "auc_roc": auc, "brier": brier, "log_loss": ll},
    }, model_path)
    print(f"\nSaved to: {model_path}")

    print(f"\nComparison vs Synthetic Baseline:")
    print(f"  Baseline accuracy: 0.8708 -> New: {acc:.4f}")
    print(f"  Baseline AUC:      0.9354 -> New: {auc:.4f}")

    return str(model_path)


if __name__ == "__main__":
    print("=" * 60)
    print("RETRAINING OCCUPANCY MODEL WITH REAL DATA")
    print("=" * 60)

    df = prepare_occupancy_data(str(KAGGLE_PATH))
    retrain_occupancy(df)

    print("\n--- Testing predictions ---")
    from src.optimus_price.occupancy_model import OccupancyPredictor
    predictor = OccupancyPredictor()
    predictor.load()

    prices = [60, 80, 100, 120, 150, 200]
    for price in prices:
        occ = predictor.predict_single({}, price)
        rev = occ * price * 100
        print(f"  Price ${price:3d} -> Occ: {occ*100:5.1f}% -> Revenue: ${rev:,.0f}")
