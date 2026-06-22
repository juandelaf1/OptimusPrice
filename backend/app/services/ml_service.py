"""ML Service — wraps trained model for inference"""
import os, sys, json
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
        """Build full 41-feature vector from simple input"""
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
            elif col.startswith("competitor_price_"):
                ota = col.replace("competitor_price_", "")
                scraped = data.get("competitor_prices", {}).get(ota)
                full[col] = scraped if scraped else data.get("base_price", 100) * np.random.uniform(0.85, 1.15)
            elif col == "competitor_min_price":
                prices = data.get("competitor_prices", {})
                full[col] = min(prices.values()) if prices else data.get("base_price", 100) * 0.9
            elif col == "competitor_max_price":
                prices = data.get("competitor_prices", {})
                full[col] = max(prices.values()) if prices else data.get("base_price", 100) * 1.1
            elif col == "competitor_avg_price":
                prices = data.get("competitor_prices", {})
                vals = list(prices.values())
                full[col] = sum(vals) / len(vals) if vals else data.get("base_price", 100)
            elif col == "competitor_price_std":
                prices = data.get("competitor_prices", {}).values()
                full[col] = np.std(list(prices)) if prices else 0
            elif col == "price_vs_competitors":
                full[col] = 0.05
            elif col == "price_advantage":
                full[col] = 0.05
            elif col == "is_cheapest":
                full[col] = 0
            elif col == "competitor_count":
                full[col] = len(data.get("competitor_prices", {}))
            elif col == "price_volatility":
                full[col] = 0.02
            elif col in ("price_position_below", "price_position_above"):
                full[col] = 0
            else:
                full[col] = 0
        return full

    def predict(self, data: dict) -> dict:
        """Predict optimal price"""
        features = self._build_features(data)
        df = pd.DataFrame([features])
        price = float(self.model.predict(df)[0])

        base_price = data.get("base_price", price)
        competitor_prices = data.get("competitor_prices", {})
        comp_avg = sum(competitor_prices.values()) / len(competitor_prices) if competitor_prices else None

        return {
            "price": round(price, 2),
            "currency": "EUR",
            "features_used": len(self.feature_names or []),
            "competitor_avg": round(comp_avg, 2) if comp_avg else None,
            "savings_vs_ota": self._calc_savings(price, competitor_prices, base_price),
        }

    def _calc_savings(self, price, competitor_prices, base_price):
        """Calculate savings vs OTA channels (15-30% commission)"""
        results = []
        for ota, ota_price in competitor_prices.items():
            ota_net = ota_price * 0.85  # 15% commission
            savings = abs(ota_price - price)
            results.append({
                "ota": ota,
                "ota_price": round(ota_price, 2),
                "ota_net": round(ota_net, 2),
                "optimus_price": round(price, 2),
                "savings_direct": round(price - ota_net, 2),
                "savings_pct": round(((ota_price - price) / ota_price) * 100, 1),
            })
        return results
