#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Price Elasticity Framework for Optimus Price
Calculates price elasticity and generates revenue optimization recommendations.
Revenue(price) = Occupancy(price) x Price
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"


@dataclass
class ElasticityResult:
    """Result of elasticity calculation."""
    elasticity: float
    elasticity_type: str  # elastic, unit_elastic, inelastic
    price_change_recommended: str  # increase, decrease, maintain
    risk_level: str  # low, medium, high
    confidence: float
    reasoning: str = ""


@dataclass
class RevenueCurve:
    """Revenue curve analysis for a price range."""
    prices: np.ndarray
    occupancy_probs: np.ndarray
    revenues: np.ndarray
    optimal_price: float
    optimal_revenue: float
    current_price: float
    current_revenue: float
    revenue_gain: float
    revenue_gain_pct: float


@dataclass
class PricingRecommendation:
    """Complete pricing recommendation."""
    current_price: float
    recommended_price: float
    expected_occupancy_current: float
    expected_occupancy_recommended: float
    expected_revenue_current: float
    expected_revenue_recommended: float
    revenue_change: float
    revenue_change_pct: float
    elasticity: float
    elasticity_type: str
    risk_level: str
    confidence: float
    reasoning: str


class PriceElasticityEngine:
    """
    Calculates price elasticity and generates revenue optimization.
    
    Core concept:
        Revenue = Occupancy(price) x Price
        
    To maximize revenue, we need to find the price where:
        dRevenue/dPrice = 0
        => Occupancy + Price x dOccupancy/dPrice = 0
        => Occupancy = -Price x dOccupancy/dPrice
        => Elasticity = -1 (unit elastic)
    """

    def __init__(self, occupancy_predictor=None):
        """
        Args:
            occupancy_predictor: OccupancyPredictor instance
        """
        self.occupancy_predictor = occupancy_predictor

    def calculate_point_elasticity(
        self,
        price: float,
        occupancy: float,
        price_change: float = 1.0,
    ) -> float:
        """
        Calculate point elasticity at a given price.
        
        E = (dQ/dP) x (P/Q)
        
        Args:
            price: Current price
            occupancy: Current occupancy rate
            price_change: Small price change for numerical derivative
            
        Returns:
            Elasticity value (negative for normal goods)
        """
        if self.occupancy_predictor is None:
            return -1.0  # Default: unit elastic

        # Calculate occupancy at current and slightly different price
        df_placeholder = pd.DataFrame({"placeholder": [0]})

        occ_current = self.occupancy_predictor.predict_single(
            {}, price
        )
        occ_new = self.occupancy_predictor.predict_single(
            {}, price + price_change
        )

        # dQ/dP
        dQ_dP = (occ_new - occ_current) / price_change

        # Elasticity = (dQ/dP) x (P/Q)
        if occ_current > 0:
            elasticity = dQ_dP * (price / occ_current)
        else:
            elasticity = -1.0

        return float(elasticity)

    def calculate_arc_elasticity(
        self,
        price1: float,
        price2: float,
        occupancy1: float,
        occupancy2: float,
    ) -> float:
        """
        Calculate arc elasticity between two points.
        
        E = ((Q2 - Q1) / ((Q2 + Q1)/2)) / ((P2 - P1) / ((P2 + P1)/2))
        """
        if price1 == price2 or occupancy1 + occupancy2 == 0:
            return -1.0

        dQ = occupancy2 - occupancy1
        avg_Q = (occupancy1 + occupancy2) / 2
        dP = price2 - price1
        avg_P = (price1 + price2) / 2

        if avg_Q == 0 or avg_P == 0:
            return -1.0

        elasticity = (dQ / avg_Q) / (dP / avg_P)
        return float(elasticity)

    def classify_elasticity(self, elasticity: float) -> ElasticityResult:
        """
        Classify elasticity and generate recommendation.
        
        Rules:
            E < -1.5: Very elastic (price increase risky)
            -1.5 <= E < -0.5: Normal range
            -0.5 <= E < 0: Inelastic (price increase safe)
            E >= 0: Anomaly (should not happen normally)
        """
        abs_e = abs(elasticity)

        if elasticity < -1.5:
            elasticity_type = "very_elastic"
            price_change = "decrease"
            risk = "high"
            confidence = 0.6
            reasoning = (
                "Demand is very sensitive to price. "
                "Small price increases significantly reduce occupancy. "
                "Consider competitive pricing or value-added packages."
            )
        elif elasticity < -0.5:
            elasticity_type = "elastic"
            price_change = "increase"
            risk = "medium"
            confidence = 0.75
            reasoning = (
                "Demand responds normally to price changes. "
                "Price optimization can improve revenue. "
                "Monitor occupancy after price changes."
            )
        elif elasticity < 0:
            elasticity_type = "inelastic"
            price_change = "increase"
            risk = "low"
            confidence = 0.85
            reasoning = (
                "Demand is relatively insensitive to price. "
                "Price increases are likely to improve revenue. "
                "Good opportunity for rate optimization."
            )
        else:
            elasticity_type = "anomaly"
            price_change = "maintain"
            risk = "medium"
            confidence = 0.5
            reasoning = (
                "Unusual elasticity detected. "
                "Maintain current pricing and investigate."
            )

        return ElasticityResult(
            elasticity=elasticity,
            elasticity_type=elasticity_type,
            price_change_recommended=price_change,
            risk_level=risk,
            confidence=confidence,
        )

    def generate_revenue_curve(
        self,
        base_features: Dict,
        price_range: Tuple[float, float] = (50.0, 300.0),
        n_points: int = 50,
        total_rooms: int = 100,
    ) -> RevenueCurve:
        """
        Generate revenue curve for a range of prices.
        
        Args:
            base_features: Base hotel features (without price)
            price_range: (min_price, max_price) to test
            n_points: Number of price points to evaluate
            total_rooms: Total rooms in hotel
            
        Returns:
            RevenueCurve with optimal pricing analysis
        """
        prices = np.linspace(price_range[0], price_range[1], n_points)
        occupancy_probs = np.zeros(n_points)
        revenues = np.zeros(n_points)

        for i, price in enumerate(prices):
            if self.occupancy_predictor is not None:
                occ = self.occupancy_predictor.predict_single(base_features, price)
            else:
                raise ValueError("Occupancy predictor not loaded. Cannot generate revenue curve.")

            occupancy_probs[i] = occ
            revenues[i] = occ * price * total_rooms

        # Find optimal price
        optimal_idx = np.argmax(revenues)
        optimal_price = prices[optimal_idx]
        optimal_revenue = revenues[optimal_idx]

        # Current price (middle of range or specified)
        current_price = (price_range[0] + price_range[1]) / 2
        current_idx = np.argmin(np.abs(prices - current_price))
        current_revenue = revenues[current_idx]

        revenue_gain = optimal_revenue - current_revenue
        revenue_gain_pct = (revenue_gain / current_revenue * 100) if current_revenue > 0 else 0

        return RevenueCurve(
            prices=prices,
            occupancy_probs=occupancy_probs,
            revenues=revenues,
            optimal_price=float(optimal_price),
            optimal_revenue=float(optimal_revenue),
            current_price=float(current_price),
            current_revenue=float(current_revenue),
            revenue_gain=float(revenue_gain),
            revenue_gain_pct=float(revenue_gain_pct),
        )

    def optimize_price(
        self,
        base_features: Dict,
        current_price: float,
        price_range: Tuple[float, float] = (50.0, 300.0),
        total_rooms: int = 100,
        min_occupancy: float = 0.3,
    ) -> PricingRecommendation:
        """
        Generate complete pricing recommendation.
        
        Args:
            base_features: Hotel features
            current_price: Current room price
            price_range: Price range to consider
            total_rooms: Total rooms
            min_occupancy: Minimum acceptable occupancy
            
        Returns:
            PricingRecommendation with full analysis
        """
        # Generate revenue curve
        curve = self.generate_revenue_curve(
            base_features, price_range, total_rooms=total_rooms
        )

        # Get current occupancy
        if self.occupancy_predictor is not None:
            occ_current = self.occupancy_predictor.predict_single(
                base_features, current_price
            )
            occ_optimal = self.occupancy_predictor.predict_single(
                base_features, curve.optimal_price
            )
        else:
            raise ValueError("Occupancy predictor not loaded. Cannot optimize price.")

        # Calculate elasticity at current price
        elasticity = self.calculate_point_elasticity(
            current_price, occ_current
        )
        elasticity_result = self.classify_elasticity(elasticity)

        # Ensure minimum occupancy constraint
        recommended_price = curve.optimal_price
        if occ_optimal < min_occupancy:
            # Find price that gives minimum occupancy
            valid_prices = curve.prices[curve.occupancy_probs >= min_occupancy]
            if len(valid_prices) > 0:
                recommended_price = valid_prices[np.argmax(
                    curve.revenues[curve.occupancy_probs >= min_occupancy]
                )]

        # Revenue calculations
        rev_current = occ_current * current_price * total_rooms
        rev_recommended = occ_optimal * recommended_price * total_rooms
        rev_change = rev_recommended - rev_current
        rev_change_pct = (rev_change / rev_current * 100) if rev_current > 0 else 0

        return PricingRecommendation(
            current_price=current_price,
            recommended_price=float(recommended_price),
            expected_occupancy_current=float(occ_current),
            expected_occupancy_recommended=float(occ_optimal),
            expected_revenue_current=float(rev_current),
            expected_revenue_recommended=float(rev_recommended),
            revenue_change=float(rev_change),
            revenue_change_pct=float(rev_change_pct),
            elasticity=float(elasticity),
            elasticity_type=elasticity_result.elasticity_type,
            risk_level=elasticity_result.risk_level,
            confidence=elasticity_result.confidence,
            reasoning=elasticity_result.reasoning,
        )

    def simulate_price_change(
        self,
        base_features: Dict,
        current_price: float,
        price_change_pct: float,
        total_rooms: int = 100,
    ) -> Dict:
        """
        Simulate effect of a specific price change.
        
        Args:
            base_features: Hotel features
            current_price: Current price
            price_change_pct: Percentage change (-20 = decrease 20%)
            total_rooms: Total rooms
            
        Returns:
            Dictionary with simulation results
        """
        new_price = current_price * (1 + price_change_pct / 100)

        if self.occupancy_predictor is not None:
            occ_current = self.occupancy_predictor.predict_single(
                base_features, current_price
            )
            occ_new = self.occupancy_predictor.predict_single(
                base_features, new_price
            )
        else:
            raise ValueError("Occupancy predictor not loaded. Cannot simulate price change.")

        rev_current = occ_current * current_price * total_rooms
        rev_new = occ_new * new_price * total_rooms

        elasticity = self.calculate_arc_elasticity(
            current_price, new_price, occ_current, occ_new
        )

        return {
            "current_price": current_price,
            "new_price": new_price,
            "price_change_pct": price_change_pct,
            "current_occupancy": occ_current,
            "new_occupancy": occ_new,
            "occupancy_change": occ_new - occ_current,
            "current_revenue": rev_current,
            "new_revenue": rev_new,
            "revenue_change": rev_new - rev_current,
            "revenue_change_pct": ((rev_new - rev_current) / rev_current * 100) if rev_current > 0 else 0,
            "elasticity": elasticity,
            "recommendation": "profitable" if rev_new > rev_current else "unprofitable",
        }


def run_elasticity_analysis():
    """Run a complete elasticity analysis demo."""
    print("=" * 60)
    print("PRICE ELASTICITY ANALYSIS")
    print("=" * 60)

    # Try to load occupancy predictor
    from src.optimus_price.occupancy_model import OccupancyPredictor

    predictor = OccupancyPredictor()
    if not predictor.load():
        print("Occupancy model not found. Training new one...")
        predictor.train(pd.read_csv(DATA_DIR / "processed" / "hotel_reservations_clean.csv"))
        predictor.save()

    # Create engine
    engine = PriceElasticityEngine(predictor)

    # Demo features
    base_features = {
        "total_guests": 2,
        "total_nights": 3,
        "lead_time_days": 30,
        "is_weekend": 0,
        "season_factor": 1.0,
        "month": 6,
        "is_last_minute": 0,
        "is_early_bird": 0,
        "special_requests": 1,
        "is_repeated_guest": 0,
        "is_online_booking": 1,
        "has_meal_plan": 1,
        "room_type_value": 2,
        "requires_parking": 0,
    }

    # Generate revenue curve
    print("\n--- Revenue Curve Analysis ---")
    curve = engine.generate_revenue_curve(
        base_features,
        price_range=(50, 250),
        n_points=21,
        total_rooms=100,
    )

    print(f"Optimal Price: ${curve.optimal_price:.2f}")
    print(f"Optimal Revenue: ${curve.optimal_revenue:.2f}/night")
    print(f"Current Price: ${curve.current_price:.2f}")
    print(f"Current Revenue: ${curve.current_revenue:.2f}/night")
    print(f"Revenue Gain: ${curve.revenue_gain:.2f} ({curve.revenue_gain_pct:.1f}%)")

    # Price recommendation
    print("\n--- Pricing Recommendation ---")
    recommendation = engine.optimize_price(
        base_features,
        current_price=120.0,
        price_range=(50, 250),
        total_rooms=100,
    )

    print(f"Current Price:     ${recommendation.current_price:.2f}")
    print(f"Recommended Price: ${recommendation.recommended_price:.2f}")
    print(f"Revenue Change:    ${recommendation.revenue_change:.2f} ({recommendation.revenue_change_pct:.1f}%)")
    print(f"Elasticity:        {recommendation.elasticity:.3f}")
    print(f"Risk Level:        {recommendation.risk_level}")
    print(f"Confidence:        {recommendation.confidence:.0%}")
    print(f"Reasoning:         {recommendation.reasoning}")

    # Simulate price changes
    print("\n--- Price Change Simulations ---")
    for change_pct in [-10, -5, 0, 5, 10, 15, 20]:
        result = engine.simulate_price_change(
            base_features, 120.0, change_pct, total_rooms=100
        )
        print(
            f"  {change_pct:+3d}%: Price=${result['new_price']:.0f}, "
            f"Occ={result['new_occupancy']:.1%}, "
            f"Rev=${result['new_revenue']:.0f} "
            f"({result['revenue_change_pct']:+.1f}%) "
            f"[{result['recommendation']}]"
        )

    return engine


if __name__ == "__main__":
    run_elasticity_analysis()
