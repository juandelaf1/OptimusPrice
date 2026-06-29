# Feature Catalog

**Generated**: June 2026
**Dataset**: hotel_reservations_real.csv (117,429 rows)
**Status**: Design phase — no implementation yet

---

## Current Features (27)

### Temporal (5)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| arrival_year | int | 2015-2017 | Dataset |
| arrival_month | int | 1-12 | Dataset |
| arrival_date | int | 1-31 | Dataset |
| arrival_week_number | int | 1-53 | Dataset |
| arrival_day_of_week | int | 0-6 | Dataset |

### Stay (3)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| stays_in_weekend_nights | int | 0-15 | Dataset |
| stays_in_week_nights | int | 0-31 | Dataset |
| total_nights | int | 0-39 | Derived (sum) |

### Guest (4)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| total_guests | float | 1-7 | Derived (sum) |
| adults | int | 0-4 | Dataset |
| children | float | 0-3 | Dataset |
| babies | int | 0-2 | Dataset |

### Booking Behavior (6)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| lead_time | int | 0-737 | Dataset |
| is_repeated_guest | int | 0-1 | Dataset |
| previous_cancellations | int | 0-14 | Dataset |
| previous_bookings_not_canceled | int | 0-72 | Dataset |
| booking_changes | int | 0-18 | Dataset |
| days_in_waiting_list | int | 0-126 | Dataset |

### Service (2)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| required_car_parking_spaces | int | 0-4 | Dataset |
| total_of_special_requests | int | 0-5 | Dataset |

### Categorical (Encoded) (6)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| room_type_value | int | 0-8 | Encoded |
| meal_plan_value | int | 0-3 | Encoded |
| market_segment_value | float | 0-6 | Encoded |
| distribution_channel_value | int | 0-4 | Encoded |
| customer_type_value | int | 0-3 | Encoded |
| deposit_type_value | int | 0-2 | Encoded |

### Target & Status (2)

| Feature | Type | Values | Source |
|---------|------|--------|--------|
| avg_price_per_room | float | 0.26-510.00 | Target |
| booking_status_Not_Canceled | int | 0-1 | Dataset |

---

## Missing Business Variables

### High Impact (Expected R2 improvement > 0.03)

| Variable | Reason Missing | Expected Impact |
|----------|---------------|-----------------|
| Location/region | Not in dataset | HIGH |
| Hotel star rating | Not in dataset | HIGH |
| Hotel brand | Not in dataset | HIGH |
| Competitor prices | OTAs block scraping | HIGH |
| Local events | Not available | MEDIUM-HIGH |
| Weather | Not available | MEDIUM-HIGH |

### Medium Impact (Expected R2 improvement 0.01-0.03)

| Variable | Reason Missing | Expected Impact |
|----------|---------------|-----------------|
| Season | Can derive from month | MEDIUM |
| Holiday flags | Can derive from date | MEDIUM |
| Booking channel | Encoded but not enriched | MEDIUM |
| Room type details | Encoded but not enriched | LOW-MEDIUM |

### Low Impact (Expected R2 improvement < 0.01)

| Variable | Reason Missing | Expected Impact |
|----------|---------------|-----------------|
| Payment method | Not available | LOW |
| Loyalty tier | Not available | LOW |
| Corporate contract | Not available | LOW |

---

## Feature Groups for Engineering

### Group 1: Temporal Features

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| season | month_to_season(arrival_month) | categorical | 0-3 |
| quarter | (arrival_month - 1) // 3 + 1 | int | 1-4 |
| month_sin | sin(2 * pi * arrival_month / 12) | float | -1 to 1 |
| month_cos | cos(2 * pi * arrival_month / 12) | float | -1 to 1 |
| day_sin | sin(2 * pi * arrival_day_of_week / 7) | float | -1 to 1 |
| day_cos | cos(2 * pi * arrival_day_of_week / 7) | float | -1 to 1 |
| is_weekend | 1 if arrival_day_of_week in [5,6] else 0 | binary | 0-1 |
| is_month_start | 1 if arrival_date <= 7 else 0 | binary | 0-1 |
| is_month_end | 1 if arrival_date >= 25 else 0 | binary | 0-1 |

### Group 2: Booking Behavior Features

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| lead_time_bin | pd.cut(lead_time, bins=[0,7,30,90,180,737]) | categorical | 0-4 |
| advance_booking | 1 if lead_time > 30 else 0 | binary | 0-1 |
| stay_length_category | pd.cut(total_nights, bins=[0,1,3,7,14,39]) | categorical | 0-4 |
| is_short_stay | 1 if total_nights <= 1 else 0 | binary | 0-1 |
| is_long_stay | 1 if total_nights >= 7 else 0 | binary | 0-1 |
| has_children | 1 if children > 0 else 0 | binary | 0-1 |
| has_babies | 1 if babies > 0 else 0 | binary | 0-1 |
| cancellation_history | 1 if previous_cancellations > 0 else 0 | binary | 0-1 |
| loyalty_score | is_repeated_guest + (previous_bookings_not_canceled > 0) | int | 0-2 |

### Group 3: Demand Indicators

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| weekend_ratio | stays_in_weekend_nights / (total_nights + 1) | float | 0-1 |
| guest_density | total_guests / (total_nights + 1) | float | 0-7 |
| booking_intensity | booking_changes / (lead_time + 1) | float | 0-18 |
| special_request_rate | total_of_special_requests / (total_nights + 1) | float | 0-5 |
| parking_rate | required_car_parking_spaces / (total_guests + 1) | float | 0-4 |
| wait_ratio | days_in_waiting_list / (lead_time + 1) | float | 0-126 |
| cancellation_ratio | previous_cancellations / (previous_bookings_not_canceled + 1) | float | 0-15 |

### Group 4: Interaction Features

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| room_market | room_type_value * market_segment_value | int | 0-48 |
| room_customer | room_type_value * customer_type_value | int | 0-24 |
| lead_time_market | lead_time * market_segment_value | float | 0-4422 |
| guests_total_nights | total_guests * total_nights | float | 0-273 |
| month_room | arrival_month * room_type_value | int | 0-96 |

### Group 5: Historical Aggregates (Requires temporal grouping)

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| rolling_occupancy_7d | mean(booking_status) over 7-day window | float | 0-1 |
| rolling_occupancy_30d | mean(booking_status) over 30-day window | float | 0-1 |
| rolling_adr_7d | mean(avg_price_per_room) over 7-day window | float | 0-510 |
| rolling_adr_30d | mean(avg_price_per_room) over 30-day window | float | 0-510 |
| rolling_booking_pace_7d | count(bookings) over 7-day window | int | 0-N |
| rolling_booking_pace_30d | count(bookings) over 30-day window | int | 0-N |
| lag_price_7d | avg_price_per_room lagged 7 days | float | 0-510 |
| lag_price_30d | avg_price_per_room lagged 30 days | float | 0-510 |
| lag_price_90d | avg_price_per_room lagged 90 days | float | 0-510 |

### Group 6: Competitor Variables (Placeholder)

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| competitor_avg_price | Mean competitor price | float | Missing allowed |
| competitor_min_price | Min competitor price | float | Missing allowed |
| competitor_max_price | Max competitor price | float | Missing allowed |
| price_vs_competitor | (own_price - competitor_avg) / competitor_avg | float | Missing allowed |
| competitor_count | Number of competitors | int | Missing allowed |

### Group 7: Weather & Events (Placeholder)

| Feature | Formula | Type | Values |
|---------|---------|------|--------|
| temperature | Average temperature | float | Missing allowed |
| precipitation | Rain/snow indicator | binary | Missing allowed |
| is_holiday | Holiday calendar flag | binary | 0-1 |
| is_event | Local event flag | binary | 0-1 |
| event_type | Type of event | categorical | Missing allowed |

---

## Summary

| Group | Features | Complexity | Expected Impact |
|-------|----------|------------|-----------------|
| Temporal | 9 | Low | Medium |
| Booking Behavior | 9 | Low | Medium |
| Demand Indicators | 7 | Medium | Medium-High |
| Interactions | 5 | Low | Low-Medium |
| Historical Aggregates | 9 | High | High |
| Competitor | 5 | High | High (if data available) |
| Weather & Events | 5 | High | Medium-High |
| **Total** | **49** | | |

---

*Generated by Sprint 4 feature analysis*
