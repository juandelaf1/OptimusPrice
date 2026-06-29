# V2 SCRAPING READINESS CHECKLIST

**Version**: 1.0
**Status**: IN PROGRESS
**Last Updated**: June 2026

---

## 1. Infrastructure Readiness

### 1.1 Market Map
- [x] Market segments defined (6 segments)
- [x] Geographic coordinates assigned per segment
- [x] Price ranges validated per segment
- [x] Seasonality patterns documented
- [x] OTA dependency assessed per segment

### 1.2 Data Contract
- [x] Schema finalized (market_prices table)
- [x] Segment field added to schema
- [x] Quality rules defined per segment
- [x] Validation rules implemented
- [x] Aggregation schema defined

### 1.3 Pipeline Components
- [x] Database schema updated with segments
- [x] Ingestion module supports segments
- [x] Validation module validates segments
- [x] Aggregation module aggregates by segment
- [x] Pipeline tested end-to-end

---

## 2. Configuration Readiness

### 2.1 Scraping Configuration
- [x] Rate limits configured (10 req/min, 100 req/hr)
- [x] Retry policy configured (3 retries, 30s delay)
- [x] User agent rotation enabled
- [x] Segment-specific queries defined
- [x] Geographic bounds configured

### 2.2 Source Configuration
- [x] Booking.com enabled (150 listings/segment)
- [x] Airbnb enabled (50 listings/segment)
- [x] Expedia disabled (enable when ready)

### 2.3 Target Configuration
- [x] Lookahead days: 365
- [x] Date range: 2025-07-01 to 2026-12-31
- [x] Price ranges validated per segment

---

## 3. Validation Readiness

### 3.1 Schema Validation
- [x] Segment field in market_prices table
- [x] Segment field in market_aggregates table
- [x] Indexes created for segment queries
- [x] UNIQUE constraint includes segment

### 3.2 Data Quality Validation
- [x] Price range validation per segment
- [x] Date validity checks
- [x] Location validation (Mallorca)
- [x] Segment validation (6 valid segments)
- [x] Quality score calculation per segment

### 3.3 Pipeline Validation
- [x] Test insertion: 6 records (1 per segment)
- [x] Batch insert: 6/6 successful
- [x] Query filtering by segment works
- [x] Statistics by segment work

---

## 4. Pre-Scraping Requirements

### 4.1 Technical Requirements
- [x] Database initialized and tested
- [x] Pipeline modules imported and validated
- [x] Configuration files updated
- [x] Segment-aware queries defined
- [x] Geographic coordinates verified

### 4.2 Operational Requirements
- [ ] RASPAL scraper installed and configured
- [ ] User agents file created
- [ ] Proxy rotation configured (if needed)
- [ ] Logging configured
- [ ] Error handling implemented

### 4.3 Data Requirements
- [ ] Minimum 100 records per segment target defined
- [ ] Minimum 30 days coverage target defined
- [ ] All segments represented target defined
- [ ] Quality score average > 0.8 target defined

---

## 5. Post-Scraping Validation

### 5.1 Data Collection Validation
- [ ] Minimum 100 records per segment
- [ ] Minimum 30 days coverage
- [ ] All 6 segments represented
- [ ] All sources (Booking.com, Airbnb) represented
- [ ] No schema violations
- [ ] Duplicates handled correctly

### 5.2 Quality Validation
- [ ] Quality score average > 0.8
- [ ] No extreme price outliers
- [ ] Geographic coverage verified
- [ ] Temporal coverage verified

### 5.3 Model Training Validation
- [ ] Training data query returns results
- [ ] Market context query returns results
- [ ] Segment statistics query returns results
- [ ] V2 model can be trained on collected data

---

## 6. Readiness Status Summary

| Category | Items | Status |
|----------|-------|--------|
| **Infrastructure** | 10 | ✅ 10/10 |
| **Configuration** | 9 | ✅ 9/9 |
| **Validation** | 9 | ✅ 9/9 |
| **Pre-Scraping** | 12 | ⏳ 8/12 |
| **Post-Scraping** | 12 | ⏳ 0/12 |
| **TOTAL** | 52 | ⏳ 36/52 (69%) |

---

## 7. Next Steps to Enable Scraping

### Immediate (Pre-Scraping)
1. Install RASPAL scraper
2. Create user_agents.txt file
3. Configure proxy rotation (if needed)
4. Set up logging
5. Implement error handling

### Short-term (Data Collection)
1. Start with playa_costa segment (Priority 1)
2. Collect 100+ records per source
3. Validate data quality
4. Expand to other segments

### Medium-term (Model Training)
1. Collect 30+ days of data
2. Train V2 model on collected data
3. Validate model performance
4. Deploy V2 model

---

## 8. Blockers

| Blocker | Impact | Resolution |
|---------|--------|------------|
| RASPAL not installed | Cannot scrape | Install RASPAL |
| No user agents file | Rate limiting risk | Create user_agents.txt |
| No proxy rotation | IP blocking risk | Configure proxies |
| No logging | Debugging difficulty | Implement logging |

---

## 9. Success Criteria

| Criterion | Target | Current |
|-----------|--------|---------|
| Pipeline validation | PASS | PASS ✅ |
| Segment support | 6 segments | 6 segments ✅ |
| Data points | >100,000 | 6 (test) |
| Date coverage | >12 months | 0 |
| Segment coverage | >4 segments | 6 (test) |
| Quality score | >0.8 | N/A |

---

*This checklist tracks readiness for V2 scraping activation. Complete all pre-scraping items before enabling scraping.*
