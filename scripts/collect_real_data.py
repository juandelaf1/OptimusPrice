#!/usr/bin/env python3
"""
Real Data Collection for Optimus Price
Uses RASPAL for fetching + Groq API for LLM extraction
"""

import sys, os, json, time, re
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")

import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from raspal import Fetcher, AutoThrottle, Extractor


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "scraped"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CITIES = [
    "Madrid", "Barcelona", "Paris", "London", "Rome",
    "Amsterdam", "Berlin", "Milan", "Lisbon", "Prague",
    "Vienna", "Brussels", "Zurich", "Dublin", "Edinburgh",
]

DATE_RANGES = [
    (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
    for i in range(1, 8)
]


def groq_extract_hotels(text: str) -> List[Dict]:
    prompt = f"""Extract ALL hotel pricing information from this hotel search results page.

For EACH hotel visible on the page, extract:
- name: hotel name
- price: numeric price (no currency symbol)
- currency: currency code (EUR, USD, GBP, etc.)
- rating: rating score (0-10)
- room_type: room type if mentioned
- availability: "available" or "sold_out"

Return a JSON array of hotel objects. Only include hotels with actual prices shown.
If no hotels found, return an empty array [].

Page text:
{text[:4000]}

Return ONLY the JSON array. No explanation."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 2000,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(content)
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "hotels" in result:
            return result["hotels"]
        return []
    except Exception as e:
        return []


class RealDataCollector:
    def __init__(self):
        self.fetcher = Fetcher(throttle=AutoThrottle(min_delay=2, max_delay=8))
        self.extractor = Extractor()
        self.results = []

    def collect_city_date(self, city: str, checkin: str, checkout: str) -> List[Dict]:
        records = []
        urls = {
            "booking.com": f"https://www.booking.com/searchresults.html?ss={city}&checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1",
            "trivago.es": f"https://www.trivago.es/es/srl/hoteles?search={city}&dates={checkin},{checkout}",
        }

        for ota, url in urls.items():
            try:
                r = self.fetcher.fetch(url, engine="stealth", timeout=15000)
                if not r.html or len(r.html) < 1000:
                    continue

                text = self.extractor.extract_text(r.html)
                if not text or len(text) < 100:
                    continue

                hotels = groq_extract_hotels(text)
                for hotel in hotels:
                    price = hotel.get("price")
                    if price and float(price) > 0:
                        records.append({
                            "city": city,
                            "ota": ota,
                            "checkin": checkin,
                            "checkout": checkout,
                            "hotel_name": hotel.get("name", ""),
                            "price": float(price),
                            "currency": hotel.get("currency", "EUR"),
                            "rating": hotel.get("rating", 0),
                            "room_type": hotel.get("room_type", ""),
                            "availability": hotel.get("availability", "available"),
                            "scrape_timestamp": datetime.now().isoformat(),
                        })
                print(f"  {ota}: {len(hotels)} hotels extracted")

            except Exception as e:
                print(f"  {ota} error: {str(e)[:60]}")

            time.sleep(2)

        return records

    def collect_batch(
        self,
        cities: List[str],
        dates: List[str],
        delay: float = 3.0,
    ) -> pd.DataFrame:
        total = len(cities) * len(dates)
        count = 0
        all_records = []

        print(f"\nCollection: {len(cities)} cities x {len(dates)} dates = {total} searches")
        print(f"Estimated time: {total * delay * 2 / 60:.1f} minutes (2 OTAs per search)\n")

        for checkin in dates:
            dt = datetime.strptime(checkin, "%Y-%m-%d")
            checkout = (dt + timedelta(days=1)).strftime("%Y-%m-%d")

            for city in cities:
                count += 1
                pct = count / total * 100
                print(f"[{count}/{total} {pct:.0f}%] {city} | {checkin}")

                records = self.collect_city_date(city, checkin, checkout)
                all_records.extend(records)
                print(f"  Collected: {len(records)} records (total: {len(all_records)})")

                time.sleep(delay)

        df = pd.DataFrame(all_records)
        return df

    def save_results(self, df: pd.DataFrame, tag: str = "real") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if len(df) > 0:
            csv_path = DATA_DIR / f"{tag}_data_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            print(f"\nSaved {len(df)} records to {csv_path}")

            print(f"\nSummary:")
            print(f"  Total records: {len(df)}")
            print(f"  Cities: {df['city'].nunique()}")
            print(f"  OTAs: {df['ota'].unique().tolist()}")
            print(f"  Price range: {df['price'].min():.2f} - {df['price'].max():.2f}")
            print(f"  Avg price: {df['price'].mean():.2f}")

            return str(csv_path)
        else:
            print("\nNo records to save")
            return ""


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Collect real hotel pricing data")
    parser.add_argument("--cities", type=int, default=5, help="Number of cities")
    parser.add_argument("--dates", type=int, default=3, help="Number of dates")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between requests")
    parser.add_argument("--tag", type=str, default="real", help="Output tag")
    args = parser.parse_args()

    print("=" * 60)
    print("REAL DATA COLLECTION - Optimus Price")
    print("Using RASPAL + Groq API")
    print("=" * 60)

    collector = RealDataCollector()
    selected_cities = CITIES[: args.cities]
    selected_dates = DATE_RANGES[: args.dates]

    print(f"\nConfig: {len(selected_cities)} cities, {len(selected_dates)} dates")

    df = collector.collect_batch(selected_cities, selected_dates, delay=args.delay)
    collector.save_results(df, tag=args.tag)


if __name__ == "__main__":
    main()
