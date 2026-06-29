#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Occupancy Prediction Model for Optimus Price
Predicts occupancy probability at different price points.
Occupancy = f(price, seasonality, lead_time, competitors, demand)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    roc_auc_score, brier_score_loss, log_loss,
    classification_report, confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
import joblib
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"


class OccupancyPredictor:
    """
    Predicts occupancy probability at different price points.
    
    Used for:
    - Revenue optimization: Revenue = Occupancy(price) x Price
    - Price elasticity estimation
    - Dynamic pricing recommendations
    """

    def __init__(self):
        self.model = None
        self.calibrated_model = None
        self.feature_names = None
        self.is_fitted = False

    def prepare_features(
        self,
        df: pd.DataFrame,
        target_price: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Prepare features for occupancy prediction.
        
        Args:
            df: Raw booking/hotel data
            target_price: If provided, use this as the proposed room price
            
        Returns:
            DataFrame with engineered features for occupancy prediction
        """
        features = pd.DataFrame()

        # Price features (if target_price provided, override)
        if target_price is not None:
            features["room_price"] = target_price
        elif "avg_price_per_room" in df.columns:
            features["room_price"] = df["avg_price_per_room"]
        else:
            features["room_price"] = 100.0  # default

        # Price vs market (from historical data)
        if "avg_price_per_room" in df.columns:
            market_avg = df["avg_price_per_room"].rolling(window=30, min_periods=1).mean()
            features["price_vs_market"] = features["room_price"] / (market_avg + 1)
        else:
            features["price_vs_market"] = 1.0

        # Seasonality features
        if "arrival_month" in df.columns:
            features["month"] = df["arrival_month"]
            season_factor = {
                1: 0.70, 2: 0.65, 3: 0.75, 4: 0.85,
                5: 0.90, 6: 1.25, 7: 1.40, 8: 1.35,
                9: 0.95, 10: 0.85, 11: 0.75, 12: 1.20,
            }
            features["season_factor"] = features["month"].map(season_factor).fillna(1.0)
        else:
            features["month"] = 6
            features["season_factor"] = 1.0

        if "arrival_day_of_week" in df.columns:
            features["is_weekend"] = (df["arrival_day_of_week"] >= 5).astype(int)
        else:
            features["is_weekend"] = 0

        # Lead time features
        if "lead_time" in df.columns:
            features["lead_time_days"] = df["lead_time"]
            features["is_last_minute"] = (df["lead_time"] < 7).astype(int)
            features["is_early_bird"] = (df["lead_time"] > 60).astype(int)
        else:
            features["lead_time_days"] = 30
            features["is_last_minute"] = 0
            features["is_early_bird"] = 0

        # Guest features
        if "total_guests" in df.columns:
            features["total_guests"] = df["total_guests"]
        else:
            features["total_guests"] = 2

        if "total_nights" in df.columns:
            features["total_nights"] = df["total_nights"]
        else:
            features["total_nights"] = 1

        # Booking behavior features
        if "no_of_special_requests" in df.columns:
            features["special_requests"] = df["no_of_special_requests"]
        else:
            features["special_requests"] = 0

        if "repeated_guest" in df.columns:
            features["is_repeated_guest"] = df["repeated_guest"]
        else:
            features["is_repeated_guest"] = 0

        # Market segment
        if "market_segment_type_Online" in df.columns:
            features["is_online_booking"] = df["market_segment_type_Online"].astype(int)
        else:
            features["is_online_booking"] = 1

        # Meal plan value
        meal_cols = [c for c in df.columns if c.startswith("type_of_meal_plan_")]
        if meal_cols:
            features["has_meal_plan"] = (df[meal_cols].sum(axis=1) > 0).astype(int)
        else:
            features["has_meal_plan"] = 0

        # Room type value indicator
        room_cols = [c for c in df.columns if c.startswith("room_type_reserved_")]
        if room_cols:
            # Higher room type number = higher value
            room_values = {}
            for i, col in enumerate(sorted(room_cols)):
                room_values[col] = i + 1
            features["room_type_value"] = sum(
                df[col].astype(int) * val for col, val in room_values.items()
            )
        else:
            features["room_type_value"] = 1

        # Parking (amenity demand proxy)
        if "required_car_parking_space" in df.columns:
            features["requires_parking"] = df["required_car_parking_space"]
        else:
            features["requires_parking"] = 0

        # NOTE: booking_status is the TARGET proxy, NOT a feature
        # Including it would cause target leakage. Do not add it here.

        self.feature_names = list(features.columns)
        return features

    def create_occupancy_target(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Create occupancy target variable.
        
        In real usage, this would be the actual occupancy rate.
        For synthetic data, we simulate occupancy based on booking patterns.
        
        Logic:
        - Not Canceled = 1 (occupied)
        - Canceled = 0 (not occupied)
        """
        if "booking_status_Not_Canceled" in df.columns:
            return df["booking_status_Not_Canceled"].astype(int)
        else:
            # Default: 70% occupancy
            return pd.Series(np.ones(len(df)), index=df.index)

    def train(
        self,
        df: pd.DataFrame,
        calibrate: bool = True,
    ) -> Dict:
        """
        Train the occupancy prediction model.
        
        Args:
            df: Training data with booking features
            calibrate: Whether to calibrate probabilities
            
        Returns:
            Dictionary with training metrics
        """
        from sklearn.ensemble import GradientBoostingClassifier

        print("Preparing features...")
        X = self.prepare_features(df)
        y = self.create_occupancy_target(df)

        print(f"Features: {X.shape[1]}, Samples: {len(X)}")
        print(f"Occupancy rate: {y.mean():.3f} ({y.sum()}/{len(y)})")

        # Time-series split
        split_idx = int(len(X) * 0.8)
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

        print(f"Train: {len(X_train)}, Test: {len(X_test)}")

        # Build pipeline
        self.model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
            )),
        ])

        print("Training occupancy model...")
        self.model.fit(X_train, y_train)

        # Calibrate probabilities
        if calibrate:
            print("Calibrating probabilities...")
            self.calibrated_model = CalibratedClassifierCV(
                self.model, cv=3, method="sigmoid"
            )
            self.calibrated_model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        if self.calibrated_model:
            y_prob_cal = self.calibrated_model.predict_proba(X_test)[:, 1]
        else:
            y_prob_cal = y_prob

        metrics = {
            "accuracy": float((y_pred == y_test).mean()),
            "auc_roc": float(roc_auc_score(y_test, y_prob_cal)),
            "brier_score": float(brier_score_loss(y_test, y_prob_cal)),
            "log_loss": float(log_loss(y_test, y_prob_cal)),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "occupancy_rate_train": float(y_train.mean()),
            "occupancy_rate_test": float(y_test.mean()),
        }

        print("\nOccupancy Model Metrics:")
        for k, v in metrics.items():
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

        self.is_fitted = True
        return metrics

    def predict_occupancy(
        self,
        df: pd.DataFrame,
        prices: Optional[List[float]] = None,
    ) -> pd.DataFrame:
        """
        Predict occupancy at different price points.
        
        Args:
            df: Hotel/booking data
            prices: List of prices to test. If None, uses current price.
            
        Returns:
            DataFrame with columns: price, occupancy_probability, expected_revenue
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")

        if prices is None:
            prices = [100.0]

        results = []
        for price in prices:
            X = self.prepare_features(df, target_price=price)

            if self.calibrated_model:
                occ_prob = self.calibrated_model.predict_proba(X)[:, 1]
            else:
                occ_prob = self.model.predict_proba(X)[:, 1]

            avg_occ = occ_prob.mean()
            expected_revenue = avg_occ * price

            results.append({
                "price": price,
                "occupancy_probability": avg_occ,
                "expected_revenue_per_room": expected_revenue,
                "n_samples": len(df),
            })

        return pd.DataFrame(results)

    def predict_single(
        self,
        features: Dict,
        price: float,
    ) -> float:
        """Predict occupancy for a single observation."""
        if not self.is_fitted:
            raise ValueError("Model not trained.")

        # Build feature vector directly with defaults
        feature_vector = {
            "room_price": price,
            "price_vs_market": 1.0,
            "month": 6,
            "season_factor": 1.0,
            "is_weekend": 0,
            "lead_time_days": features.get("lead_time_days", 30),
            "is_last_minute": 0,
            "is_early_bird": 0,
            "total_guests": features.get("total_guests", 2),
            "total_nights": features.get("total_nights", 1),
            "special_requests": features.get("special_requests", 0),
            "is_repeated_guest": features.get("is_repeated_guest", 0),
            "is_online_booking": 1,
            "has_meal_plan": 1,
            "room_type_value": features.get("room_type_value", 2),
            "requires_parking": features.get("requires_parking", 0),
        }

        # Ensure correct feature order
        X = pd.DataFrame([feature_vector])
        # Reorder to match training order
        if self.feature_names is not None:
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0
            X = X[self.feature_names]

        if self.calibrated_model:
            return float(self.calibrated_model.predict_proba(X)[:, 1][0])
        else:
            return float(self.model.predict_proba(X)[:, 1][0])

    def save(self, path: Optional[str] = None) -> str:
        """Save the trained model."""
        if path is None:
            path = str(MODELS_DIR / "occupancy_predictor.pkl")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "calibrated_model": self.calibrated_model,
            "feature_names": self.feature_names,
            "is_fitted": self.is_fitted,
        }, path)
        print(f"Occupancy model saved: {path}")
        return path

    def load(self, path: Optional[str] = None) -> bool:
        """Load a trained model."""
        if path is None:
            path = str(MODELS_DIR / "occupancy_predictor.pkl")

        try:
            data = joblib.load(path)
            self.model = data["model"]
            self.calibrated_model = data["calibrated_model"]
            self.feature_names = data["feature_names"]
            self.is_fitted = data["is_fitted"]
            print(f"Occupancy model loaded: {path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


def train_occupancy_model():
    """Train and save the occupancy prediction model."""
    print("=" * 60)
    print("TRAINING OCCUPANCY PREDICTION MODEL")
    print("=" * 60)

    # Load data
    data_path = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
    if not data_path.exists():
        print(f"Data not found: {data_path}")
        return None

    df = pd.read_csv(data_path)
    print(f"Data: {len(df)} rows, {len(df.columns)} columns")

    # Train model
    predictor = OccupancyPredictor()
    metrics = predictor.train(df, calibrate=True)

    # Save model
    model_path = predictor.save()

    print(f"\nModel saved to: {model_path}")
    return predictor


if __name__ == "__main__":
    train_occupancy_model()
