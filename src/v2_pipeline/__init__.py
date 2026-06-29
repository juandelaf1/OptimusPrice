"""
V2 Pipeline — Market Intelligence System
Multi-source data collection for hotel pricing intelligence.
"""

__version__ = "2.0.0"

from .market_db import MarketIntelligenceDB, VALID_REGIONS, VALID_SEGMENTS
from .ine_ingester import INEDataIngester
from .gtrends_ingester import GoogleTrendsIngester

__all__ = [
    'MarketIntelligenceDB',
    'INEDataIngester',
    'GoogleTrendsIngester',
    'VALID_REGIONS',
    'VALID_SEGMENTS',
]
