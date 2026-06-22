import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_and_clean_data(data_path: str | None = None) -> pd.DataFrame:
    if data_path is None:
        data_path = os.path.join(BASE_DIR, "../../data/raw/Hotel Reservations.csv")

    df = pd.read_csv(data_path)

    df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")

    df.drop_duplicates(inplace=True)

    Q1 = df["avg_price_per_room"].quantile(0.25)
    Q3 = df["avg_price_per_room"].quantile(0.75)
    IQR = Q3 - Q1
    low = Q1 - 1.5 * IQR
    high = Q3 + 1.5 * IQR
    df = df[(df["avg_price_per_room"] >= low) & (df["avg_price_per_room"] <= high)]

    df.drop(columns=["Booking_ID"], inplace=True, errors="ignore")
    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.get_dummies(
        df,
        columns=["type_of_meal_plan", "room_type_reserved", "market_segment_type", "booking_status"],
        drop_first=True,
    )

    df["total_guests"] = df["no_of_adults"] + df["no_of_children"]
    df["total_nights"] = df["no_of_weekend_nights"] + df["no_of_week_nights"]

    arrival_dates = pd.to_datetime(
        dict(year=df["arrival_year"], month=df["arrival_month"], day=df["arrival_date"]),
        errors="coerce",
    )
    df = df[arrival_dates.notna()].copy()
    arrival_dates = arrival_dates[arrival_dates.notna()]
    df["arrival_day_of_week"] = arrival_dates.dt.weekday
    df["arrival_week_number"] = arrival_dates.dt.isocalendar().week.astype(int)

    df.drop(
        columns=["no_of_adults", "no_of_children", "no_of_weekend_nights", "no_of_week_nights",
                 "arrival_year", "arrival_month", "arrival_date"],
        inplace=True, errors="ignore",
    )

    return df


def run_pipeline(data_path: str | None = None, output_path: str | None = None) -> pd.DataFrame:
    df = load_and_clean_data(data_path)
    df = prepare_features(df)

    if output_path is None:
        output_path = os.path.join(BASE_DIR, "../../data/processed/hotel_reservations_clean.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    feature_cols = [c for c in df.columns if c != "avg_price_per_room"]
    print(f"Features: {len(feature_cols)} -> {feature_cols}")
    print(f"Procesado: {output_path} ({len(df)} filas)")
    return df


if __name__ == "__main__":
    run_pipeline()
