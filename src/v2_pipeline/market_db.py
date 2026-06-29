#!/usr/bin/env python3
"""
V2 Pipeline — Market Intelligence Database
Schema for market_index, price_bands, demand_signals, seasonality_index.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Dict
from contextlib import contextmanager


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data" / "v2_market" / "processed"
DB_PATH = DB_DIR / "market_intelligence.db"

VALID_REGIONS = ['mallorca', 'baleares', 'costa_del_sol', 'barcelona', 'valencia']
VALID_SEGMENTS = [
    'palma_urbano', 'playa_costa', 'magaluf_party',
    'alcudia_family', 'interior_rural', 'luxury_villas',
]
VALID_PERIODS = ['daily', 'weekly', 'monthly']
VALID_SOURCES = ['ine', 'google_trends', 'aemet', 'airbnb', 'manual', 'dataset', 'airdna']
VALID_CONFIDENCE = ['high', 'medium', 'low']
VALID_SEASONS = ['peak', 'high', 'shoulder', 'low']
VALID_ACCOMMODATIONS = ['hotel', 'apartment', 'villa', 'rural_house', None]

SCHEMA_SQL = """
-- Market index: precio agregado por región/zona
CREATE TABLE IF NOT EXISTS market_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_date DATE NOT NULL,
    period TEXT NOT NULL DEFAULT 'monthly',
    region TEXT NOT NULL DEFAULT 'mallorca',
    subregion TEXT,
    segment TEXT NOT NULL,
    accommodation_type TEXT,
    price_index REAL NOT NULL,
    avg_price REAL,
    median_price REAL,
    price_change_pct REAL,
    sample_size INTEGER NOT NULL DEFAULT 1,
    confidence_level TEXT DEFAULT 'medium',
    source TEXT NOT NULL,
    source_url TEXT,
    data_freshness_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_date, period, region, subregion, segment, accommodation_type)
);

-- Price bands: distribución de precios por zona/temporada
CREATE TABLE IF NOT EXISTS price_bands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    band_date DATE NOT NULL,
    season TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT 'mallorca',
    subregion TEXT,
    segment TEXT NOT NULL,
    budget_max REAL,
    mid_min REAL,
    mid_max REAL,
    premium_min REAL,
    budget_pct REAL,
    mid_pct REAL,
    premium_pct REAL,
    source TEXT NOT NULL,
    sample_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(band_date, season, region, subregion, segment)
);

-- Demand signals: proxy de demanda turística
CREATE TABLE IF NOT EXISTS demand_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_date DATE NOT NULL,
    region TEXT NOT NULL DEFAULT 'mallorca',
    subregion TEXT,
    search_volume_index REAL,
    booking_pace REAL,
    occupancy_estimate REAL,
    event_impact REAL,
    source TEXT NOT NULL,
    source_metric TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(signal_date, region, subregion, source)
);

-- Seasonality index: factores estacionales históricos
CREATE TABLE IF NOT EXISTS seasonality_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month INTEGER NOT NULL,
    day_of_week INTEGER,
    region TEXT NOT NULL DEFAULT 'mallorca',
    segment TEXT NOT NULL,
    seasonality_factor REAL NOT NULL DEFAULT 1.0,
    avg_occupancy REAL,
    avg_price_index REAL,
    years_of_data INTEGER,
    data_sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month, day_of_week, region, segment)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_mi_date ON market_index(index_date);
CREATE INDEX IF NOT EXISTS idx_mi_region ON market_index(region, subregion);
CREATE INDEX IF NOT EXISTS idx_mi_segment ON market_index(segment);
CREATE INDEX IF NOT EXISTS idx_pb_date ON price_bands(band_date);
CREATE INDEX IF NOT EXISTS idx_pb_segment ON price_bands(segment);
CREATE INDEX IF NOT EXISTS idx_ds_date ON demand_signals(signal_date);
CREATE INDEX IF NOT EXISTS idx_ds_region ON demand_signals(region);
CREATE INDEX IF NOT EXISTS idx_si_month ON seasonality_index(month, region);
"""


class MarketIntelligenceDB:
    """Market intelligence database manager."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def _conn(self):
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

    def insert_market_index(self, data: dict) -> int:
        sql = """
        INSERT OR REPLACE INTO market_index (
            index_date, period, region, subregion, segment,
            accommodation_type, price_index, avg_price, median_price,
            price_change_pct, sample_size, confidence_level,
            source, source_url, data_freshness_days
        ) VALUES (
            :index_date, :period, :region, :subregion, :segment,
            :accommodation_type, :price_index, :avg_price, :median_price,
            :price_change_pct, :sample_size, :confidence_level,
            :source, :source_url, :data_freshness_days
        )
        """
        defaults = {
            'period': 'monthly', 'region': 'mallorca', 'subregion': None,
            'accommodation_type': None, 'avg_price': None, 'median_price': None,
            'price_change_pct': None, 'confidence_level': 'medium',
            'source_url': None, 'data_freshness_days': None,
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        with self._conn() as conn:
            return conn.execute(sql, data).lastrowid

    def insert_price_band(self, data: dict) -> int:
        sql = """
        INSERT OR REPLACE INTO price_bands (
            band_date, season, region, subregion, segment,
            budget_max, mid_min, mid_max, premium_min,
            budget_pct, mid_pct, premium_pct,
            source, sample_size
        ) VALUES (
            :band_date, :season, :region, :subregion, :segment,
            :budget_max, :mid_min, :mid_max, :premium_min,
            :budget_pct, :mid_pct, :premium_pct,
            :source, :sample_size
        )
        """
        defaults = {
            'region': 'mallorca', 'subregion': None,
            'budget_max': None, 'mid_min': None, 'mid_max': None, 'premium_min': None,
            'budget_pct': None, 'mid_pct': None, 'premium_pct': None, 'sample_size': None,
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        with self._conn() as conn:
            return conn.execute(sql, data).lastrowid

    def insert_demand_signal(self, data: dict) -> int:
        sql = """
        INSERT OR REPLACE INTO demand_signals (
            signal_date, region, subregion,
            search_volume_index, booking_pace, occupancy_estimate, event_impact,
            source, source_metric
        ) VALUES (
            :signal_date, :region, :subregion,
            :search_volume_index, :booking_pace, :occupancy_estimate, :event_impact,
            :source, :source_metric
        )
        """
        defaults = {
            'region': 'mallorca', 'subregion': None,
            'search_volume_index': None, 'booking_pace': None,
            'occupancy_estimate': None, 'event_impact': None, 'source_metric': None,
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        with self._conn() as conn:
            return conn.execute(sql, data).lastrowid

    def insert_seasonality(self, data: dict) -> int:
        sql = """
        INSERT OR REPLACE INTO seasonality_index (
            month, day_of_week, region, segment,
            seasonality_factor, avg_occupancy, avg_price_index,
            years_of_data, data_sources
        ) VALUES (
            :month, :day_of_week, :region, :segment,
            :seasonality_factor, :avg_occupancy, :avg_price_index,
            :years_of_data, :data_sources
        )
        """
        defaults = {
            'day_of_week': None, 'avg_occupancy': None, 'avg_price_index': None,
            'years_of_data': None, 'data_sources': None,
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        with self._conn() as conn:
            return conn.execute(sql, data).lastrowid

    def insert_batch(self, table: str, records: List[dict]) -> dict:
        inserters = {
            'market_index': self.insert_market_index,
            'price_bands': self.insert_price_band,
            'demand_signals': self.insert_demand_signal,
            'seasonality_index': self.insert_seasonality,
        }
        inserter = inserters.get(table)
        if not inserter:
            raise ValueError(f"Unknown table: {table}")
        inserted = 0
        failed = 0
        errors = []
        for record in records:
            try:
                inserter(record)
                inserted += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
        return {'inserted': inserted, 'failed': failed, 'errors': errors[:10]}

    def get_stats(self) -> dict:
        with self._conn() as conn:
            tables = ['market_index', 'price_bands', 'demand_signals', 'seasonality_index']
            stats = {}
            for t in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                stats[t] = count
            return stats

    def query_market_index(
        self,
        region: str = 'mallorca',
        segment: Optional[str] = None,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        conditions = ["region = :region"]
        params = {'region': region, 'limit': limit}
        if segment:
            conditions.append("segment = :segment")
            params['segment'] = segment
        if min_date:
            conditions.append("index_date >= :min_date")
            params['min_date'] = min_date
        if max_date:
            conditions.append("index_date <= :max_date")
            params['max_date'] = max_date
        where = " AND ".join(conditions)
        sql = f"SELECT * FROM market_index WHERE {where} ORDER BY index_date DESC LIMIT :limit"
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def query_seasonality(
        self,
        region: str = 'mallorca',
        segment: Optional[str] = None
    ) -> List[dict]:
        conditions = ["region = :region"]
        params = {'region': region}
        if segment:
            conditions.append("segment = :segment")
            params['segment'] = segment
        where = " AND ".join(conditions)
        sql = f"SELECT * FROM seasonality_index WHERE {where} ORDER BY month"
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]


if __name__ == "__main__":
    db = MarketIntelligenceDB()
    print(f"Database: {db.db_path}")
    print(f"Stats: {db.get_stats()}")
