import sys
sys.path.insert(0, '.')
from pathlib import Path
from src.v2_pipeline.market_db import MarketIntelligenceDB

db = MarketIntelligenceDB(Path('data/v2_market/processed/market_intelligence.db'))

with db._conn() as conn:
    rows = conn.execute("SELECT signal_date, occupancy_estimate, source_metric FROM demand_signals WHERE source = 'ine' LIMIT 10").fetchall()
    print('Raw occupancy values:')
    for r in rows:
        print('  %s: %.3f (%s)' % (r['signal_date'], r['occupancy_estimate'], r['source_metric']))
