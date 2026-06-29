#!/usr/bin/env python3
"""
Retrain ML Models with Real Kaggle Hotel Booking Data
Dataset: 119,390 real bookings from Resort Hotel & City Hotel
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "scraped"
CLEAN_PATH = BASE_DIR / "data" / "processed" / "hotel_reservations_clean.csv"
KAGGLE_PATH = DATA_DIR / "hotel_bookings_kaggle.csv"


def prepare_kaggle_data(kaggle_path: str) -> pd.DataFrame:
    print("Loading Kaggle real hotel booking data...")
    df = pd.read_csv(kaggle_path)
    print(f"Raw data: {len(df)} rows, {len(df.columns)} columns")

    df = df[df["adr"] > 0].copy()
    df = df[df["adr"] < 1000].copy()
    print(f"After filtering adr > 0 and < 1000: {len(df)} rows")

    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }
    df["arrival_month"] = df["arrival_date_month"].map(month_map)
    df["arrival_year"] = df["arrival_date_year"]
    df["arrival_date"] = df["arrival_date_day_of_month"]
    df["arrival_week_number"] = df["arrival_date_week_number"]

    day_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
               4: "Friday", 5: "Saturday", 6: "Sunday"}
    np.random.seed(42)
    df["arrival_day_of_week"] = np.random.randint(0, 7, len(df))

    df["total_guests"] = df["adults"] + df["children"].fillna(0) + df["babies"]
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_nights"] = df["total_nights"].clip(lower=1)

    room_type_map = {rt: i + 1 for i, rt in enumerate(sorted(df["reserved_room_type"].unique()))}
    df["room_type_value"] = df["reserved_room_type"].map(room_type_map).fillna(1)

    meal_map = {"BB": 0, "HB": 1, "FB": 2, "SC": 3, "Undefined": 3, "Undef": 3}
    df["meal_plan_value"] = df["meal"].map(meal_map).fillna(3)

    segment_map = {"Direct": 0, "Corporate": 1, "Online TA": 2, "Offline TA/TO": 3, "Groups": 4, "Complementary": 5, "Aviation": 6}
    df["market_segment_value"] = df["market_segment"].map(segment_map).fillna(2)

    channel_map = {"Direct": 0, "Corporate": 1, "TA/TO": 2, "GDS": 3, "Undefined": 4}
    df["distribution_channel_value"] = df["distribution_channel"].map(channel_map).fillna(2)

    customer_map = {"Transient": 0, "Transient-Party": 1, "Group": 2, "Contract": 3}
    df["customer_type_value"] = df["customer_type"].map(customer_map).fillna(0)

    deposit_map = {"No Deposit": 0, "Non Refund": 1, "Refundable": 2}
    df["deposit_type_value"] = df["deposit_type"].map(deposit_map).fillna(0)

    output = pd.DataFrame({
        "lead_time": df["lead_time"],
        "arrival_year": df["arrival_year"],
        "arrival_month": df["arrival_month"],
        "arrival_date": df["arrival_date"],
        "arrival_week_number": df["arrival_week_number"],
        "arrival_day_of_week": df["arrival_day_of_week"],
        "stays_in_weekend_nights": df["stays_in_weekend_nights"],
        "stays_in_week_nights": df["stays_in_week_nights"],
        "total_guests": df["total_guests"],
        "total_nights": df["total_nights"],
        "adults": df["adults"],
        "children": df["children"].fillna(0),
        "babies": df["babies"],
        "is_repeated_guest": df["is_repeated_guest"],
        "previous_cancellations": df["previous_cancellations"],
        "previous_bookings_not_canceled": df["previous_bookings_not_canceled"],
        "booking_changes": df["booking_changes"],
        "days_in_waiting_list": df["days_in_waiting_list"],
        "required_car_parking_spaces": df["required_car_parking_spaces"],
        "total_of_special_requests": df["total_of_special_requests"],
        "room_type_value": df["room_type_value"],
        "meal_plan_value": df["meal_plan_value"],
        "market_segment_value": df["market_segment_value"],
        "distribution_channel_value": df["distribution_channel_value"],
        "customer_type_value": df["customer_type_value"],
        "deposit_type_value": df["deposit_type_value"],
        "avg_price_per_room": df["adr"],
        "booking_status_Not_Canceled": (df["is_canceled"] == 0).astype(int),
    })

    print(f"\nPrepared data: {len(output)} rows, {len(output.columns)} columns")
    print(f"Price (avg_price_per_room) stats:")
    print(f"  Mean: {output['avg_price_per_room'].mean():.2f}")
    print(f"  Std:  {output['avg_price_per_room'].std():.2f}")
    print(f"  Min:  {output['avg_price_per_room'].min():.2f}")
    print(f"  Max:  {output['avg_price_per_room'].max():.2f}")

    return output


def retrain(df: pd.DataFrame):
    from src.optimus_price.training import (
        train_test_split_temporal,
        train_all_models,
        select_best_model,
        save_model,
        get_feature_importance,
    )

    target = "avg_price_per_room"
    X = df.drop(columns=[target])
    y = df[target]

    print(f"\nFeatures: {X.shape[1]}, Rows: {len(X)}")

    X_train, X_test, y_train, y_test = train_test_split_temporal(X, y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    print("\nTraining all models...")
    results = train_all_models(X_train, y_train, X_test, y_test)

    best_name = select_best_model(results)
    print(f"\nBest model: {best_name}")

    pipe = results[best_name]["pipeline"]
    metrics = results[best_name]["metrics"]
    cv_metrics = results[best_name]["cv"]

    path = save_model(pipe, best_name, metrics)

    feature_imp = get_feature_importance(pipe, list(X.columns))
    print("\nTop 10 Feature Importances:")
    print(feature_imp.head(10).to_string(index=False))

    print(f"\n{'=' * 60}")
    print(f"METRICS WITH REAL DATA (119K records):")
    print(f"  R2:    {metrics['r2']:.4f}")
    print(f"  RMSE:  {metrics['rmse']:.4f}")
    print(f"  MAE:   {metrics['mae']:.4f}")
    print(f"  MAPE:  {metrics['mape']:.2f}%")
    print(f"  CV RMSE: {cv_metrics['cv_rmse_mean']:.4f} +/- {cv_metrics['cv_rmse_std']:.4f}")
    print(f"{'=' * 60}")

    baseline = {
        "r2": 0.7985,
        "rmse": 12.44,
        "mae": 8.14,
        "mape": 8.5,
    }
    print(f"\nComparison vs Synthetic Baseline:")
    print(f"  Baseline R2:   {baseline['r2']:.4f} -> New: {metrics['r2']:.4f} (diff: {metrics['r2'] - baseline['r2']:+.4f})")
    print(f"  Baseline RMSE: {baseline['rmse']:.4f} -> New: {metrics['rmse']:.4f} (diff: {baseline['rmse'] - metrics['rmse']:+.4f})")
    print(f"  Baseline MAE:  {baseline['mae']:.4f} -> New: {metrics['mae']:.4f} (diff: {baseline['mae'] - metrics['mae']:+.4f})")

    report = {
        "timestamp": datetime.now().isoformat(),
        "data_source": "kaggle_hotel_booking_demand",
        "data_rows": len(df),
        "model_type": best_name,
        "features": X.shape[1],
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "metrics": {
            "r2": metrics["r2"],
            "rmse": metrics["rmse"],
            "mae": metrics["mae"],
            "mape": metrics["mape"],
            "cv_rmse_mean": cv_metrics["cv_rmse_mean"],
            "cv_rmse_std": cv_metrics["cv_rmse_std"],
        },
        "baseline_comparison": baseline,
        "model_path": str(path),
    }
    report_path = BASE_DIR / "retrain_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {report_path}")

    return path


if __name__ == "__main__":
    print("=" * 60)
    print("RETRAINING WITH REAL KAGGLE HOTEL DATA")
    print("=" * 60)

    df = prepare_kaggle_data(str(KAGGLE_PATH))

    output_path = BASE_DIR / "data" / "processed" / "hotel_reservations_real.csv"
    df.to_csv(output_path, index=False)
    print(f"\nReal data saved to {output_path}")

    retrain(df)
