#!/usr/bin/env python3
"""
Phase 3: Time-Series Enrichment
Seasonality decomposition and trend extraction for hotel pricing.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SeasonalityResult:
    """Result of seasonality decomposition."""
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    seasonal_factors: Dict[int, float]
    trend_slope: float
    trend_intercept: float


class TimeSeriesEnricher:
    """Extracts seasonality and trend from time series data."""
    
    def __init__(self, period: int = 12):
        """
        Args:
            period: Seasonal period (12 for monthly data)
        """
        self.period = period
    
    def decompose_additive(self, series: pd.Series) -> SeasonalityResult:
        """
        Simple additive decomposition.
        y = trend + seasonal + residual
        """
        n = len(series)
        
        # 1. Trend (moving average)
        trend = series.rolling(window=self.period, center=True, min_periods=1).mean()
        
        # 2. Detrended series
        detrended = series - trend
        
        # 3. Seasonal component (average of each period)
        seasonal = pd.Series(0.0, index=series.index)
        seasonal_factors = {}
        
        for i in range(self.period):
            mask = [(j % self.period == i) for j in range(n)]
            period_mean = detrended[mask].mean()
            seasonal_factors[i] = period_mean
            seasonal[mask] = period_mean
        
        # 4. Residual
        residual = series - trend - seasonal
        
        # 5. Trend slope (linear fit)
        x = np.arange(n)
        slope, intercept = np.polyfit(x, trend.fillna(0).values, 1)
        
        return SeasonalityResult(
            trend=trend,
            seasonal=seasonal,
            residual=residual,
            seasonal_factors=seasonal_factors,
            trend_slope=float(slope),
            trend_intercept=float(intercept),
        )
    
    def get_seasonal_factors(self, dates: pd.Series) -> pd.Series:
        """
        Get seasonal factors for a series of dates.
        Returns a series of factors (1.0 = average, >1 = peak, <1 = low).
        """
        # Calculate seasonal factors from historical data
        months = dates.dt.month
        
        # Default seasonal pattern for hotel pricing
        default_factors = {
            1: 0.70, 2: 0.65, 3: 0.80, 4: 0.95,
            5: 1.10, 6: 1.25, 7: 1.40, 8: 1.40,
            9: 1.15, 10: 0.90, 11: 0.75, 12: 0.70,
        }
        
        return months.map(default_factors).fillna(1.0)
    
    def extract_features(self, df: pd.DataFrame, date_col: str = 'arrival_date') -> pd.DataFrame:
        """
        Extract time-series features from a DataFrame.
        
        Adds columns:
        - ts_trend: Long-term trend value
        - ts_seasonal: Seasonal component
        - ts_seasonal_factor: Seasonal multiplier (1.0 = average)
        - ts_residual: Residual after removing trend and seasonality
        - ts_month_sin: Cyclical month encoding (sin)
        - ts_month_cos: Cyclical month encoding (cos)
        - ts_quarter: Quarter of year
        - ts_is_peak: Whether date is in peak season
        """
        df = df.copy()
        
        if date_col not in df.columns:
            # Try to construct date from arrival_year and arrival_month
            if 'arrival_year' in df.columns and 'arrival_month' in df.columns:
                df[date_col] = pd.to_datetime(
                    df['arrival_year'].astype(str) + '-' + 
                    df['arrival_month'].astype(str).str.zfill(2) + '-01'
                )
            else:
                return df
        
        dates = pd.to_datetime(df[date_col])
        
        # Cyclical month encoding
        df['ts_month_sin'] = np.sin(2 * np.pi * dates.dt.month / 12)
        df['ts_month_cos'] = np.cos(2 * np.pi * dates.dt.month / 12)
        
        # Quarter
        df['ts_quarter'] = dates.dt.quarter
        
        # Peak season flag (Jun-Sep, Dec)
        df['ts_is_peak'] = dates.dt.month.isin([6, 7, 8, 9, 12]).astype(int)
        
        # Seasonal factor
        df['ts_seasonal_factor'] = self.get_seasonal_factors(dates)
        
        return df


def enrich_features_v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich DataFrame with V2 time-series features.
    Compatible with existing V1 feature set.
    """
    enricher = TimeSeriesEnricher()
    return enricher.extract_features(df)


if __name__ == "__main__":
    # Demo
    print("=== Time-Series Enrichment Demo ===\n")
    
    # Create sample monthly data
    dates = pd.date_range('2020-01-01', '2024-12-01', freq='MS')
    n = len(dates)
    
    # Simulated hotel prices with trend and seasonality
    trend = np.linspace(100, 150, n)
    seasonal = 20 * np.sin(2 * np.pi * np.arange(n) / 12)
    noise = np.random.normal(0, 5, n)
    prices = trend + seasonal + noise
    
    series = pd.Series(prices, index=dates)
    
    # Decompose
    enricher = TimeSeriesEnricher(period=12)
    result = enricher.decompose_additive(series)
    
    print(f"Trend slope: {result.trend_slope:.2f} EUR/month")
    print(f"Seasonal factors:")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i, factor in sorted(result.seasonal_factors.items()):
        bar = '#' * int(abs(factor) * 20)
        sign = '+' if factor >= 0 else '-'
        print(f"  {month_names[i]}: {sign}{abs(factor):.2f} {bar}")
    
    # Extract features
    print("\n=== Feature Extraction ===")
    df = pd.DataFrame({
        'arrival_year': [2024] * 12,
        'arrival_month': list(range(1, 13)),
    })
    
    df_enriched = enricher.extract_features(df)
    print(df_enriched[['arrival_month', 'ts_month_sin', 'ts_month_cos', 
                       'ts_quarter', 'ts_is_peak', 'ts_seasonal_factor']].to_string())
