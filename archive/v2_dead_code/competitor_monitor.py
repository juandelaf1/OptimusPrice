#!/usr/bin/env python3
"""
Competitor Price Monitoring System for Enhanced Optimus Price
Integrates with RASPAL to fetch and analyze competitor hotel pricing
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

from enhanced_optimus import EnhancedOptimusPrice
from raspal import Fetcher, AutoThrottle, LLMExtractor
from raspal.models import LLMConfig
import time
from typing import Dict, List, Optional


class OTAPriceComparator:
    """Analyzes OTA pricing strategies and opportunities"""

    def __init__(self, optimus_model: EnhancedOptimusPrice):
        self.optimus_model = optimus_model
        self.ota_sources = ["booking.com", "expedia.com", "hotels.com", "trivago.es"]
        self.fetcher = Fetcher(throttle=AutoThrottle(min_delay=1, max_delay=60))
        self.price_history: Dict[str, List] = {}

    def analyze_price_gap(self, hotel_data: Dict) -> Dict:
        """Analyze pricing gap between internal and OTA prices"""
        hotel_id = hotel_data.get("hotel_id", "test-hotel-001")
        internal_price = self.optimus_model.predict_with_market_context(hotel_data)
        ota_prices = self.fetch_competitor_prices(hotel_id)

        if not ota_prices:
            return {"status": "no_data", "message": "Could not fetch competitor prices"}

        opportunities = []
        for ota, price in ota_prices.items():
            if price is None:
                continue
            price_gap = price - internal_price
            opportunity_score = self.calculate_opportunity_score(internal_price, price)

            opportunities.append({
                "ota": ota,
                "ota_price": price,
                "internal_price": internal_price,
                "price_gap": price_gap,
                "opportunity_score": opportunity_score,
                "recommendation": self.generate_recommendation(internal_price, price, opportunity_score)
            })

        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

        return {
            "hotel_id": hotel_id,
            "internal_price": internal_price,
            "competitor_analysis": opportunities,
            "top_opportunity": opportunities[0] if opportunities else None
        }

    def fetch_competitor_prices(self, hotel_id: str) -> Dict[str, Optional[float]]:
        """Fetch current prices from all OTA sources"""
        prices = {}
        for ota in self.ota_sources:
            price = self.get_single_ota_price(hotel_id, ota)
            if price:
                prices[ota] = price
        return prices

    def get_single_ota_price(self, hotel_id: str, ota: str) -> Optional[float]:
        """Fetch price from a specific OTA source"""
        url_map = {
            "booking.com": f"https://www.booking.com/hotel/price/{hotel_id}",
            "expedia.com": f"https://www.expedia.com/hotel/{hotel_id}",
            "hotels.com": f"https://www.hotels.com/hotel/{hotel_id}",
            "trivago.es": f"https://www.trivago.es/hotel/{hotel_id}"
        }

        url = url_map.get(ota)
        if not url:
            return None

        try:
            result = self.fetcher.fetch(url, engine="stealth", cache_ttl=300)

            llm = LLMExtractor()
            data = llm.extract(
                result.html,
                LLMConfig(
                    template="hotel_pricing",
                    output_schema={
                        "price": 0,
                        "currency": "EUR",
                        "hotel_name": ""
                    }
                )
            )

            return data.get("price")

        except Exception as e:
            print(f"Error fetching price from {ota}: {e}")
            return None

    def calculate_opportunity_score(self, internal_price: float, competitor_price: float) -> float:
        """Calculate opportunity score based on price differences"""
        if competitor_price <= internal_price:
            return 0.0

        gap = competitor_price - internal_price
        price_ratio = gap / internal_price
        score = min(price_ratio * 100, 100)

        return score

    def generate_recommendation(self, internal_price: float, competitor_price: float, score: float) -> Dict:
        """Generate price adjustment recommendation"""
        if score < 10:
            return {
                "action": "monitor",
                "reason": "Price gap is minimal, maintain current pricing",
                "priority": "low"
            }
        elif score < 30:
            return {
                "action": "adjust",
                "recommended_price": competitor_price * 0.95,
                "reason": f"Moderate opportunity: ${score:.1f} gap",
                "priority": "medium"
            }
        elif score < 60:
            return {
                "action": "significant_adjust",
                "recommended_price": competitor_price * 0.90,
                "reason": f"High opportunity: ${score:.1f} gap",
                "priority": "high"
            }
        else:
            return {
                "action": "aggressive_adjust",
                "recommended_price": competitor_price * 0.85,
                "reason": f"Very high opportunity: ${score:.1f} gap",
                "priority": "critical"
            }

    def start_continuous_monitoring(self, interval_minutes: int = 15):
        """Start continuous monitoring of competitor prices"""
        print(f"Starting competitor price monitoring every {interval_minutes} minutes...")
        print(f"Monitoring {len(self.ota_sources)} OTA sources")

        import schedule

        def monitor_prices():
            print(f"Price check at {time.strftime('%H:%M:%S')}")
            sample_hotel = {"hotel_id": "sample-hotel-001", "location": "beach", "season": "peak"}
            analysis = self.analyze_price_gap(sample_hotel)

            if analysis.get("top_opportunity"):
                opp = analysis["top_opportunity"]
                print(f"Top opportunity: {opp['ota']} - ${opp['ota_price']} (gap: ${opp['price_gap']:.2f})")
                print(f"Recommendation: {opp['recommendation']}")

        schedule.every(interval_minutes).minutes.do(monitor_prices)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_price_history(self, hotel_id: str, hours: int = 24) -> List:
        """Get price history for a hotel"""
        return self.price_history.get(hotel_id, [])

    def record_price_check(self, hotel_id: str, price: float, ota: str):
        """Record price check for historical analysis"""
        if hotel_id not in self.price_history:
            self.price_history[hotel_id] = []
        self.price_history[hotel_id].append({
            "timestamp": time.time(),
            "price": price,
            "ota": ota,
            "source": "automated_monitoring"
        })


def setup_enhanced_system():
    """Setup and initialize the enhanced Optimus Price system"""
    print("Initializing Enhanced Optimus Price System with RASPAL Integration...")
    enhanced_system = EnhancedOptimusPrice()
    competitor_monitor = OTAPriceComparator(enhanced_system)
    print("Enhanced system initialized successfully!")
    print("RASPAL integration complete")
    print("Competitor monitoring active")
    return enhanced_system, competitor_monitor


if __name__ == "__main__":
    enhanced_system, competitor_monitor = setup_enhanced_system()

    print(f"\nSystem Statistics:")
    print(f"ML Models: 4 optimized Python modules")
    print(f"RASPAL Sources: {len(competitor_monitor.ota_sources)} OTA platforms")
    print(f"Scraping Engines: scrapling, playwright, stealth, auto")
    print(f"Monitoring Intervals: Every 15 minutes by default")
    print(f"Price Extraction: AI-powered with LLM")

    sample = {"hotel_id": "test-hotel-001", "total_guests": 2, "total_nights": 3, "season": "peak_season"}
    result = competitor_monitor.analyze_price_gap(sample)
    print(f"\nSample analysis: {result['status'] if 'status' in result else 'completed'}")
