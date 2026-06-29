#!/usr/bin/env python3
"""
V2 Pipeline — Google Trends Data Ingester
Parses and ingests Google Trends data for tourism demand signals.
Google Trends provides free CSV exports of search interest over time.
"""

import csv
import re
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional

from .market_db import MarketIntelligenceDB


BASE_DIR = Path(__file__).resolve().parent.parent.parent
GTRENDS_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "google_trends"

# Tourism-related search queries for Mallorca
DEFAULT_QUERIES = [
    'Mallorca hotels',
    'Mallorca apartments',
    'Mallorca tourism',
    'Mallorca weather',
    'Mallorca things to do',
    'Alcudia hotels',
    'Palma de Mallorca hotels',
    'Magaluf hotels',
]


class GoogleTrendsIngester:
    """Parses and ingests Google Trends CSV exports."""

    def __init__(self, db: Optional[MarketIntelligenceDB] = None):
        self.db = db or MarketIntelligenceDB()
        GTRENDS_DIR.mkdir(parents=True, exist_ok=True)

    def parse_trends_csv(self, filepath: Path) -> List[Dict]:
        """Parse a Google Trends CSV export."""
        records = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if len(rows) < 2:
            return records

        # Google Trends format: first row is header with query names
        # Second row onwards: "date, value1, value2, ..."
        header = rows[0]
        query_names = [h.strip() for h in header[1:]]

        for row in rows[1:]:
            if not row or not row[0].strip():
                continue
            date_str = row[0].strip()
            # Parse date (format: "2024-01-01" or "2024-01")
            parsed_date = self._parse_date(date_str)
            if not parsed_date:
                continue

            for i, query in enumerate(query_names):
                if i + 1 < len(row):
                    value = self._parse_number(row[i + 1])
                    if value is not None:
                        records.append({
                            'date': parsed_date,
                            'query': query,
                            'value': value,
                            'source_file': filepath.stem,
                        })

        return records

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string from Google Trends."""
        date_str = date_str.strip()
        for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse a numeric value."""
        if not value_str or value_str.strip() in ('', '<1', 'N/A'):
            return None
        value_str = value_str.strip().replace('<', '')
        try:
            return float(value_str)
        except ValueError:
            return None

    def _query_to_region(self, query: str) -> tuple:
        """Map a search query to region/subregion."""
        query_lower = query.lower()
        if 'alcudia' in query_lower:
            return 'mallorca', 'alcudia'
        if 'palma' in query_lower:
            return 'mallorca', 'palma'
        if 'magaluf' in query_lower:
            return 'mallorca', 'magaluf'
        if 'menorca' in query_lower:
            return 'mallorca', 'menorca'
        if 'ibiza' in query_lower:
            return 'mallorca', 'ibiza'
        return 'mallorca', None

    def ingest_csv(self, filepath: Path) -> dict:
        """Parse a Google Trends CSV and insert into database."""
        records = self.parse_trends_csv(filepath)
        if not records:
            return {'inserted': 0, 'message': 'No valid records found'}

        inserted = 0
        for record in records:
            try:
                region, subregion = self._query_to_region(record['query'])
                self.db.insert_demand_signal({
                    'signal_date': record['date'],
                    'region': region,
                    'subregion': subregion,
                    'search_volume_index': record['value'],
                    'source': 'google_trends',
                    'source_metric': record['query'],
                })
                inserted += 1
            except Exception:
                pass

        return {'inserted': inserted, 'total_parsed': len(records)}

    def ingest_directory(self) -> dict:
        """Ingest all CSV files in the Google Trends directory."""
        results = []
        for csv_file in GTRENDS_DIR.glob('*.csv'):
            result = self.ingest_csv(csv_file)
            results.append({'file': csv_file.name, **result})
        return {'files_processed': len(results), 'results': results}

    def create_sample_data(self):
        """Create sample Google Trends-like data for testing."""
        import random
        random.seed(42)

        sample_records = []
        base_date = date(2020, 1, 1)

        # Simulate 60 months of search volume data
        for month_offset in range(60):
            current_date = date(
                2020 + month_offset // 12,
                (month_offset % 12) + 1,
                1
            )
            month = current_date.month

            # Seasonal pattern for search volume
            seasonal = {
                1: 30, 2: 25, 3: 40, 4: 55,
                5: 70, 6: 85, 7: 100, 8: 95,
                9: 75, 10: 55, 11: 35, 12: 30,
            }
            base_volume = seasonal[month]
            noise = random.uniform(-5, 5)
            trend = (month_offset / 12) * 2  # Slight upward trend

            queries = ['Mallorca hotels', 'Palma de Mallorca hotels', 'Mallorca tourism']
            for query in queries:
                region, subregion = self._query_to_region(query)
                sample_records.append({
                    'signal_date': current_date,
                    'region': region,
                    'subregion': subregion,
                    'search_volume_index': min(100, max(0, base_volume + noise + trend)),
                    'source': 'google_trends',
                    'source_metric': query,
                })

        for record in sample_records:
            self.db.insert_demand_signal(record)

        return {'records_created': len(sample_records)}


if __name__ == "__main__":
    ingester = GoogleTrendsIngester()
    result = ingester.create_sample_data()
    print(f"Sample data created: {result}")
    stats = ingester.db.get_stats()
    print(f"Database stats: {stats}")
