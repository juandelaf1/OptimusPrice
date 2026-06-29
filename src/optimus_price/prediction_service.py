#!/usr/bin/env python3
"""
Optimus Price V1 — Prediction Service
Standardized prediction output with confidence and key drivers.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import joblib
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Try to import V2 market context
try:
    from src.v2_pipeline.market_context import MarketContextProvider
    MARKET_CONTEXT_AVAILABLE = True
except ImportError:
    MARKET_CONTEXT_AVAILABLE = False


@dataclass
class PredictionResult:
    """Standardized V1 prediction output with optional V2 market context."""
    predicted_price: float
    confidence_range: Dict[str, float]
    key_drivers: List[Dict[str, float]]
    model_info: Dict[str, str]
    metadata: Dict[str, any]
    market_context: Optional[Dict] = None


class PredictionService:
    """
    V1 Prediction Service.
    
    Produces standardized output:
    {
        "predicted_price": float,
        "confidence_range": {"low": float, "high": float},
        "key_drivers": [{"feature": str, "impact": float}],
        "model_info": {"model": str, "r2": float}
    }
    """

    def __init__(self):
        self.pipeline = None
        self.feature_names = None
        self.model_info = None

    def load(self, model_path: Optional[str] = None) -> bool:
        """Load trained model."""
        try:
            if model_path is None:
                model_path = MODELS_DIR / "pipeline_trained_model.pkl"
            
            self.pipeline = joblib.load(model_path)
            
            # Load metadata if available
            metadata_path = MODELS_DIR / "model_metadata.yaml"
            if metadata_path.exists():
                import yaml
                with open(metadata_path) as f:
                    metadata = yaml.safe_load(f)
                # Get the latest model info
                for model_name, info in metadata.items():
                    if info.get("file", "").startswith("pipeline_elasticnet"):
                        self.model_info = {
                            "model": model_name,
                            "r2": info.get("metrics", {}).get("r2", 0.3467),
                            "rmse": info.get("metrics", {}).get("rmse", 31.79),
                            "mae": info.get("metrics", {}).get("mae", 24.39),
                            "mape": info.get("metrics", {}).get("mape", 23.83),
                        }
                        break
            
            if self.model_info is None:
                self.model_info = {
                    "model": "ElasticNet",
                    "r2": 0.3467,
                    "rmse": 31.79,
                    "mae": 24.39,
                    "mape": 23.83,
                }
            
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def _build_features(self, input_data: Dict) -> np.ndarray:
        """Build feature array from input dictionary."""
        # Feature order must match training data
        features = np.array([[
            input_data.get("room_type_value", 0),
            input_data.get("arrival_year", 2017),
            input_data.get("market_segment_value", 0),
            input_data.get("total_guests", 2),
            input_data.get("children", 0),
            input_data.get("arrival_month", 6),
            input_data.get("lead_time", 30),
            input_data.get("booking_status_Not_Canceled", 1),
            input_data.get("arrival_week_number", 26),
            input_data.get("distribution_channel_value", 0),
            input_data.get("meal_plan_value", 0),
            input_data.get("deposit_type_value", 0),
            input_data.get("adults", 2),
            input_data.get("total_of_special_requests", 0),
            input_data.get("arrival_date", 15),
            input_data.get("booking_changes", 0),
            input_data.get("customer_type_value", 0),
            input_data.get("previous_cancellations", 0),
            input_data.get("stays_in_weekend_nights", 0),
            input_data.get("previous_bookings_not_canceled", 0),
            input_data.get("stays_in_week_nights", 3),
            input_data.get("required_car_parking_spaces", 0),
            input_data.get("days_in_waiting_list", 0),
            input_data.get("is_repeated_guest", 0),
            input_data.get("arrival_day_of_week", 0),
            input_data.get("total_nights", 3),
            input_data.get("babies", 0),
        ]])
        return features

    def _get_confidence_range(self, prediction: float, rmse: float = 31.79) -> Dict[str, float]:
        """
        Calculate confidence range based on model RMSE.
        
        Uses ±1 RMSE as the confidence interval (~68% coverage).
        """
        return {
            "low": max(0, round(prediction - rmse, 2)),
            "high": round(prediction + rmse, 2),
        }

    def _get_key_drivers(self, features: np.ndarray, top_n: int = 5) -> List[Dict[str, float]]:
        """
        Get top feature drivers based on coefficient magnitude.
        
        Returns features with highest absolute impact on prediction.
        """
        if self.pipeline is None:
            return []
        
        model = self.pipeline.named_steps.get("model")
        if model is None or not hasattr(model, "coef_"):
            return []
        
        # Get feature names
        feature_names = [
            "room_type_value", "arrival_year", "market_segment_value",
            "total_guests", "children", "arrival_month", "lead_time",
            "booking_status", "arrival_week_number", "distribution_channel",
            "meal_plan", "deposit_type", "adults", "special_requests",
            "arrival_date", "booking_changes", "customer_type",
            "previous_cancellations", "weekend_nights", "previous_bookings",
            "week_nights", "parking_spaces", "waiting_list",
            "repeated_guest", "arrival_day_of_week", "total_nights", "babies"
        ]
        
        coefs = model.coef_
        
        # Calculate impact = coefficient * feature_value
        impacts = []
        for i, (name, coef, val) in enumerate(zip(feature_names, coefs, features[0])):
            impact = coef * val
            impacts.append({"feature": name, "impact": round(float(impact), 2)})
        
        # Sort by absolute impact
        impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        return impacts[:top_n]

    def predict(self, input_data: Dict, include_market_context: bool = False) -> PredictionResult:
        """
        Make prediction with standardized V1 output.
        
        Args:
            input_data: Dictionary with feature values
            include_market_context: If True, include V2 market context in result
            
        Returns:
            PredictionResult with predicted_price, confidence_range, key_drivers, model_info
        """
        if self.pipeline is None:
            raise ValueError("Model not loaded. Call load() first.")
        
        # Build features
        features = self._build_features(input_data)
        
        # Make prediction
        prediction = self.pipeline.predict(features)[0]
        prediction = max(0, round(float(prediction), 2))
        
        # Get confidence range
        rmse = self.model_info.get("rmse", 31.79)
        confidence_range = self._get_confidence_range(prediction, rmse)
        
        # Get key drivers
        key_drivers = self._get_key_drivers(features)
        
        # Get market context if requested
        market_context = None
        if include_market_context and MARKET_CONTEXT_AVAILABLE:
            try:
                from datetime import date
                arrival_month = input_data.get("arrival_month", 6)
                year = input_data.get("arrival_year", 2025)
                target_date = date(year, arrival_month, 15)
                
                ctx_provider = MarketContextProvider()
                ctx_result = ctx_provider.adjust_prediction(
                    base_price=prediction,
                    region='mallorca',
                    segment='playa_costa',
                    target_date=target_date,
                )
                market_context = ctx_result.get('context')
            except Exception:
                pass
        
        # Build result
        result = PredictionResult(
            predicted_price=prediction,
            confidence_range=confidence_range,
            key_drivers=key_drivers,
            model_info=self.model_info,
            metadata={
                "nights": input_data.get("total_nights", 1),
                "guests": input_data.get("total_guests", 1),
                "room_type": input_data.get("room_type_value", 0),
                "arrival_month": input_data.get("arrival_month", 0),
            },
            market_context=market_context,
        )
        
        return result

    def predict_to_json(self, input_data: Dict) -> str:
        """Return prediction as JSON string."""
        result = self.predict(input_data)
        return json.dumps(asdict(result), indent=2)


# Convenience function
def predict_price(input_data: Dict, model_path: Optional[str] = None, include_market_context: bool = False) -> Dict:
    """
    Convenience function for V1 prediction.
    
    Returns standardized dict:
    {
        "predicted_price": float,
        "confidence_range": {"low": float, "high": float},
        "key_drivers": [{"feature": str, "impact": float}],
        "model_info": {"model": str, "r2": float},
        "market_context": {...} (if include_market_context=True)
    }
    """
    service = PredictionService()
    if not service.load(model_path):
        raise ValueError("Failed to load model")
    
    result = service.predict(input_data, include_market_context=include_market_context)
    return asdict(result)


if __name__ == "__main__":
    # Test prediction
    test_input = {
        "room_type_value": 1,
        "arrival_year": 2017,
        "market_segment_value": 0,
        "total_guests": 2,
        "children": 0,
        "arrival_month": 7,
        "lead_time": 30,
        "booking_status_Not_Canceled": 1,
        "arrival_week_number": 27,
        "distribution_channel_value": 0,
        "meal_plan_value": 1,
        "deposit_type_value": 0,
        "adults": 2,
        "total_of_special_requests": 1,
        "arrival_date": 15,
        "booking_changes": 0,
        "customer_type_value": 0,
        "previous_cancellations": 0,
        "stays_in_weekend_nights": 2,
        "previous_bookings_not_canceled": 0,
        "stays_in_week_nights": 3,
        "required_car_parking_spaces": 0,
        "days_in_waiting_list": 0,
        "is_repeated_guest": 0,
        "arrival_day_of_week": 5,
        "total_nights": 5,
        "babies": 0,
    }
    
    result = predict_price(test_input)
    print(json.dumps(result, indent=2))
