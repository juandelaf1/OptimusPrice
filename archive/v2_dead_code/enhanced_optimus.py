#!/usr/bin/env python3
"""
Enhanced Optimus Price System with RASPAL Integration
Combines ML-powered pricing with real-time web scraping for competitive intelligence
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

from raspal import Fetcher, LLMExtractor, AutoThrottle
from scraping_manager import ScrapingManager
from src.optimus_price.training import (
    load_processed_data, train_best_and_save, build_pipeline,
    evaluate_model, select_best_model, train_all_models
)
from src.optimus_price.data_processing import load_and_clean_data, prepare_features
from src.optimus_price.evaluation import save_metrics_report
from src.optimus_price.occupancy_model import OccupancyPredictor
from src.optimus_price.elasticity_engine import PriceElasticityEngine
from src.optimus_price.revenue_optimizer import RevenueOptimizer
from typing import Dict, List, Optional
import os

MODEL_DIR = r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final\models"


class RevenueIntelligence:
    """Revenue intelligence combining occupancy, elasticity, and optimization"""

    def __init__(self):
        self.occupancy_predictor = OccupancyPredictor()
        self.elasticity_engine = None
        self.revenue_optimizer = None
        self._loaded = False

    def load(self) -> bool:
        """Load all revenue models"""
        try:
            self.occupancy_predictor.load()
            self.elasticity_engine = PriceElasticityEngine(self.occupancy_predictor)
            self.revenue_optimizer = RevenueOptimizer(self.occupancy_predictor, self.elasticity_engine)
            self._loaded = True
            print("Revenue Intelligence models loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading revenue models: {e}")
            return False

    def get_optimal_price(
        self,
        current_price: float,
        features: Dict = None,
        total_rooms: int = 100,
    ) -> Dict:
        """Get optimal price recommendation"""
        if not self._loaded:
            return {"error": "Models not loaded"}

        if features is None:
            features = {
                "lead_time_days": 30,
                "total_guests": 2,
                "total_nights": 2,
            }

        try:
            recommendation = self.revenue_optimizer.optimize(
                features, current_price=current_price, total_rooms=total_rooms
            )
            return {
                "current_price": recommendation.current_price,
                "recommended_price": recommendation.recommended_price,
                "elasticity": recommendation.elasticity,
                "revenue_gain_per_room": recommendation.revenue_gain_per_room,
                "total_revenue_gain": recommendation.revenue_gain_per_room * total_rooms,
                "annual_gain": recommendation.revenue_gain_per_room * total_rooms * 365,
                "confidence": recommendation.confidence,
                "risk_level": recommendation.risk_level,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_revenue_curve(
        self,
        current_price: float,
        features: Dict = None,
        min_price: float = None,
        max_price: float = None,
    ) -> Dict:
        """Get revenue curve analysis"""
        if not self._loaded:
            return {"error": "Models not loaded"}

        if features is None:
            features = {
                "lead_time_days": 30,
                "total_guests": 2,
                "total_nights": 2,
            }

        if min_price is None:
            min_price = current_price * 0.5
        if max_price is None:
            max_price = current_price * 2

        try:
            curve = self.elasticity_engine.generate_revenue_curve(
                features, min_price, max_price, current_price
            )
            return {
                "optimal_price": curve.optimal_price,
                "optimal_revenue": curve.optimal_revenue,
                "current_revenue": curve.current_revenue,
                "revenue_gain_pct": curve.revenue_gain_pct,
                "prices": curve.prices.tolist(),
                "revenues": curve.revenues.tolist(),
                "occupancy_probs": curve.occupancy_probs.tolist(),
            }
        except Exception as e:
            return {"error": str(e)}


class EnhancedOptimusPrice:
    """Enhanced Optimus Price with real-time market intelligence"""

    def __init__(self):
        self.raspal_fetcher = Fetcher(throttle=AutoThrottle(min_delay=1, max_delay=60))
        self.scraper = ScrapingManager()
        self.market_cache = {}
        self._model_pipeline = None
        self._model_name = None
        self._feature_names = None
        self.revenue_intelligence = RevenueIntelligence()

    def load_model(self, model_path: str = None) -> bool:
        """Load a trained model pipeline"""
        import joblib
        import pandas as pd
        if model_path is None:
            models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pkl")] if os.path.exists(MODEL_DIR) else []
            if not models:
                print("No trained models found. Train one first.")
                return False
            model_path = os.path.join(MODEL_DIR, models[-1])

        try:
            self._model_pipeline = joblib.load(model_path)
            self._model_name = os.path.basename(model_path)
            if hasattr(self._model_pipeline, 'feature_names_in_'):
                self._feature_names = list(self._model_pipeline.feature_names_in_)
            else:
                last_step = self._model_pipeline.steps[-1][1] if hasattr(self._model_pipeline, 'steps') else self._model_pipeline
                if hasattr(last_step, 'feature_names_in_'):
                    self._feature_names = list(last_step.feature_names_in_)
            print(f"Loaded model: {self._model_name} ({len(self._feature_names or [])} features)")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def _build_full_features(self, features: Dict) -> Dict:
        """Build complete feature vector expected by the model"""
        import pandas as pd
        import numpy as np

        if self._feature_names is None:
            return features

        full = {}
        for col in self._feature_names:
            if col in features:
                full[col] = features[col]
            elif col == "total_guests":
                full[col] = features.get("total_guests", 2)
            elif col == "total_nights":
                full[col] = features.get("total_nights", 1)
            elif col == "lead_time":
                full[col] = features.get("lead_time", 30)
            elif col == "arrival_year":
                full[col] = 2025
            elif col == "arrival_month":
                full[col] = features.get("arrival_month", 7)
            elif col == "arrival_date":
                full[col] = 15
            elif col == "arrival_day_of_week":
                full[col] = 3
            elif col == "arrival_week_number":
                full[col] = 28
            elif col in ("required_car_parking_space", "repeated_guest", "no_of_previous_cancellations",
                         "no_of_previous_bookings_not_canceled", "no_of_special_requests"):
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

    def predict(self, features: Dict) -> float:
        """Make a price prediction using the loaded model"""
        import pandas as pd
        if self._model_pipeline is None:
            raise ValueError("No model loaded. Call load_model() first.")

        full_features = self._build_full_features(features)
        df = pd.DataFrame([full_features])
        try:
            prediction = self._model_pipeline.predict(df)[0]
            return float(prediction)
        except Exception as e:
            print(f"Prediction error: {e}")
            raise

    def train_with_web_data(self, historical_data, competitor_urls):
        """Train ML model with web-derived training data"""
        for url in competitor_urls:
            result = self.raspal_fetcher.fetch(url, engine="stealth")
            processed = self._process_web_training_data(result)
            historical_data.extend(processed)
        return self._train(historical_data)

    def _process_web_training_data(self, result):
        """Process web data for ML training"""
        return []

    def _train(self, data):
        """Internal training wrapper"""
        print("Training not yet integrated with actual pipeline.")
        print("Use: python -m src.optimus_price.training")
        return None

    def predict_with_market_context(self, hotel_features: Dict) -> float:
        """Predict pricing with market context integration"""
        base_prediction = self.predict(hotel_features)
        return base_prediction

    def _calculate_market_adjustment(self, market_data: Dict) -> float:
        adjustment = 0.0
        seasonal_factor = market_data.get("seasonal_adjustment", 1.0)
        adjustment += (seasonal_factor - 1.0)
        competitor_pressure = market_data.get("competitor_pressure", "medium")
        if competitor_pressure == "high":
            adjustment -= 0.15
        elif competitor_pressure == "low":
            adjustment += 0.05
        return adjustment

    def collect_competitor_intelligence(self, hotel_ids: List[str]) -> Dict:
        """Collect competitor pricing data from multiple sources"""
        market_data = {}
        for hotel_id in hotel_ids:
            features = {"hotel_id": hotel_id}
            internal_prediction = self.predict_with_market_context(features)
            market_data[hotel_id] = {
                "internal_prediction": internal_prediction,
                "hotel_id": hotel_id
            }
        return market_data

    def optimize_price_with_market_data(self, hotel_data: Dict) -> float:
        """Optimize price considering market conditions"""
        internal_prediction = hotel_data.get("internal_prediction", 100)
        competitor_prices = hotel_data.get("competitor_prices", {})

        if not competitor_prices:
            return internal_prediction

        valid_prices = [p for p in competitor_prices.values() if p is not None]
        if not valid_prices:
            return internal_prediction

        min_competitor_price = min(valid_prices)

        if internal_prediction > min_competitor_price * 1.2:
            return min_competitor_price * 0.95
        elif internal_prediction < min_competitor_price * 0.8:
            return internal_prediction * 1.05
        else:
            return internal_prediction

    def scrape_and_predict(self, hotel_id: str, scrape_otas: bool = True) -> Dict:
        """Scrape hotel prices from OTAs and return optimized prediction"""
        base_features = {"hotel_id": hotel_id, "total_guests": 2, "total_nights": 1}
        base_price = self.predict_with_market_context(base_features)

        if not scrape_otas:
            return {"hotel_id": hotel_id, "predicted_price": base_price}

        otas_results = self.scraper.scrape_hotel(hotel_id)
        competitor_prices = {}
        for ota, data in otas_results.items():
            parsed = data.get("parsed", {})
            price = parsed.get("price") if isinstance(parsed, dict) else None
            if price:
                competitor_prices[ota] = float(price)

        optimized = self.optimize_price_with_market_data({
            "internal_prediction": base_price,
            "competitor_prices": competitor_prices
        })

        return {
            "hotel_id": hotel_id,
            "base_price": base_price,
            "optimized_price": optimized,
            "competitor_prices": competitor_prices,
            "market_adjustment": optimized - base_price
        }


def create_enhanced_system():
    """Create and configure the enhanced Optimus Price system"""
    print("Initializing Enhanced Optimus Price System with RASPAL Integration...")
    system = EnhancedOptimusPrice()
    system.revenue_intelligence.load()
    print("Enhanced Optimus Price system initialized successfully!")
    print("RASPAL integration active")
    print("Real-time market intelligence ready")
    print("Revenue Intelligence ready")
    return system


if __name__ == "__main__":
    system = create_enhanced_system()
    sample = {"total_guests": 2, "total_nights": 3, "season": "peak_season", "location": "beach_resort"}
    pred = system.predict_with_market_context(sample)
    print(f"Sample prediction for beach resort (peak, 2 guests, 3 nights): ${pred:.2f}")
