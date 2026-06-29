#!/usr/bin/env python3
"""
V2 Pipeline — Minimal Tests
Tests for the V2 market intelligence pipeline.
"""

import sys
import tempfile
from pathlib import Path
from datetime import date

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.v2_pipeline.market_db import MarketIntelligenceDB, VALID_REGIONS, VALID_SEGMENTS
from src.v2_pipeline.ine_ingester import INEDataIngester
from src.v2_pipeline.gtrends_ingester import GoogleTrendsIngester


def test_market_db_creation():
    """Test that MarketIntelligenceDB creates tables correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = MarketIntelligenceDB(db_path)
        stats = db.get_stats()
        assert all(v == 0 for v in stats.values()), f"Fresh DB should have 0 records: {stats}"
        print("PASS: test_market_db_creation")


def test_market_index_insert():
    """Test market_index insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        db.insert_market_index({
            'index_date': date(2024, 1, 1),
            'period': 'monthly',
            'region': 'mallorca',
            'segment': 'playa_costa',
            'price_index': 100.0,
            'avg_price': 150.0,
            'sample_size': 10,
            'source': 'ine',
        })
        stats = db.get_stats()
        assert stats['market_index'] == 1, f"Expected 1, got {stats['market_index']}"
        print("PASS: test_market_index_insert")


def test_demand_signal_insert():
    """Test demand_signals insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        db.insert_demand_signal({
            'signal_date': date(2024, 7, 1),
            'region': 'mallorca',
            'occupancy_estimate': 0.85,
            'source': 'ine',
        })
        stats = db.get_stats()
        assert stats['demand_signals'] == 1, f"Expected 1, got {stats['demand_signals']}"
        print("PASS: test_demand_signal_insert")


def test_seasonality_insert():
    """Test seasonality_index insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        db.insert_seasonality({
            'month': 7,
            'region': 'mallorca',
            'segment': 'playa_costa',
            'seasonality_factor': 1.0,
        })
        stats = db.get_stats()
        assert stats['seasonality_index'] == 1, f"Expected 1, got {stats['seasonality_index']}"
        print("PASS: test_seasonality_insert")


def test_price_band_insert():
    """Test price_bands insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        db.insert_price_band({
            'band_date': date(2024, 7, 1),
            'season': 'peak',
            'region': 'mallorca',
            'segment': 'playa_costa',
            'budget_max': 80,
            'mid_min': 80,
            'mid_max': 200,
            'premium_min': 200,
            'source': 'manual',
        })
        stats = db.get_stats()
        assert stats['price_bands'] == 1, f"Expected 1, got {stats['price_bands']}"
        print("PASS: test_price_band_insert")


def test_batch_insert():
    """Test batch insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        records = [
            {
                'index_date': date(2024, m, 1),
                'period': 'monthly',
                'region': 'mallorca',
                'segment': 'playa_costa',
                'price_index': 100.0 + m,
                'sample_size': 10,
                'source': 'ine',
            }
            for m in range(1, 13)
        ]
        result = db.insert_batch('market_index', records)
        assert result['inserted'] == 12, f"Expected 12, got {result}"
        stats = db.get_stats()
        assert stats['market_index'] == 12
        print("PASS: test_batch_insert")


def test_ine_ingester_sample_data():
    """Test INE ingester sample data creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        ingester = INEDataIngester(db)
        result = ingester.create_sample_data()
        assert result['records_created'] > 0, "Should create sample records"
        stats = db.get_stats()
        assert stats['demand_signals'] > 0, "Should have demand signals"
        assert stats['seasonality_index'] > 0, "Should have seasonality"
        print("PASS: test_ine_ingester_sample_data")


def test_gtrends_ingester_sample_data():
    """Test Google Trends ingester sample data creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        ingester = GoogleTrendsIngester(db)
        result = ingester.create_sample_data()
        assert result['records_created'] > 0, "Should create sample records"
        stats = db.get_stats()
        assert stats['demand_signals'] > 0, "Should have demand signals"
        print("PASS: test_gtrends_ingester_sample_data")


def test_query_market_index():
    """Test querying market_index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MarketIntelligenceDB(Path(tmpdir) / "test.db")
        for m in range(1, 13):
            db.insert_market_index({
                'index_date': date(2024, m, 1),
                'period': 'monthly',
                'region': 'mallorca',
                'segment': 'playa_costa',
                'price_index': 100.0 + m,
                'sample_size': 10,
                'source': 'ine',
            })
        results = db.query_market_index(region='mallorca', segment='playa_costa')
        assert len(results) == 12, f"Expected 12, got {len(results)}"
        print("PASS: test_query_market_index")


def test_valid_constants():
    """Test that validation constants are defined."""
    assert len(VALID_REGIONS) > 0, "VALID_REGIONS should not be empty"
    assert len(VALID_SEGMENTS) > 0, "VALID_SEGMENTS should not be empty"
    assert 'mallorca' in VALID_REGIONS, "mallorca should be in VALID_REGIONS"
    print("PASS: test_valid_constants")


if __name__ == "__main__":
    tests = [
        test_market_db_creation,
        test_market_index_insert,
        test_demand_signal_insert,
        test_seasonality_insert,
        test_price_band_insert,
        test_batch_insert,
        test_ine_ingester_sample_data,
        test_gtrends_ingester_sample_data,
        test_query_market_index,
        test_valid_constants,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {len(tests)} total")
