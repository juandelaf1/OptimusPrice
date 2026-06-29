# V2 DATASET SPECIFICATION — Mallorca Market Data

**Version**: 2.0
**Status**: ACTIVE
**Last Updated**: June 2026

---

## 1. Dataset Definition

### 1.1 Purpose

Capture real market pricing data for Mallorca accommodations to train V2 pricing models, with segment-aware collection.

### 1.2 Scope

| Attribute | Value |
|-----------|-------|
| **Geography** | Mallorca, Spain (6 segments) |
| **Time Range** | 2024-01-01 → 2026-12-31 (36 months) |
| **Minimum Required** | 12 months (2025-01-01 → 2025-12-31) |
| **Target Frequency** | Daily snapshots |
| **Accommodation Types** | Hotels, apartments, villas, rural houses |
| **Segments** | 6 (see v2_market_map.md) |

### 1.3 Segments

| Code | Segment | Price Range | Peak Season | OTA Dep. |
|------|---------|-------------|-------------|----------|
| `palma_urbano` | Palma Urbano | €80-250 | Jun-Sep | HIGH |
| `playa_costa` | Playa Costa Turística | €100-400 | Jun-Sep | VERY HIGH |
| `magaluf_party` | Magaluf/Palmanova | €40-180 | May-Oct | HIGH |
| `alcudia_family` | Alcudia/Pollensa | €90-300 | Jun-Sep | HIGH |
| `interior_rural` | Interior Rural | €120-500 | Apr-Oct | MEDIUM |
| `luxury_villas` | Luxury Villas | €300-1500 | May-Sep | LOW |

---

## 2. Schema Definition

### 2.1 Core Table: `market_prices`

```sql
CREATE TABLE market_prices (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    snapshot_date DATE NOT NULL,           -- When we collected this
    target_date DATE NOT NULL,             -- When the stay would be
    days_ahead INTEGER NOT NULL,           -- days_ahead = target_date - snapshot_date
    
    -- Segment (NEW in v2.0)
    segment TEXT NOT NULL,                 -- "palma_urbano", "playa_costa", etc.
    
    -- Location
    location TEXT NOT NULL,                -- "Mallorca" (initial)
    sublocation TEXT,                      -- "Palma", "Alcudia", "Sóller", etc.
    latitude REAL,
    longitude REAL,
    
    -- Property
    property_type TEXT NOT NULL,           -- "hotel", "apartment", "villa", "rural_house"
    property_name TEXT,                    -- Listing name (anonymized if needed)
    star_rating INTEGER,                   -- 1-5 stars (hotels), NULL for apartments
    bedrooms INTEGER,                      -- Number of bedrooms
    max_guests INTEGER,                    -- Maximum occupancy
    
    -- Pricing
    price_per_night REAL NOT NULL,        -- Observed price in EUR
    currency TEXT DEFAULT 'EUR',
    original_currency TEXT,                -- If scraped from non-EUR source
    original_price REAL,                   -- Price in original currency
    
    -- Availability
    is_available BOOLEAN DEFAULT 1,       -- 1=available, 0=sold out
    min_nights INTEGER DEFAULT 1,         -- Minimum stay
    max_nights INTEGER,                   -- Maximum stay (NULL=no limit)
    
    -- Source
    source TEXT NOT NULL,                  -- "booking.com", "airbnb", "expedia", "manual"
    listing_id TEXT,                       -- OTA listing ID (anonymized)
    scraping_method TEXT,                  -- "raspal", "api", "manual"
    
    -- Metadata
    collected_at TIMESTAMP NOT NULL,      -- Exact collection timestamp
    data_quality_score REAL DEFAULT 1.0,  -- 0.0-1.0 quality indicator
    
    -- Indexes
    UNIQUE(snapshot_date, target_date, source, listing_id)
);

-- Indexes for query performance
CREATE INDEX idx_market_prices_target ON market_prices(target_date);
CREATE INDEX idx_market_prices_location ON market_prices(location, sublocation);
CREATE INDEX idx_market_prices_source ON market_prices(source);
CREATE INDEX idx_market_prices_snapshot ON market_prices(snapshot_date);
CREATE INDEX idx_market_prices_segment ON market_prices(segment);
```

### 2.2 Derived Table: `market_aggregates`

```sql
CREATE TABLE market_aggregates (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    aggregate_date DATE NOT NULL,          -- Date of aggregation
    target_date DATE NOT NULL,             -- Target stay date
    
    -- Segment
    segment TEXT NOT NULL,                 -- Segment filter
    
    -- Location
    location TEXT NOT NULL,
    sublocation TEXT,
    
    -- Property Filter
    property_type TEXT,                    -- NULL = all types
    star_rating INTEGER,                   -- NULL = all ratings
    
    -- Aggregated Metrics
    avg_price REAL,
    median_price REAL,
    min_price REAL,
    max_price REAL,
    std_price REAL,
    
    -- Counts
    total_listings INTEGER,
    available_listings INTEGER,
    unavailable_listings INTEGER,
    
    -- Market Context
    avg_days_ahead REAL,                   -- Average booking window
    price_percentile_25 REAL,
    price_percentile_75 REAL,
    
    -- Freshness
    data_points_count INTEGER,             -- How many raw observations
    last_updated TIMESTAMP,
    
    UNIQUE(aggregate_date, target_date, segment, location, sublocation, property_type, star_rating)
);
```

---

## 3. Segment-Aware Data Collection

### 3.1 Sources by Segment

| Segment | Source | Target Listings | Priority |
|---------|--------|-----------------|----------|
| `playa_costa` | Booking.com | 150 | 1 |
| `playa_costa` | Airbnb | 50 | 1 |
| `alcudia_family` | Booking.com | 150 | 2 |
| `alcudia_family` | Airbnb | 50 | 2 |
| `palma_urbano` | Booking.com | 150 | 3 |
| `palma_urbano` | Airbnb | 50 | 3 |
| `magaluf_party` | Booking.com | 100 | 4 |
| `magaluf_party` | Airbnb | 50 | 4 |
| `interior_rural` | Booking.com | 80 | 5 |
| `interior_rural` | Airbnb | 20 | 5 |
| `luxury_villas` | Booking.com | 50 | 6 |
| `luxury_villas` | Airbnb | 50 | 6 |
| **TOTAL** | | **950** | |

### 3.2 Geographic Coordinates by Segment

| Segment | Center Lat | Center Lng | Radius (km) |
|---------|------------|------------|-------------|
| `palma_urbano` | 39.5696 | 2.6502 | 5 |
| `playa_costa` | 39.5000 | 2.8000 | 15 |
| `magaluf_party` | 39.5089 | 2.4447 | 5 |
| `alcudia_family` | 39.8266 | 3.1215 | 10 |
| `interior_rural` | 39.7000 | 2.9000 | 20 |
| `luxury_villas` | 39.5500 | 2.4500 | 15 |

### 3.3 Search Queries by Segment

| Segment | Booking.com Query | Airbnb Query |
|---------|-------------------|--------------|
| `palma_urbano` | "Palma de Mallorca hotels" | "Palma apartments" |
| `playa_costa` | "Playa de Palma hotels" | "Playa de Palma apartments" |
| `magaluf_party` | "Magaluf hotels" | "Magaluf apartments" |
| `alcudia_family` | "Alcudia hotels" | "Alcudia apartments" |
| `interior_rural` | "Mallorca rural hotels" | "Mallorca fincas" |
| `luxury_villas` | "Mallorca luxury hotels" | "Mallorca luxury villas" |

---

## 4. Data Quality Rules

### 4.1 Validation Rules

| Rule | Description | Action |
|------|-------------|--------|
| **Price Range** | 10 ≤ price ≤ 1500 EUR | Reject if outside |
| **Date Validity** | target_date > snapshot_date | Reject |
| **Days Ahead** | 0 ≤ days_ahead ≤ 365 | Reject |
| **Location** | Must be in Mallorca | Reject |
| **Segment** | Must be in VALID_SEGMENTS | Reject |
| **Currency** | Convert to EUR | Store original + EUR |
| **Duplicates** | Same source + listing + dates | Keep latest |

### 4.2 Quality Score Calculation

```python
def calculate_quality_score(row):
    score = 1.0
    
    # Penalize missing fields
    if not row['sublocation']:
        score -= 0.1
    if not row['star_rating'] and row['property_type'] == 'hotel':
        score -= 0.1
    if not row['bedrooms']:
        score -= 0.05
    
    # Penalize stale data
    days_old = (now - row['collected_at']).days
    if days_old > 7:
        score -= 0.2
    if days_old > 30:
        score -= 0.5
    
    # Penalize extreme prices (per segment)
    segment_ranges = {
        'palma_urbano': (30, 500),
        'playa_costa': (30, 800),
        'magaluf_party': (15, 400),
        'alcudia_family': (30, 600),
        'interior_rural': (40, 1000),
        'luxury_villas': (100, 3000),
    }
    low, high = segment_ranges.get(row['segment'], (10, 1000))
    if row['price_per_night'] < low or row['price_per_night'] > high:
        score -= 0.1
    
    return max(0.0, score)
```

---

## 5. Pipeline Architecture

### 5.1 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    V2 DATA PIPELINE (SEGMENT-AWARE)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   OTA APIs  │───▶│   RASPAL    │───▶│   Raw Data  │    │
│  │  (Booking,  │    │   Scraper   │    │   (CSV/DB)  │    │
│  │  Airbnb,    │    │             │    │             │    │
│  │  Expedia)   │    └─────────────┘    └─────────────┘    │
│  └─────────────┘           │                   │           │
│                            ▼                   ▼           │
│                    ┌─────────────┐    ┌─────────────┐    │
│                    │  Segment    │───▶│  Validation │    │
│                    │  Router     │    │  & Cleaning │    │
│                    └─────────────┘    └─────────────┘    │
│                                            │               │
│                                            ▼               │
│                                    ┌─────────────┐    │
│                                    │  market_    │    │
│                                    │  prices     │    │
│                                    └─────────────┘    │
│                                            │               │
│                                            ▼               │
│                                    ┌─────────────┐    │
│                                    │  Aggregation │    │
│                                    │  Engine      │    │
│                                    └─────────────┘    │
│                                            │               │
│                                            ▼               │
│                                    ┌─────────────┐    │
│                                    │  market_    │    │
│                                    │  aggregates │    │
│                                    └─────────────┘    │
│                                            │               │
│                                            ▼               │
│                                    ┌─────────────┐    │
│                                    │  V2 Model   │    │
│                                    │  Training   │    │
│                                    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Ingestion Schedule

| Task | Frequency | Time | Description |
|------|-----------|------|-------------|
| **Scrape Booking.com** | Daily | 02:00 UTC | Collect prices for next 365 days, segment-aware |
| **Scrape Airbnb** | Daily | 03:00 UTC | Collect prices for next 365 days, segment-aware |
| **Scrape Expedia** | Daily | 04:00 UTC | Collect prices for next 365 days, segment-aware |
| **Aggregate Data** | Daily | 05:00 UTC | Update market_aggregates per segment |
| **Quality Check** | Daily | 06:00 UTC | Flag anomalies, update scores |
| **Model Retrain** | Weekly | Sunday 07:00 UTC | Retrain on latest data |

---

## 6. File Structure

```
Optimus_Price_Final/
├── data/
│   ├── v2_market/
│   │   ├── raw/                          # Raw scraped data
│   │   │   ├── booking/
│   │   │   ├── airbnb/
│   │   │   └── expedia/
│   │   ├── processed/                    # Cleaned & validated
│   │   │   └── market_prices.db          # SQLite database
│   │   └── aggregates/                   # Pre-computed aggregates
│   │       └── market_aggregates.db
│   └── v1_historical/                    # V1 Kaggle data (frozen)
│       └── hotel_reservations_real.csv
├── src/
│   ├── v2_pipeline/
│   │   ├── __init__.py
│   │   ├── scraper.py                    # RASPAL integration
│   │   ├── validator.py                  # Data quality checks
│   │   ├── aggregator.py                 # Market aggregates
│   │   ├── ingester.py                   # DB ingestion
│   │   └── backfill.py                   # Historical backfill
│   └── optimus_price/                    # Shared ML core
│       ├── training.py
│       ├── evaluation.py
│       └── prediction_service.py
├── configs/
│   └── v2_scraping.yaml                  # Scraping configuration
└── scripts/
    └── v2_daily_scrape.py                # Daily scraping job
```

---

## 7. Configuration

### 7.1 Scraping Config (`configs/v2_scraping.yaml`)

```yaml
# V2 Scraping Configuration (Segment-Aware)
version: "2.0"

location:
  name: "Mallorca"
  bounding_box:
    north: 39.95
    south: 39.15
    east: 3.45
    west: 2.30

segments:
  palma_urbano:
    name: "Palma Urbano"
    center: { lat: 39.5696, lng: 2.6502 }
    radius_km: 5
    price_range: [30, 500]
    peak_months: [6, 7, 8, 9]
    booking_queries:
      booking: "Palma de Mallorca hotels"
      airbnb: "Palma apartments"
  
  playa_costa:
    name: "Playa Costa Turística"
    center: { lat: 39.5000, lng: 2.8000 }
    radius_km: 15
    price_range: [30, 800]
    peak_months: [6, 7, 8, 9]
    booking_queries:
      booking: "Playa de Palma hotels"
      airbnb: "Playa de Palma apartments"
  
  magaluf_party:
    name: "Magaluf/Palmanova"
    center: { lat: 39.5089, lng: 2.4447 }
    radius_km: 5
    price_range: [15, 400]
    peak_months: [5, 6, 7, 8, 9, 10]
    booking_queries:
      booking: "Magaluf hotels"
      airbnb: "Magaluf apartments"
  
  alcudia_family:
    name: "Alcudia/Pollensa"
    center: { lat: 39.8266, lng: 3.1215 }
    radius_km: 10
    price_range: [30, 600]
    peak_months: [6, 7, 8, 9]
    booking_queries:
      booking: "Alcudia hotels"
      airbnb: "Alcudia apartments"
  
  interior_rural:
    name: "Interior Rural"
    center: { lat: 39.7000, lng: 2.9000 }
    radius_km: 20
    price_range: [40, 1000]
    peak_months: [4, 5, 6, 7, 8, 9, 10]
    booking_queries:
      booking: "Mallorca rural hotels"
      airbnb: "Mallorca fincas"
  
  luxury_villas:
    name: "Luxury Villas"
    center: { lat: 39.5500, lng: 2.4500 }
    radius_km: 15
    price_range: [100, 3000]
    peak_months: [5, 6, 7, 8, 9]
    booking_queries:
      booking: "Mallorca luxury hotels"
      airbnb: "Mallorca luxury villas"

sources:
  booking:
    enabled: true
    base_url: "https://www.booking.com"
    max_listings_per_segment: 150
    scrape_interval: "daily"
    delay_between_requests: 2.0
    max_retries: 3
    retry_delay: 30
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    rate_limit:
      requests_per_minute: 10
      requests_per_hour: 100
    rotation:
      enabled: true
      user_agents_file: "configs/user_agents.txt"
    
  airbnb:
    enabled: true
    base_url: "https://www.airbnb.com"
    max_listings_per_segment: 50
    scrape_interval: "daily"
    delay_between_requests: 3.0
    max_retries: 3
    retry_delay: 60
    rate_limit:
      requests_per_minute: 6
      requests_per_hour: 60
    rotation:
      enabled: true
      user_agents_file: "configs/user_agents.txt"
    
  expedia:
    enabled: false
    base_url: "https://www.expedia.com"
    max_listings_per_segment: 50
    scrape_interval: "daily"
    delay_between_requests: 4.0

target_dates:
  lookahead_days: 365
  date_range: "2025-07-01 to 2026-12-31"

quality:
  min_price: 10
  max_price: 3000
  min_quality_score: 0.5
  segment_price_ranges:
    palma_urbano: [30, 500]
    playa_costa: [30, 800]
    magaluf_party: [15, 400]
    alcudia_family: [30, 600]
    interior_rural: [40, 1000]
    luxury_villas: [100, 3000]

database:
  path: "data/v2_market/processed/market_prices.db"
```

---

## 8. Queries for V2 Model

### 8.1 Training Data Query (Segment-Aware)

```sql
-- Get training data for V2 model per segment
SELECT 
    snapshot_date,
    target_date,
    days_ahead,
    segment,
    sublocation,
    property_type,
    star_rating,
    bedrooms,
    max_guests,
    price_per_night,
    is_available,
    source,
    data_quality_score
FROM market_prices
WHERE 
    snapshot_date >= '2024-01-01'
    AND data_quality_score >= 0.7
    AND is_available = 1
ORDER BY snapshot_date, target_date;
```

### 8.2 Market Context Query (Segment-Aware)

```sql
-- Get market context for a specific date, location and segment
SELECT 
    AVG(price_per_night) as avg_price,
    MIN(price_per_night) as min_price,
    MAX(price_per_night) as max_price,
    COUNT(*) as total_listings,
    COUNT(CASE WHEN property_type = 'hotel' THEN 1 END) as hotels,
    COUNT(CASE WHEN property_type = 'apartment' THEN 1 END) as apartments
FROM market_prices
WHERE 
    target_date = :target_date
    AND segment = :segment
    AND sublocation = :sublocation
    AND is_available = 1
    AND snapshot_date >= date('now', '-7 days');
```

### 8.3 Segment Statistics Query

```sql
-- Get statistics per segment
SELECT 
    segment,
    COUNT(*) as total_records,
    COUNT(DISTINCT listing_id) as unique_listings,
    AVG(price_per_night) as avg_price,
    MIN(target_date) as earliest_date,
    MAX(target_date) as latest_date
FROM market_prices
GROUP BY segment
ORDER BY total_records DESC;
```

---

## 9. Backfill Strategy

### 9.1 Historical Data Sources

| Source | Coverage | Method |
|--------|----------|--------|
| **Booking.com** | 2024-01 → 2025-06 | RASPAL backfill |
| **Airbnb** | 2024-01 → 2025-06 | RASPAL backfill |
| **Kaggle** | 2015-2017 | Frozen (V1 only) |

### 9.2 Backfill Execution

```python
# Backfill command (segment-aware)
python -m src.v2_pipeline.backfill \
    --start-date 2024-01-01 \
    --end-date 2025-06-28 \
    --source booking \
    --segment playa_costa
```

---

## 10. Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Data Points** | > 100,000 | 1 (test) |
| **Date Coverage** | > 12 months | 0 |
| **Source Diversity** | > 2 OTAs | 0 |
| **Quality Score Avg** | > 0.8 | N/A |
| **Geographic Coverage** | > 5 sublocations | 0 |
| **Segment Coverage** | > 4 segments | 0 |
| **Listings per Segment** | > 100 | 0 |

---

## 11. Readiness Checklist

### Pre-Scraping Requirements

- [ ] Market map defined (v2_market_map.md)
- [ ] Data contract finalized (this document)
- [ ] Pipeline validated against schema
- [ ] Rate limits configured
- [ ] Retry policy configured
- [ ] User agent rotation configured
- [ ] Segment-aware scraping queries defined
- [ ] Geographic coordinates verified
- [ ] Price ranges validated per segment
- [ ] Database schema supports segments

### Post-Scraping Validation

- [ ] Minimum 100 records per segment
- [ ] Minimum 30 days coverage
- [ ] All segments represented
- [ ] Quality score average > 0.8
- [ ] No schema violations
- [ ] Duplicates handled correctly

---

*This document defines the V2 data specification. Segment-aware data collection is the first priority.*
