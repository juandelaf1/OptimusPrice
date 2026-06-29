#!/usr/bin/env python3
"""
Phase 3: Competitor Price Monitoring Service
Continuous monitoring of OTA prices with alerts and reporting
Integrates RASPAL scraping with ML-powered price analysis
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from enhanced_optimus import EnhancedOptimusPrice
from scraping_manager import ScrapingManager

BASE_DIR = r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final"
MONITOR_DIR = os.path.join(BASE_DIR, "data", "monitoring")
ALERTS_DIR = os.path.join(MONITOR_DIR, "alerts")
REPORTS_DIR = os.path.join(MONITOR_DIR, "reports")

os.makedirs(MONITOR_DIR, exist_ok=True)
os.makedirs(ALERTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "data", "monitoring", "service.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("monitor")


@dataclass
class PriceAlert:
    hotel_id: str
    ota: str
    internal_price: float
    ota_price: float
    gap: float
    gap_percent: float
    opportunity_score: float
    recommendation: str
    priority: str
    timestamp: str

    def to_dict(self):
        return asdict(self)


class MonitoringService:
    """Continuous competitor price monitoring service"""

    def __init__(self, interval_minutes: int = 15):
        self.interval = interval_minutes
        self.system = EnhancedOptimusPrice()
        self.system.load_model()
        self.scraper = ScrapingManager()
        self.monitored_hotels: List[str] = []
        self.alert_thresholds = {
            "critical": 60,
            "high": 30,
            "medium": 10,
            "low": 0
        }
    def add_hotel(self, hotel_id: str):
        """Add a hotel to monitoring"""
        if hotel_id not in self.monitored_hotels:
            self.monitored_hotels.append(hotel_id)
            log.info(f"Added hotel {hotel_id} to monitoring")

    def remove_hotel(self, hotel_id: str):
        """Remove a hotel from monitoring"""
        if hotel_id in self.monitored_hotels:
            self.monitored_hotels.remove(hotel_id)
            log.info(f"Removed hotel {hotel_id} from monitoring")

    def check_prices(self, hotel_id: str) -> Dict:
        """Check prices for a single hotel across all OTAs"""
        log.info(f"Checking prices for {hotel_id}")

        base_features = {"hotel_id": hotel_id, "total_guests": 2, "total_nights": 1}
        internal_price = self.system.predict_with_market_context(base_features)

        scrape_results = self.scraper.scrape_hotel(hotel_id)
        alerts = []
        competitor_prices = {}

        for ota, data in scrape_results.items():
            if "error" in data:
                continue
            parsed = data.get("parsed", {})
            if not isinstance(parsed, dict):
                continue
            ota_price = parsed.get("price")
            if not ota_price:
                continue

            ota_price = float(ota_price)
            competitor_prices[ota] = ota_price
            gap = ota_price - internal_price
            gap_pct = ((ota_price - internal_price) / internal_price) * 100 if internal_price else 0
            score = min(max(gap_pct, 0), 100)

            priority = "low"
            if score >= self.alert_thresholds["critical"]:
                priority = "critical"
            elif score >= self.alert_thresholds["high"]:
                priority = "high"
            elif score >= self.alert_thresholds["medium"]:
                priority = "medium"

            alert = PriceAlert(
                hotel_id=hotel_id,
                ota=ota,
                internal_price=internal_price,
                ota_price=ota_price,
                gap=gap,
                gap_percent=round(gap_pct, 2),
                opportunity_score=score,
                recommendation=self._get_recommendation(score),
                priority=priority,
                timestamp=datetime.now().isoformat()
            )
            alerts.append(alert)

            if priority in ("critical", "high"):
                self._save_alert(alert)
                log.warning(f"ALERT [{priority}] {hotel_id} @ {ota}: ${ota_price} vs ${internal_price} (gap: {gap_pct:.1f}%)")

        result = {
            "hotel_id": hotel_id,
            "timestamp": datetime.now().isoformat(),
            "internal_price": internal_price,
            "competitor_prices": competitor_prices,
            "alerts": [a.to_dict() for a in alerts],
            "alert_count": len(alerts),
            "critical_alerts": sum(1 for a in alerts if a.priority == "critical"),
            "high_alerts": sum(1 for a in alerts if a.priority == "high")
        }

        self._save_check_result(result)
        return result

    def _get_recommendation(self, score: float) -> str:
        if score >= 60:
            return "aggressive_adjust"
        elif score >= 30:
            return "significant_adjust"
        elif score >= 10:
            return "adjust"
        return "monitor"

    def _save_alert(self, alert: PriceAlert):
        """Save alert to file"""
        date_str = datetime.now().strftime("%Y%m%d")
        path = os.path.join(ALERTS_DIR, f"alerts_{date_str}.jsonl")
        with open(path, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")

    def _save_check_result(self, result: Dict):
        """Save check result"""
        date_str = datetime.now().strftime("%Y%m%d")
        path = os.path.join(REPORTS_DIR, f"check_{date_str}.jsonl")
        with open(path, "a") as f:
            f.write(json.dumps(result) + "\n")

    def check_all_hotels(self) -> Dict[str, Dict]:
        """Check prices for all monitored hotels"""
        results = {}
        for hotel_id in self.monitored_hotels:
            try:
                results[hotel_id] = self.check_prices(hotel_id)
            except Exception as e:
                log.error(f"Error checking {hotel_id}: {e}")
                results[hotel_id] = {"error": str(e)}
        return results

    def generate_report(self) -> Dict:
        """Generate summary report of recent monitoring"""
        today = datetime.now().strftime("%Y%m%d")
        report = {
            "date": today,
            "monitored_hotels": len(self.monitored_hotels),
            "total_checks": 0,
            "total_alerts": 0,
            "critical_alerts": 0,
            "high_alerts": 0,
            "medium_alerts": 0,
            "top_opportunities": []
        }

        alerts_path = os.path.join(ALERTS_DIR, f"alerts_{today}.jsonl")
        if os.path.exists(alerts_path):
            with open(alerts_path) as f:
                for line in f:
                    if line.strip():
                        alert = json.loads(line)
                        report["total_alerts"] += 1
                        if alert["priority"] == "critical":
                            report["critical_alerts"] += 1
                        elif alert["priority"] == "high":
                            report["high_alerts"] += 1
                        elif alert["priority"] == "medium":
                            report["medium_alerts"] += 1

        report_path = os.path.join(REPORTS_DIR, f"summary_{today}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def run_once(self):
        """Run a single monitoring cycle"""
        log.info(f"=== Monitoring cycle: {len(self.monitored_hotels)} hotels ===")
        results = self.check_all_hotels()
        report = self.generate_report()
        total_critical = sum(r.get("critical_alerts", 0) for r in results.values())
        total_high = sum(r.get("high_alerts", 0) for r in results.values())
        log.info(f"Cycle complete: {total_critical} critical, {total_high} high alerts")
        return results

    def start(self):
        """Start continuous monitoring loop"""
        log.info(f"Starting monitoring service (interval: {self.interval} min)")
        log.info(f"Hotels monitored: {len(self.monitored_hotels)}")

        if not self.monitored_hotels:
            log.warning("No hotels in monitoring list. Use add_hotel() first.")
            self.add_hotel("sample-hotel-001")

        self.run_once()

        import schedule
        schedule.every(self.interval).minutes.do(self.run_once)

        log.info("Service running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Monitoring service stopped by user")


def start_service(interval: int = 15, hotels: Optional[List[str]] = None):
    """Start the monitoring service"""
    service = MonitoringService(interval_minutes=interval)

    if hotels:
        for h in hotels:
            service.add_hotel(h)
    else:
        service.add_hotel("sample-hotel-001")
        service.add_hotel("sample-hotel-002")

    service.start()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Optimus Price Monitoring Service")
    parser.add_argument("--interval", type=int, default=15, help="Check interval in minutes")
    parser.add_argument("--hotels", nargs="+", default=None, help="Hotel IDs to monitor")
    parser.add_argument("--once", action="store_true", help="Run once then exit")
    args = parser.parse_args()

    service = MonitoringService(interval_minutes=args.interval)

    if args.hotels:
        for h in args.hotels:
            service.add_hotel(h)
    else:
        service.add_hotel("sample-hotel-001")
        service.add_hotel("sample-hotel-002")

    if args.once:
        service.run_once()
        report = service.generate_report()
        print(json.dumps(report, indent=2))
    else:
        service.start()
