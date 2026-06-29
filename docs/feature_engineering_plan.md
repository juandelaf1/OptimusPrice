# Feature Engineering Plan

**Generated**: June 2026
**Status**: Design phase — no implementation yet
**Target**: Increase R2 from 0.3470 to 0.45+

---

## Executive Summary

This plan defines 49 candidate features across 7 groups. Implementation will be incremental, with validation after each group.

| Group | Features | Priority | Expected R2 Gain |
|-------|----------|----------|------------------|
| Temporal | 9 | HIGH | +0.02-0.03 |
| Booking Behavior | 9 | HIGH | +0.02-0.03 |
| Demand Indicators | 7 | HIGH | +0.03-0.05 |
| Interactions | 5 | MEDIUM | +0.01-0.02 |
| Historical Aggregates | 9 | MEDIUM | +0.05-0.10 |
| Competitor | 5 | LOW | +0.05-0.10 (if data) |
| Weather & Events | 5 | LOW | +0.02-0.05 (if data) |

---

## Implementation Phases

### Phase 1: Temporal Features (Week 1)

**Goal**: Capture seasonal patterns

| Feature | Formula | Complexity |
|---------|---------|------------|
| season | month_to_season(arrival_month) | LOW |
| quarter | (arrival_month - 1) // 3 + 1 | LOW |
| month_sin | sin(2 * pi * arrival_month / 12) | LOW |
| month_cos | cos(2 * pi * arrival_month / 12) | LOW |
| day_sin | sin(2 * pi * arrival_day_of_week / 7) | LOW |
| day_cos | cos(2 * pi * arrival_day_of_week / 7) | LOW |
| is_weekend | 1 if day in [5,6] else 0 | LOW |
| is_month_start | 1 if date <= 7 else 0 | LOW |
| is_month_end | 1 if date >= 25 else 0 | LOW |

**Dependencies**: None
**Validation**: R2 improvement >= 0.01
**Risk**: LOW

### Phase 2: Booking Behavior Features (Week 1)

**Goal**: Capture booking patterns

| Feature | Formula | Complexity |
|---------|---------|------------|
| lead_time_bin | pd.cut(lead_time, 5 bins) | LOW |
| advance_booking | 1 if lead_time > 30 else 0 | LOW |
| stay_length_category | pd.cut(total_nights, 5 bins) | LOW |
| is_short_stay | 1 if total_nights <= 1 else 0 | LOW |
| is_long_stay | 1 if total_nights >= 7 else 0 | LOW |
| has_children | 1 if children > 0 else 0 | LOW |
| has_babies | 1 if babies > 0 else 0 | LOW |
| cancellation_history | 1 if prev_cancellations > 0 else 0 | LOW |
| loyalty_score | is_repeated + (prev_bookings > 0) | LOW |

**Dependencies**: None
**Validation**: R2 improvement >= 0.01
**Risk**: LOW

### Phase 3: Demand Indicators (Week 2)

**Goal**: Capture demand signals

| Feature | Formula | Complexity |
|---------|---------|------------|
| weekend_ratio | weekend_nights / (total_nights + 1) | LOW |
| guest_density | total_guests / (total_nights + 1) | LOW |
| booking_intensity | booking_changes / (lead_time + 1) | LOW |
| special_request_rate | special_requests / (total_nights + 1) | LOW |
| parking_rate | parking_spaces / (total_guests + 1) | LOW |
| wait_ratio | waiting_list / (lead_time + 1) | LOW |
| cancellation_ratio | prev_cancellations / (prev_not_canceled + 1) | LOW |

**Dependencies**: None
**Validation**: R2 improvement >= 0.02
**Risk**: LOW

### Phase 4: Interaction Features (Week 2)

**Goal**: Capture feature interactions

| Feature | Formula | Complexity |
|---------|---------|------------|
| room_market | room_type * market_segment | LOW |
| room_customer | room_type * customer_type | LOW |
| lead_time_market | lead_time * market_segment | LOW |
| guests_total_nights | total_guests * total_nights | LOW |
| month_room | arrival_month * room_type | LOW |

**Dependencies**: None
**Validation**: R2 improvement >= 0.01
**Risk**: LOW

### Phase 5: Historical Aggregates (Week 3)

**Goal**: Capture temporal trends

| Feature | Formula | Complexity |
|---------|---------|------------|
| rolling_occupancy_7d | mean(booking_status) over 7d | MEDIUM |
| rolling_occupancy_30d | mean(booking_status) over 30d | MEDIUM |
| rolling_adr_7d | mean(price) over 7d | MEDIUM |
| rolling_adr_30d | mean(price) over 30d | MEDIUM |
| rolling_booking_pace_7d | count(bookings) over 7d | MEDIUM |
| rolling_booking_pace_30d | count(bookings) over 30d | MEDIUM |
| lag_price_7d | price lagged 7d | MEDIUM |
| lag_price_30d | price lagged 30d | MEDIUM |
| lag_price_90d | price lagged 90d | MEDIUM |

**Dependencies**: Temporal sort, groupby operations
**Validation**: R2 improvement >= 0.03
**Risk**: MEDIUM (data leakage risk if not careful)

### Phase 6: Competitor Variables (Week 4, Placeholder)

**Goal**: Market intelligence

| Feature | Formula | Complexity |
|---------|---------|------------|
| competitor_avg_price | Mean competitor price | HIGH |
| competitor_min_price | Min competitor price | HIGH |
| competitor_max_price | Max competitor price | HIGH |
| price_vs_competitor | (own - avg) / avg | HIGH |
| competitor_count | Number of competitors | HIGH |

**Dependencies**: External data source
**Validation**: N/A (placeholder only)
**Risk**: HIGH (data availability)

### Phase 7: Weather & Events (Week 4, Placeholder)

**Goal**: External context

| Feature | Formula | Complexity |
|---------|---------|------------|
| temperature | Average temperature | HIGH |
| precipitation | Rain/snow indicator | HIGH |
| is_holiday | Holiday calendar flag | HIGH |
| is_event | Local event flag | HIGH |
| event_type | Type of event | HIGH |

**Dependencies**: External data source
**Validation**: N/A (placeholder only)
**Risk**: HIGH (data availability)

---

## Validation Strategy

### After Each Phase

1. Train ElasticNet with new features
2. Compare R2, RMSE, MAE, MAPE
3. Check for data leakage
4. Check for multicollinearity (VIF)
5. Document results

### Success Criteria

| Metric | Current | Target | Minimum |
|--------|---------|--------|---------|
| R2 | 0.3470 | 0.50 | 0.40 |
| RMSE | 31.78 | 25.00 | 28.00 |
| MAE | 24.37 | 18.00 | 21.00 |
| MAPE | 23.78% | 18.00% | 20.00% |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Data leakage | Temporal split, no future info |
| Multicollinearity | VIF check after each phase |
| Overfitting | Cross-validation, feature importance |
| Feature explosion | Select top features only |
| Computational cost | Incremental implementation |

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Current dataset | Available | Required |
| External weather data | Not available | Phase 7 blocked |
| Competitor data | Not available | Phase 6 blocked |
| Holiday calendar | Available (derivable) | Phase 1 OK |

---

*Generated by Sprint 4 feature engineering design*
