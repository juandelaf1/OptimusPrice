#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revenue Optimization Engine for Optimus Price
Combines occupancy prediction + elasticity analysis for optimal pricing.
Maximize: Revenue = Occupancy(price) x Price x Rooms
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"


@dataclass
class RevenueOptimizationResult:
    """Complete revenue optimization result."""
    hotel_id: str
    current_price: float
    optimal_price: float
    price_change: float
    price_change_pct: float
    current_occupancy: float
    optimal_occupancy: float
    current_revenue_per_room: float
    optimal_revenue_per_room: float
    revenue_gain_per_room: float
    revenue_gain_pct: float
    total_rooms: int
    current_total_revenue: float
    optimal_total_revenue: float
    total_revenue_gain: float
    elasticity: float
    elasticity_type: str
    risk_level: str
    confidence: float
    recommendation: str
    reasoning: str


class RevenueOptimizer:
    """
    Revenue optimization engine that combines:
    - Occupancy prediction (what occupancy do we get at price X?)
    - Price elasticity (how does demand change with price?)
    - Revenue maximization (what price maximizes Revenue = Occ x Price x Rooms?)
    """

    def __init__(self, occupancy_predictor=None, elasticity_engine=None):
        self.occupancy_predictor = occupancy_predictor
        self.elasticity_engine = elasticity_engine

    def optimize(
        self,
        hotel_id: str,
        current_price: float,
        hotel_features: Optional[Dict] = None,
        total_rooms: int = 100,
        price_range: Tuple[float, float] = (50.0, 300.0),
        min_occupancy: float = 0.3,
        min_price: float = 30.0,
        max_price: float = 500.0,
    ) -> RevenueOptimizationResult:
        """
        Generate complete revenue optimization recommendation.
        
        Args:
            hotel_id: Unique hotel identifier
            current_price: Current room price
            hotel_features: Hotel-specific features
            total_rooms: Total number of rooms
            price_range: Range of prices to consider
            min_occupancy: Minimum acceptable occupancy rate
            min_price: Absolute minimum price (rate fence)
            max_price: Absolute maximum price (rate fence)
            
        Returns:
            RevenueOptimizationResult with full analysis
        """
        if hotel_features is None:
            hotel_features = {}

        # Use elasticity engine
        if self.elasticity_engine is None:
            raise ValueError("Elasticity engine not loaded. Cannot optimize without real models.")
        
        recommendation = self.elasticity_engine.optimize_price(
            hotel_features, current_price, price_range, total_rooms, min_occupancy
        )

        # Apply rate fences
        optimal_price = max(min_price, min(max_price, recommendation.recommended_price))

        # Recalculate with constrained price
        if self.occupancy_predictor is not None:
            occ_current = self.occupancy_predictor.predict_single(
                hotel_features, current_price
            )
            occ_optimal = self.occupancy_predictor.predict_single(
                hotel_features, optimal_price
            )
        else:
            occ_current = recommendation.expected_occupancy_current
            occ_optimal = recommendation.expected_occupancy_recommended

        # Revenue calculations
        rev_current = occ_current * current_price
        rev_optimal = occ_optimal * optimal_price
        rev_gain = rev_optimal - rev_current
        rev_gain_pct = (rev_gain / rev_current * 100) if rev_current > 0 else 0

        # Determine recommendation text
        if rev_gain > 0:
            if optimal_price > current_price:
                rec_text = "INCREASE_PRICE"
                reasoning = (
                    f"Increase price from ${current_price:.0f} to ${optimal_price:.0f}. "
                    f"Expected revenue gain: ${rev_gain:.2f}/room/night ({rev_gain_pct:.1f}%). "
                    f"Elasticity: {recommendation.elasticity:.2f} ({recommendation.elasticity_type})."
                )
            else:
                rec_text = "DECREASE_PRICE"
                reasoning = (
                    f"Decrease price from ${current_price:.0f} to ${optimal_price:.0f}. "
                    f"Expected revenue gain: ${rev_gain:.2f}/room/night ({rev_gain_pct:.1f}%). "
                    f"Higher occupancy compensates for lower rate."
                )
        else:
            rec_text = "MAINTAIN_PRICE"
            reasoning = (
                f"Current price ${current_price:.0f} is near optimal. "
                f"No significant revenue improvement possible."
            )
            optimal_price = current_price
            rev_gain = 0
            rev_gain_pct = 0

        return RevenueOptimizationResult(
                hotel_id=hotel_id,
                current_price=current_price,
                optimal_price=float(optimal_price),
                price_change=float(optimal_price - current_price),
                price_change_pct=float((optimal_price - current_price) / current_price * 100),
                current_occupancy=float(occ_current),
                optimal_occupancy=float(occ_optimal),
                current_revenue_per_room=float(rev_current),
                optimal_revenue_per_room=float(rev_optimal),
                revenue_gain_per_room=float(rev_gain),
                revenue_gain_pct=float(rev_gain_pct),
                total_rooms=total_rooms,
                current_total_revenue=float(rev_current * total_rooms),
                optimal_total_revenue=float(rev_optimal * total_rooms),
                total_revenue_gain=float(rev_gain * total_rooms),
                elasticity=float(recommendation.elasticity),
                elasticity_type=recommendation.elasticity_type,
                risk_level=recommendation.risk_level,
                confidence=recommendation.confidence,
                recommendation=rec_text,
                reasoning=reasoning,
            )

    def optimize_portfolio(
        self,
        hotels: List[Dict],
        price_range: Tuple[float, float] = (50.0, 300.0),
    ) -> List[RevenueOptimizationResult]:
        """
        Optimize pricing for multiple hotels.
        
        Args:
            hotels: List of dicts with hotel_id, current_price, features, total_rooms
            price_range: Price range to consider
            
        Returns:
            List of RevenueOptimizationResult for each hotel
        """
        results = []
        for hotel in hotels:
            result = self.optimize(
                hotel_id=hotel.get("hotel_id", "unknown"),
                current_price=hotel.get("current_price", 100.0),
                hotel_features=hotel.get("features", {}),
                total_rooms=hotel.get("total_rooms", 100),
                price_range=price_range,
            )
            results.append(result)
        return results

    def generate_executive_summary(
        self,
        results: List[RevenueOptimizationResult],
    ) -> Dict:
        """
        Generate executive summary for hotel managers.
        
        Returns:
            Dictionary with key metrics and recommendations
        """
        if not results:
            return {"error": "No results to summarize"}

        total_current_revenue = sum(r.current_total_revenue for r in results)
        total_optimal_revenue = sum(r.optimal_total_revenue for r in results)
        total_gain = total_optimal_revenue - total_current_revenue

        increase_count = sum(1 for r in results if r.recommendation == "INCREASE_PRICE")
        decrease_count = sum(1 for r in results if r.recommendation == "DECREASE_PRICE")
        maintain_count = sum(1 for r in results if r.recommendation == "MAINTAIN_PRICE")

        high_risk = sum(1 for r in results if r.risk_level == "high")
        medium_risk = sum(1 for r in results if r.risk_level == "medium")
        low_risk = sum(1 for r in results if r.risk_level == "low")

        return {
            "total_hotels": len(results),
            "total_current_revenue_night": total_current_revenue,
            "total_optimal_revenue_night": total_optimal_revenue,
            "total_revenue_gain_night": total_gain,
            "total_revenue_gain_annual": total_gain * 365,
            "avg_revenue_gain_pct": float(np.mean([r.revenue_gain_pct for r in results])),
            "recommendations": {
                "increase_price": increase_count,
                "decrease_price": decrease_count,
                "maintain_price": maintain_count,
            },
            "risk_distribution": {
                "high": high_risk,
                "medium": medium_risk,
                "low": low_risk,
            },
            "top_opportunities": [
                {
                    "hotel_id": r.hotel_id,
                    "current_price": r.current_price,
                    "optimal_price": r.optimal_price,
                    "revenue_gain": r.total_revenue_gain,
                    "revenue_gain_pct": r.revenue_gain_pct,
                    "risk_level": r.risk_level,
                }
                for r in sorted(results, key=lambda x: x.total_revenue_gain, reverse=True)[:5]
            ],
            "model_confidence": float(np.mean([r.confidence for r in results])),
        }


def run_revenue_optimization():
    """Run complete revenue optimization demo."""
    print("=" * 60)
    print("REVENUE OPTIMIZATION ENGINE")
    print("=" * 60)

    # Try to load models
    from src.optimus_price.occupancy_model import OccupancyPredictor
    from src.optimus_price.elasticity_engine import PriceElasticityEngine

    predictor = OccupancyPredictor()
    if not predictor.load():
        print("Training occupancy model...")
        df = pd.read_csv(DATA_DIR / "processed" / "hotel_reservations_clean.csv")
        predictor.train(df)
        predictor.save()

    engine = PriceElasticityEngine(predictor)
    optimizer = RevenueOptimizer(predictor, engine)

    # Demo: Optimize a single hotel
    print("\n--- Single Hotel Optimization ---")
    result = optimizer.optimize(
        hotel_id="hotel_001",
        current_price=120.0,
        total_rooms=100,
        price_range=(50, 250),
    )

    print(f"Hotel: {result.hotel_id}")
    print(f"Current Price: ${result.current_price:.2f}")
    print(f"Optimal Price: ${result.optimal_price:.2f}")
    print(f"Price Change: ${result.price_change:.2f} ({result.price_change_pct:.1f}%)")
    print(f"Current Occupancy: {result.current_occupancy:.1%}")
    print(f"Optimal Occupancy: {result.optimal_occupancy:.1%}")
    print(f"Revenue Gain/Room: ${result.revenue_gain_per_room:.2f} ({result.revenue_gain_pct:.1f}%)")
    print(f"Total Revenue Gain: ${result.total_revenue_gain:.2f}/night")
    print(f"Elasticity: {result.elasticity:.3f} ({result.elasticity_type})")
    print(f"Risk: {result.risk_level}, Confidence: {result.confidence:.0%}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Reasoning: {result.reasoning}")

    # Demo: Optimize portfolio
    print("\n--- Portfolio Optimization ---")
    hotels = [
        {"hotel_id": "hotel_001", "current_price": 120, "total_rooms": 100},
        {"hotel_id": "hotel_002", "current_price": 95, "total_rooms": 80},
        {"hotel_id": "hotel_003", "current_price": 150, "total_rooms": 60},
        {"hotel_id": "hotel_004", "current_price": 80, "total_rooms": 120},
        {"hotel_id": "hotel_005", "current_price": 200, "total_rooms": 50},
    ]

    results = optimizer.optimize_portfolio(hotels)
    summary = optimizer.generate_executive_summary(results)

    print(f"\nPortfolio Summary:")
    print(f"  Total Hotels: {summary['total_hotels']}")
    print(f"  Current Revenue: ${summary['total_current_revenue_night']:.0f}/night")
    print(f"  Optimal Revenue: ${summary['total_optimal_revenue_night']:.0f}/night")
    print(f"  Revenue Gain: ${summary['total_revenue_gain_night']:.0f}/night")
    print(f"  Annual Gain: ${summary['total_revenue_gain_annual']:.0f}")
    print(f"  Avg Gain: {summary['avg_revenue_gain_pct']:.1f}%")
    print(f"\n  Recommendations:")
    print(f"    Increase: {summary['recommendations']['increase_price']}")
    print(f"    Decrease: {summary['recommendations']['decrease_price']}")
    print(f"    Maintain: {summary['recommendations']['maintain_price']}")

    print(f"\n  Top Opportunities:")
    for opp in summary["top_opportunities"]:
        print(
            f"    {opp['hotel_id']}: ${opp['current_price']:.0f} -> "
            f"${opp['optimal_price']:.0f} "
            f"(+${opp['revenue_gain']:.0f}/night, {opp['revenue_gain_pct']:.1f}%)"
        )

    return optimizer, results


if __name__ == "__main__":
    run_revenue_optimization()
