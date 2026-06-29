# Leakage Assessment — Sprint 6

**Generated**: June 2026
**Sprint**: 6
**Status**: VALIDATED

---

## Executive Summary

Sprint 6 was validated using the identical validation strategy as Sprint 3. **No target leakage** was found in the SAFE engineered features. The previous R2=0.5884 claim was inflated because it included features derived from the target variable.

---

## Validation Strategy (Identical to Sprint 3)

| Strategy | Sprint 3 | Sprint 6 | Match |
|----------|----------|----------|-------|
| Temporal Split | 80/20 chronological | 80/20 chronological | IDENTICAL |
| TSCV | 3-fold expanding | 3-fold expanding | IDENTICAL |
| Rolling Window | 3 windows, 60% train | 3 windows, 60% train | IDENTICAL |
| Train Size | 93,943 | 93,943 | IDENTICAL |
| Test Size | 23,486 | 23,486 | IDENTICAL |

---

## Feature Analysis

### Baseline (27 features)
All original features. No engineered features.

### Engineered (44 features = 27 baseline + 17 new)
All 17 new features are **SAFE** — they do NOT use the target variable.

| Feature | Source | Target-Derived | Available at Prediction |
|---------|--------|----------------|------------------------|
| month_sin | arrival_month | NO | YES |
| month_cos | arrival_month | NO | YES |
| week_sin | arrival_week_number | NO | YES |
| week_cos | arrival_week_number | NO | YES |
| quarter | arrival_month | NO | YES |
| season | arrival_month | NO | YES |
| is_high_season | arrival_month | NO | YES |
| is_weekend_arrival | arrival_day_of_week | NO | YES |
| days_until_peak | arrival_month | NO | YES |
| lead_time_bin | lead_time | NO | YES |
| short_stay | stays_in_weekend_nights, stays_in_week_nights | NO | YES |
| medium_stay | stays_in_weekend_nights, stays_in_week_nights | NO | YES |
| long_stay | stays_in_weekend_nights, stays_in_week_nights | NO | YES |
| stay_bucket | stays_in_weekend_nights, stays_in_week_nights | NO | YES |
| booking_window | lead_time | NO | YES |
| guest_density | adults, children, babies | NO | YES |
| room_intensity | adults, children, room_type_value | NO | YES |

### Features from build_temporal_aggregate_features (EXCLUDED)
These features use `avg_price_per_room` (the target) and were NOT included:

| Feature | Why Excluded |
|---------|--------------|
| lag_7 | Uses target directly |
| lag_30 | Uses target directly |
| lag_90 | Uses target directly |
| rolling_mean_7 | Uses target directly |
| rolling_mean_30 | Uses target directly |
| rolling_mean_90 | Uses target directly |
| adr_trend | Uses target directly |
| pickup | Uses target directly |
| booking_velocity | Uses cumsum/index (prediction-time unavailable) |
| occupancy_trend | Uses booking_status (safe, but included for consistency) |

---

## Metrics Comparison

| Metric | Baseline (27f) | Engineered (44f) | Delta |
|--------|----------------|------------------|-------|
| **Holdout R2** | 0.346712 | 0.348327 | +0.001615 |
| **Holdout RMSE** | 31.7871 | 31.7478 | -0.0393 |
| **Holdout MAE** | 24.3928 | 24.2528 | -0.1400 |
| **Holdout MAPE** | 23.8336% | 23.4138% | -0.4198% |
| **CV R2** | 0.2158 | 0.1985 | -0.0173 |
| **CV R2 std** | 0.0647 | 0.1258 | +0.0611 |
| **Rolling R2** | 0.2650 | 0.2173 | -0.0477 |
| **Rolling R2 std** | 0.0574 | 0.1314 | +0.0740 |

---

## Feature Importance Ranking

| Rank | Feature | Coefficient | Engineered |
|------|---------|-------------|------------|
| 1 | room_type_value | +11.146694 | NO |
| 2 | month_sin | -9.588131 | YES |
| 3 | arrival_year | +8.646966 | NO |
| 4 | lead_time | -8.474837 | NO |
| 5 | week_cos | -8.138016 | YES |
| 6 | children | +7.453694 | NO |
| 7 | total_guests | +6.811874 | NO |
| 8 | week_sin | -6.275001 | YES |
| 9 | market_segment_value | -5.575253 | NO |
| 10 | days_until_peak | -5.112885 | YES |
| 11 | deposit_type_value | +4.590360 | NO |
| 12 | booking_status_Not_Canceled | -4.435885 | NO |
| 13 | is_high_season | -3.606301 | YES |
| 14 | meal_plan_value | +3.455980 | NO |
| 15 | season | -3.224899 | YES |

**Key finding**: 6 of top 15 features are engineered. Top feature is `room_type_value` (+11.15).

---

## Leakage Analysis

### Target-Derived Features
- **Count**: 0 (in SAFE feature set)
- **Severity**: NONE
- **Impact**: None

### Prediction-Time Availability
- **Count**: 0 issues
- **All features**: Available at prediction time

### Inflation Analysis
- **R2 inflation from target-derived**: 0.000000
- **CV inflation from target-derived**: 0.000000

---

## Verdict

```
+================================================+
|  VERDICT: VALIDATED                            |
|  REASON:  All checks passed                    |
|  LEAKAGE: None                                 |
|  STRATEGY: Identical to Sprint 3               |
+================================================+
```

### Evidence
1. Validation strategy is **IDENTICAL** to Sprint 3 (same split, same CV, same rolling)
2. **Zero target-derived features** in the SAFE feature set
3. All features are available at prediction time
4. No inflation from target-derived features

---

## Recommendations

### For Production
1. Use the 44 SAFE features (27 baseline + 17 engineered)
2. Do NOT include `build_temporal_aggregate_features` output
3. Retrain ElasticNet with the SAFE feature set

### For Future Sprints
1. Focus on features that don't use the target variable
2. Consider external data sources (weather, events, competitor prices)
3. Improve R² through better features, not target-derived features

---

## Files Generated

| File | Content |
|------|---------|
| `reports/sprint6_validation.json` | Full validation data |
| `reports/feature_importance_ranking.json` | Feature importance |
| `docs/leakage_assessment.md` | This report |

---

*Generated by Sprint 6 validation pipeline*
