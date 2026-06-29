#!/usr/bin/env python3
"""
V2 Pipeline — Aggregator
Computes market aggregates from raw price data.
"""

from datetime import datetime, date
from typing import Optional, List
import statistics

from .ingester import MarketDatabase


class MarketAggregator:
    """Computes market aggregates from raw price data."""

    def __init__(self, db: Optional[MarketDatabase] = None):
        self.db = db or MarketDatabase()

    def compute_aggregates(
        self,
        target_date: str,
        location: str = "Mallorca",
        sublocation: Optional[str] = None,
        property_type: Optional[str] = None,
        star_rating: Optional[int] = None,
    ) -> dict:
        """
        Compute aggregates for a specific target date and filters.
        
        Returns:
            Dictionary with aggregated metrics
        """
        conditions = ["target_date = ?", "location = ?", "is_available = 1"]
        params = [target_date, location]
        
        if sublocation:
            conditions.append("sublocation = ?")
            params.append(sublocation)
        if property_type:
            conditions.append("property_type = ?")
            params.append(property_type)
        if star_rating:
            conditions.append("star_rating = ?")
            params.append(star_rating)
        
        where = " AND ".join(conditions)
        
        sql = f"""
        SELECT 
            price_per_night,
            days_ahead,
            source
        FROM market_prices
        WHERE {where}
        """
        
        import sqlite3
        from pathlib import Path
        
        db_path = self.db.db_path
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        
        if not rows:
            return {
                'target_date': target_date,
                'location': location,
                'sublocation': sublocation,
                'property_type': property_type,
                'star_rating': star_rating,
                'data_points_count': 0,
                'avg_price': None,
                'median_price': None,
                'min_price': None,
                'max_price': None,
                'std_price': None,
            }
        
        prices = [r['price_per_night'] for r in rows]
        days = [r['days_ahead'] for r in rows]
        
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)
        std_price = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Percentiles
        sorted_prices = sorted(prices)
        n = len(sorted_prices)
        p25 = sorted_prices[n // 4] if n >= 4 else min_price
        p75 = sorted_prices[3 * n // 4] if n >= 4 else max_price
        
        return {
            'aggregate_date': date.today().isoformat(),
            'target_date': target_date,
            'location': location,
            'sublocation': sublocation,
            'property_type': property_type,
            'star_rating': star_rating,
            'avg_price': round(avg_price, 2),
            'median_price': round(median_price, 2),
            'min_price': round(min_price, 2),
            'max_price': round(max_price, 2),
            'std_price': round(std_price, 2),
            'total_listings': len(rows),
            'available_listings': len(rows),
            'unavailable_listings': 0,
            'avg_days_ahead': round(statistics.mean(days), 1),
            'price_percentile_25': round(p25, 2),
            'price_percentile_75': round(p75, 2),
            'data_points_count': len(rows),
            'last_updated': datetime.now().isoformat(),
        }

    def compute_all_aggregates(
        self,
        target_dates: Optional[List[str]] = None,
        location: str = "Mallorca",
    ) -> dict:
        """
        Compute aggregates for all target dates.
        
        Returns:
            Summary with dates processed and aggregates computed
        """
        if target_dates is None:
            # Get distinct target dates from database
            import sqlite3
            sql = "SELECT DISTINCT target_date FROM market_prices ORDER BY target_date"
            with sqlite3.connect(str(self.db.db_path)) as conn:
                rows = conn.execute(sql).fetchall()
                target_dates = [r[0] for r in rows]
        
        results = []
        for target_date in target_dates:
            agg = self.compute_aggregates(target_date, location)
            results.append(agg)
            
            # Store aggregate
            self._store_aggregate(agg)
        
        return {
            'dates_processed': len(results),
            'aggregates_computed': len([r for r in results if r['data_points_count'] > 0]),
            'total_data_points': sum(r['data_points_count'] for r in results),
        }

    def _store_aggregate(self, agg: dict):
        """Store aggregate in database."""
        sql = """
        INSERT OR REPLACE INTO market_aggregates (
            aggregate_date, target_date, location, sublocation,
            property_type, star_rating,
            avg_price, median_price, min_price, max_price, std_price,
            total_listings, available_listings, unavailable_listings,
            avg_days_ahead, price_percentile_25, price_percentile_75,
            data_points_count, last_updated
        ) VALUES (
            :aggregate_date, :target_date, :location, :sublocation,
            :property_type, :star_rating,
            :avg_price, :median_price, :min_price, :max_price, :std_price,
            :total_listings, :available_listings, :unavailable_listings,
            :avg_days_ahead, :price_percentile_25, :price_percentile_75,
            :data_points_count, :last_updated
        )
        """
        
        import sqlite3
        with sqlite3.connect(str(self.db.db_path)) as conn:
            conn.execute(sql, agg)

    def get_market_context(
        self,
        target_date: str,
        sublocation: Optional[str] = None,
    ) -> dict:
        """
        Get market context for a specific date.
        
        Returns:
            Dictionary with avg, min, max prices and listing counts
        """
        agg = self.compute_aggregates(target_date, sublocation=sublocation)
        
        return {
            'avg_competitor_price': agg['avg_price'],
            'min_price': agg['min_price'],
            'max_price': agg['max_price'],
            'total_listings': agg['total_listings'],
            'data_freshness': 'last_7_days' if agg['data_points_count'] > 0 else 'no_data',
        }


if __name__ == "__main__":
    aggregator = MarketAggregator()
    
    # Example: compute aggregates for a specific date
    result = aggregator.compute_aggregates("2025-07-15")
    print(f"Aggregates for 2025-07-15: {result}")
    
    # Get market context
    context = aggregator.get_market_context("2025-07-15", "Palma")
    print(f"Market context: {context}")
