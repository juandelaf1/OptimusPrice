#!/usr/bin/env python3
"""
Scraping Manager for Optimus Price Phase 1
Orchestrates RASPAL-based hotel pricing collection from multiple OTAs
"""

import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional
from raspal import Fetcher, Pipeline, AutoThrottle
from raspal.models import LLMConfig

CONFIG_DIR = r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final\configs"
DATA_DIR = r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final\data\scraped"


class ScrapingManager:
    """Manages OTA scraping pipelines for hotel pricing"""

    OTA_CONFIGS = {
        "booking.com": "booking_scraping.yaml",
        "expedia.com": "expedia_scraping.yaml",
        "hotels.com": "hotelscom_scraping.yaml",
        "trivago.es": "trivago_scraping.yaml",
    }

    def __init__(self):
        self.fetcher = Fetcher(throttle=AutoThrottle(min_delay=1, max_delay=30))
        self.pipeline = Pipeline()
        os.makedirs(DATA_DIR, exist_ok=True)

    def load_config(self, ota: str) -> Optional[Dict]:
        """Load YAML config for a specific OTA"""
        filename = self.OTA_CONFIGS.get(ota)
        if not filename:
            print(f"No config for {ota}")
            return None
        path = os.path.join(CONFIG_DIR, filename)
        if not os.path.exists(path):
            print(f"Config not found: {path}")
            return None
        with open(path) as f:
            return yaml.safe_load(f)

    def scrape_hotel(self, hotel_id: str, otas: Optional[List[str]] = None) -> Dict:
        """Scrape a single hotel across specified OTAs"""
        if otas is None:
            otas = list(self.OTA_CONFIGS.keys())

        results = {}
        for ota in otas:
            config = self.load_config(ota)
            if not config:
                continue

            url = config["url"].format(hotel_id=hotel_id)
            engine = config.get("engine", "auto")
            cache_ttl = config.get("cache_ttl", 1800)

            print(f"Fetching {ota} / {hotel_id} ...")
            try:
                result = self.fetcher.fetch(url, engine=engine, cache_ttl=cache_ttl)

                llm_config = config.get("llm")
                parsed = {}
                if llm_config and result.text:
                    from raspal import LLMExtractor
                    llm = LLMExtractor()
                    lc = LLMConfig(
                        model=llm_config.get("model", "llama3.2"),
                        template=llm_config.get("template", "hotel_pricing"),
                        output_schema=llm_config.get("output_schema", {"price": 0})
                    )
                    parsed = llm.extract(result.text, lc)

                entry = {
                    "ota": ota,
                    "hotel_id": hotel_id,
                    "url": url,
                    "status": result.status,
                    "cached": result.cached,
                    "engine": engine,
                    "timestamp": datetime.now().isoformat(),
                    "parsed": parsed,
                    "raw_length": len(result.text) if result.text else 0
                }
                results[ota] = entry
                self.pipeline.add(url, entry)

            except Exception as e:
                print(f"  Error fetching {ota}: {e}")
                results[ota] = {"ota": ota, "hotel_id": hotel_id, "error": str(e)}

        return results

    def scrape_multiple_hotels(self, hotel_ids: List[str], otas: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Scrape multiple hotels across OTAs"""
        all_results = {}
        for hid in hotel_ids:
            print(f"\n--- Scraping hotel: {hid} ---")
            all_results[hid] = self.scrape_hotel(hid, otas)
        return all_results

    def save_results(self, results: Dict, name: str = "scrape_results"):
        """Save scraping results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(DATA_DIR, f"{name}_{timestamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved to {path}")
        return path

    def prices_to_dataframe(self, results: Dict) -> "pd.DataFrame":
        """Convert scraping results to a DataFrame for model training"""
        import pandas as pd
        rows = []
        for hotel_id, otas in results.items():
            for ota_name, data in otas.items():
                if "parsed" in data and data["parsed"]:
                    row = {
                        "hotel_id": hotel_id,
                        "ota": ota_name,
                        "scrape_timestamp": data.get("timestamp"),
                        "status": data.get("status"),
                    }
                    row.update(data["parsed"])
                    rows.append(row)
        return pd.DataFrame(rows)

    def summary(self, results: Dict) -> Dict:
        """Generate summary statistics from scrape results"""
        total = 0
        success = 0
        for hotel_id, otas in results.items():
            for ota_name, data in otas.items():
                total += 1
                if "error" not in data:
                    success += 1
        return {
            "hotels_scraped": len(results),
            "total_requests": total,
            "successful": success,
            "failed": total - success,
            "success_rate": f"{success / total * 100:.1f}%" if total else "0%"
        }


def demo_scrape():
    """Demo: scrape sample hotel IDs across all OTAs"""
    manager = ScrapingManager()
    sample_hotels = ["sample-hotel-001", "sample-hotel-002"]
    results = manager.scrape_multiple_hotels(sample_hotels)
    summary = manager.summary(results)
    print(f"\nSummary: {summary}")
    manager.save_results(results)
    return results


if __name__ == "__main__":
    demo_scrape()
