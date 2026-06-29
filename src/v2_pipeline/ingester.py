#!/usr/bin/env python3
"""
V2 Pipeline — Database Ingestion
Manages SQLite database for market prices with segment support.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Dict
from contextlib import contextmanager


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data" / "v2_market" / "processed"
DB_PATH = DB_DIR / "market_prices.db"

VALID_SEGMENTS = [
    'palma_urbano',
    'playa_costa',
    'magaluf_party',
    'alcudia_family',
    'interior_rural',
    'luxury_villas',
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS market_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date DATE NOT NULL,
    target_date DATE NOT NULL,
    days_ahead INTEGER NOT NULL,
    segment TEXT NOT NULL,
    location TEXT NOT NULL,
    sublocation TEXT,
    latitude REAL,
    longitude REAL,
    property_type TEXT NOT NULL,
    property_name TEXT,
    star_rating INTEGER,
    bedrooms INTEGER,
    max_guests INTEGER,
    price_per_night REAL NOT NULL,
    currency TEXT DEFAULT 'EUR',
    original_currency TEXT,
    original_price REAL,
    is_available BOOLEAN DEFAULT 1,
    min_nights INTEGER DEFAULT 1,
    max_nights INTEGER,
    source TEXT NOT NULL,
    listing_id TEXT,
    scraping_method TEXT,
    collected_at TIMESTAMP NOT NULL,
    data_quality_score REAL DEFAULT 1.0,
    UNIQUE(snapshot_date, target_date, source, listing_id)
);

CREATE INDEX IF NOT EXISTS idx_market_prices_target ON market_prices(target_date);
CREATE INDEX IF NOT EXISTS idx_market_prices_location ON market_prices(location, sublocation);
CREATE INDEX IF NOT EXISTS idx_market_prices_source ON market_prices(source);
CREATE INDEX IF NOT EXISTS idx_market_prices_snapshot ON market_prices(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_market_prices_segment ON market_prices(segment);

CREATE TABLE IF NOT EXISTS market_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aggregate_date DATE NOT NULL,
    target_date DATE NOT NULL,
    segment TEXT NOT NULL,
    location TEXT NOT NULL,
    sublocation TEXT,
    property_type TEXT,
    star_rating INTEGER,
    avg_price REAL,
    median_price REAL,
    min_price REAL,
    max_price REAL,
    std_price REAL,
    total_listings INTEGER,
    available_listings INTEGER,
    unavailable_listings INTEGER,
    avg_days_ahead REAL,
    price_percentile_25 REAL,
    price_percentile_75 REAL,
    data_points_count INTEGER,
    last_updated TIMESTAMP,
    UNIQUE(aggregate_date, target_date, segment, location, sublocation, property_type, star_rating)
);
"""


class MarketDatabase:
    """Manages the market prices SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def _conn(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def insert_price(self, data: dict) -> int:
        """
        Insert a single market price record.
        
        Args:
            data: Dictionary with market price fields
            
        Returns:
            Row ID of inserted record
        """
        sql = """
        INSERT OR REPLACE INTO market_prices (
            snapshot_date, target_date, days_ahead,
            segment, location, sublocation, latitude, longitude,
            property_type, property_name, star_rating, bedrooms, max_guests,
            price_per_night, currency, original_currency, original_price,
            is_available, min_nights, max_nights,
            source, listing_id, scraping_method,
            collected_at, data_quality_score
        ) VALUES (
            :snapshot_date, :target_date, :days_ahead,
            :segment, :location, :sublocation, :latitude, :longitude,
            :property_type, :property_name, :star_rating, :bedrooms, :max_guests,
            :price_per_night, :currency, :original_currency, :original_price,
            :is_available, :min_nights, :max_nights,
            :source, :listing_id, :scraping_method,
            :collected_at, :data_quality_score
        )
        """
        
        # Set defaults for all optional fields
        defaults = {
            'segment': 'playa_costa',
            'location': 'Mallorca',
            'currency': 'EUR',
            'is_available': 1,
            'min_nights': 1,
            'collected_at': datetime.now().isoformat(),
            'data_quality_score': 1.0,
            'sublocation': None,
            'latitude': None,
            'longitude': None,
            'property_name': None,
            'star_rating': None,
            'bedrooms': None,
            'max_guests': None,
            'original_currency': None,
            'original_price': None,
            'max_nights': None,
            'listing_id': None,
            'scraping_method': None,
        }
        for key, value in defaults.items():
            data.setdefault(key, value)
        
        # Validate segment
        if data['segment'] not in VALID_SEGMENTS:
            raise ValueError(f"Invalid segment: {data['segment']}. Must be one of {VALID_SEGMENTS}")
        
        # Calculate days_ahead
        if 'days_ahead' not in data:
            snapshot = data['snapshot_date']
            target = data['target_date']
            if isinstance(snapshot, str):
                snapshot = datetime.strptime(snapshot, '%Y-%m-%d').date()
            if isinstance(target, str):
                target = datetime.strptime(target, '%Y-%m-%d').date()
            data['days_ahead'] = (target - snapshot).days
        
        with self._conn() as conn:
            cursor = conn.execute(sql, data)
            return cursor.lastrowid

    def insert_batch(self, records: List[dict]) -> dict:
        """
        Insert a batch of records.
        
        Returns:
            Summary with inserted, failed, errors
        """
        inserted = 0
        failed = 0
        errors = []
        
        for record in records:
            try:
                self.insert_price(record)
                inserted += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
        return {
            'inserted': inserted,
            'failed': failed,
            'errors': errors[:10]
        }

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM market_prices").fetchone()[0]
            sources = conn.execute(
                "SELECT source, COUNT(*) as cnt FROM market_prices GROUP BY source"
            ).fetchall()
            date_range = conn.execute(
                "SELECT MIN(target_date), MAX(target_date) FROM market_prices"
            ).fetchone()
            locations = conn.execute(
                "SELECT sublocation, COUNT(*) as cnt FROM market_prices GROUP BY sublocation"
            ).fetchall()
            segments = conn.execute(
                "SELECT segment, COUNT(*) as cnt FROM market_prices GROUP BY segment"
            ).fetchall()
            
            return {
                'total_records': total,
                'by_source': {r['source']: r['cnt'] for r in sources},
                'date_range': {
                    'min': date_range[0],
                    'max': date_range[1]
                },
                'by_location': {r['sublocation']: r['cnt'] for r in locations},
                'by_segment': {r['segment']: r['cnt'] for r in segments},
            }

    def get_segment_stats(self) -> dict:
        """Get statistics per segment."""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT 
                    segment,
                    COUNT(*) as total_records,
                    COUNT(DISTINCT listing_id) as unique_listings,
                    AVG(price_per_night) as avg_price,
                    MIN(target_date) as earliest_date,
                    MAX(target_date) as latest_date
                FROM market_prices
                GROUP BY segment
                ORDER BY total_records DESC
            """).fetchall()
            
            return {r['segment']: dict(r) for r in rows}

    def query_prices(
        self,
        target_date: Optional[str] = None,
        segment: Optional[str] = None,
        sublocation: Optional[str] = None,
        property_type: Optional[str] = None,
        source: Optional[str] = None,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Query market prices with filters.
        
        Returns:
            List of matching records
        """
        conditions = []
        params = {}
        
        if target_date:
            conditions.append("target_date = :target_date")
            params['target_date'] = target_date
        if segment:
            conditions.append("segment = :segment")
            params['segment'] = segment
        if sublocation:
            conditions.append("sublocation = :sublocation")
            params['sublocation'] = sublocation
        if property_type:
            conditions.append("property_type = :property_type")
            params['property_type'] = property_type
        if source:
            conditions.append("source = :source")
            params['source'] = source
        if min_date:
            conditions.append("target_date >= :min_date")
            params['min_date'] = min_date
        if max_date:
            conditions.append("target_date <= :max_date")
            params['max_date'] = max_date
        
        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM market_prices WHERE {where} LIMIT :limit"
        params['limit'] = limit
        
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]


if __name__ == "__main__":
    db = MarketDatabase()
    print(f"Database initialized at: {db.db_path}")
    print(f"Stats: {db.get_stats()}")
    print(f"Valid segments: {VALID_SEGMENTS}")
