"""
RASPAL Worker Service — scrapes OTAs and writes results to local DB.
Can be triggered via API or run as background loop.
"""
import os, sys, json, yaml, uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE))

CONFIG_DIR = BASE / "configs"

OTAS = {
    "Booking.com": "booking_scraping.yaml",
    "Expedia": "expedia_scraping.yaml",
    "Hotels.com": "hotelscom_scraping.yaml",
    "Trivago": "trivago_scraping.yaml",
}

FETCH_TIMEOUT = 10  # seconds max per OTA


class RaspalWorker:
    def __init__(self, hotel_id: str = None):
        self.hotel_id = hotel_id or self._get_default_hotel()
        self.fetcher = None

    def _get_default_hotel(self):
        from app.database import get_db
        conn = get_db()
        row = conn.execute("SELECT id FROM hotels LIMIT 1").fetchone()
        conn.close()
        return row["id"] if row else "demo-hotel"

    def _lazy_init(self):
        if self.fetcher is None:
            from raspal import Fetcher, AutoThrottle
            self.fetcher = Fetcher(throttle=AutoThrottle(min_delay=3, max_delay=15))

    def scrape_one(self, ota_name: str) -> Optional[dict]:
        config_path = CONFIG_DIR / OTAS[ota_name]
        if not config_path.exists():
            print(f"[RASPAL] No config for {ota_name}")
            return None

        with open(config_path) as f:
            config = yaml.safe_load(f)

        url = config["url"].format(hotel_id=self.hotel_id)
        engine = config.get("engine", "stealth")

        print(f"[RASPAL] Fetching {ota_name} ...")
        try:
            self._lazy_init()
        except ImportError:
            print(f"[RASPAL] RASPAL not installed, skipping {ota_name}")
            return None

        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                fut = pool.submit(self.fetcher.fetch, url, engine=engine, cache_ttl=3600)
                result = fut.result(timeout=FETCH_TIMEOUT)

            price = None
            llm_config = config.get("llm")
            if llm_config and result.text and len(result.text) > 100:
                try:
                    from raspal import LLMExtractor
                    from raspal.models import LLMConfig
                    llm = LLMExtractor()
                    lc = LLMConfig(
                        model=llm_config.get("model", "llama3.2"),
                        template=llm_config.get("template", "hotel_pricing"),
                        output_schema=llm_config.get("output_schema", {"price": 0}),
                    )
                    parsed = llm.extract(result.text, lc)
                    price = parsed.get("price")
                except Exception as e:
                    print(f"  LLM extraction failed: {e}")

            if price is None:
                print(f"  No price extracted from {ota_name}")
                return None

            return {
                "ota": ota_name,
                "price": float(price),
                "currency": "EUR",
                "raw_length": len(result.text) if result.text else 0,
                "cached": result.cached if hasattr(result, "cached") else False,
                "timestamp": datetime.now().isoformat(),
            }

        except concurrent.futures.TimeoutError:
            print(f"  Timeout fetching {ota_name}")
            return None
        except Exception as e:
            print(f"  Error fetching {ota_name}: {e}")
            return None

    def scrape_all(self) -> list[dict]:
        results = []
        for ota_name in OTAS:
            data = self.scrape_one(ota_name)
            if data:
                results.append(data)
        return results

    def save_to_db(self, results: list[dict]) -> int:
        from app.database import get_db
        conn = get_db()
        cur = conn.cursor()
        saved = 0
        for r in results:
            cur.execute(
                """INSERT INTO competitor_prices (id, hotel_id, ota, price, currency, raw_data, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), self.hotel_id, r["ota"], r["price"],
                 r.get("currency", "EUR"), json.dumps(r), r["timestamp"])
            )
            saved += 1
        conn.commit()
        conn.close()
        print(f"[RASPAL] Saved {saved} prices to DB")
        return saved

    def run(self) -> list[dict]:
        results = self.scrape_all()
        if results:
            self.save_to_db(results)
        return results


def trigger_scrape(hotel_id: str = None) -> list[dict]:
    worker = RaspalWorker(hotel_id)
    return worker.run()
