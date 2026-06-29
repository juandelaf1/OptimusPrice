"""ML Service — wraps trained model for inference"""
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE / "models" / "pipeline_trained_model.pkl"


class MLService:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self._load()

    def _load(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        self.model = joblib.load(MODEL_PATH)
        if hasattr(self.model, "feature_names_in_"):
            self.feature_names = list(self.model.feature_names_in_)
        elif hasattr(self.model, "steps"):
            last = self.model.steps[-1][1]
            if hasattr(last, "feature_names_in_"):
                self.feature_names = list(last.feature_names_in_)

    def _build_features(self, data: dict) -> dict:
        if self.feature_names is None:
            return data
        full = {}
        for col in self.feature_names:
            if col in data:
                full[col] = data[col]
            elif col == "total_guests":
                full[col] = data.get("guests", 2)
            elif col == "total_nights":
                full[col] = data.get("nights", 1)
            elif col == "lead_time":
                full[col] = data.get("lead_time", 14)
            elif col == "arrival_month":
                full[col] = data.get("month", 7)
            elif col == "arrival_year":
                full[col] = 2026
            elif col == "arrival_date":
                full[col] = 15
            elif col == "arrival_day_of_week":
                full[col] = 3
            elif col == "arrival_week_number":
                full[col] = 28
            elif col in ("required_car_parking_space", "repeated_guest",
                         "no_of_previous_cancellations",
                         "no_of_previous_bookings_not_canceled",
                         "no_of_special_requests"):
                full[col] = 0
            elif col == "booking_status_Not_Canceled":
                full[col] = 1
            elif col in ("type_of_meal_plan_Meal Plan 2", "type_of_meal_plan_Not Selected"):
                full[col] = 1 if col == "type_of_meal_plan_Not Selected" else 0
            elif col.startswith("room_type_reserved_"):
                full[col] = 1 if col == "room_type_reserved_Room_Type 4" else 0
            elif col.startswith("market_segment_type_"):
                full[col] = 1 if col == "market_segment_type_Online" else 0
            else:
                full[col] = 0
        return full

    def _compute_base_price(self, data: dict) -> float:
        guests = data.get("guests", 2)
        nights = data.get("nights", 1)
        month = data.get("month", 7)
        prop_type = data.get("property_type", "hotel")
        multipliers = {"hotel": 1.0, "airbnb": 0.9, "hostel": 0.6, "rural": 0.75}
        m = multipliers.get(prop_type, 0.8)
        base = 50 + (guests * 20) + (nights * 25) + (month - 6) * 8
        return base * m

    def predict(self, data: dict) -> dict:
        data["base_price"] = self._compute_base_price(data)
        features = self._build_features(data)
        df = pd.DataFrame([features])
        price = float(self.model.predict(df)[0])

        comp_prices = data.get("competitor_prices", {}) or {}
        comp_avg = sum(comp_prices.values()) / len(comp_prices) if comp_prices else None

        return {
            "price": round(price, 2),
            "currency": "EUR",
            "features_used": len(self.feature_names or []),
            "competitor_avg": round(comp_avg, 2) if comp_avg else None,
            "savings_vs_ota": self._calc_savings(price, comp_prices),
        }

    def _calc_savings(self, price: float, competitor_prices: dict) -> list:
        if not competitor_prices:
            return []
        results = []
        for ota, ota_price in competitor_prices.items():
            if ota_price is None:
                continue
            ota_net = ota_price * 0.85
            savings_pct = ((ota_price - price) / ota_price) * 100 if ota_price else 0
            results.append({
                "ota": ota,
                "ota_price": round(float(ota_price), 2),
                "ota_net": round(ota_net, 2),
                "optimus_price": round(price, 2),
                "savings_direct": round(price - ota_net, 2),
                "savings_pct": round(savings_pct, 1),
            })
        return results