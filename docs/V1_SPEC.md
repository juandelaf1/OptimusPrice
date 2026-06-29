# OPTIMUS PRICE — V1 Specification

**Version**: 1.0
**Status**: ACTIVE
**Last Updated**: June 2026

---

## 1. Definition

**Optimus Price V1** is a hotel pricing prediction system that:
- Predicts room prices based on historical booking data
- Uses ElasticNet (linear model) for interpretability
- Validates with temporal split methodology
- Provides feature importance via model coefficients

**This is a research prototype, not a production system.**

---

## 2. System Boundaries

### What V1 DOES

| Capability | Description |
|------------|-------------|
| **Price Prediction** | Predict `avg_price_per_room` from booking features |
| **Feature Importance** | Show which features drive price predictions |
| **Model Comparison** | Compare 6 models (ElasticNet champion) |
| **Temporal Validation** | Split data chronologically (no data leakage) |
| **Basic Dashboard** | Streamlit UI for prediction and analysis |

### What V1 DOES NOT DO

| Capability | Status | Notes |
|------------|--------|-------|
| **Revenue Optimization** | NOT IMPLEMENTED | Needs occupancy data |
| **Competitor Pricing** | NOT IMPLEMENTED | OTAs are JS SPAs |
| **Real-time Pricing** | NOT IMPLEMENTED | Batch training only |
| **Multi-hotel Support** | NOT IMPLEMENTED | Single dataset |
| **API Endpoints** | NOT IMPLEMENTED | Streamlit only |
| **User Authentication** | NOT IMPLEMENTED | No auth system |
| **Drift Monitoring** | NOT IMPLEMENTED | Model degrades silently |
| **SHAP Explainability** | NOT IMPLEMENTED | Coefficients only |

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    V1 ARCHITECTURE                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DATA LAYER                                             │
│  ├── hotel_reservations_real.csv (117K rows)            │
│  ├── 27 features (label-encoded)                        │
│  └── Target: avg_price_per_room                         │
│                                                         │
│  MODEL LAYER                                            │
│  ├── ElasticNet (alpha=0.1, l1_ratio=0.5)              │
│  ├── StandardScaler pipeline                            │
│  ├── Temporal split (80/20)                             │
│  └── Validation: TSCV + Rolling                         │
│                                                         │
│  DECISION LAYER                                         │
│  ├── Price prediction (numerical output)                │
│  ├── Feature coefficients (interpretability)            │
│  └── Model metrics (R2, RMSE, MAE, MAPE)               │
│                                                         │
│  INTERFACE LAYER                                        │
│  ├── Streamlit dashboard                               │
│  └── CLI training script                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Data Specification

### Primary Dataset

| Attribute | Value |
|-----------|-------|
| File | `data/processed/hotel_reservations_real.csv` |
| Rows | 117,429 |
| Features | 27 |
| Target | `avg_price_per_room` |
| Encoding | Label-encoded |
| Source | Kaggle "Hotel Booking Demand" |
| Temporal Range | 2015-2017 |
| Hotels | 2 (Resort Hotel, City Hotel) |

### Features (27)

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | room_type_value | Numerical | Room type (encoded) |
| 2 | arrival_year | Numerical | Year of arrival |
| 3 | market_segment_value | Numerical | Market segment (encoded) |
| 4 | total_guests | Numerical | Adults + children |
| 5 | children | Numerical | Number of children |
| 6 | arrival_month | Numerical | Month of arrival |
| 7 | lead_time | Numerical | Days between booking and arrival |
| 8 | booking_status_Not_Canceled | Binary | Booking was not canceled |
| 9 | arrival_week_number | Numerical | Week of year |
| 10 | distribution_channel_value | Numerical | Distribution channel (encoded) |
| 11 | meal_plan_value | Numerical | Meal plan (encoded) |
| 12 | deposit_type_value | Numerical | Deposit type (encoded) |
| 13 | adults | Numerical | Number of adults |
| 14 | total_of_special_requests | Numerical | Special requests count |
| 15 | arrival_date | Numerical | Day of month |
| 16 | booking_changes | Numerical | Booking modification count |
| 17 | customer_type_value | Numerical | Customer type (encoded) |
| 18 | previous_cancellations | Numerical | Prior cancellation count |
| 19 | stays_in_weekend_nights | Numerical | Weekend nights booked |
| 20 | previous_bookings_not_canceled | Numerical | Prior completed bookings |
| 21 | stays_in_week_nights | Numerical | Weekday nights booked |
| 22 | required_car_parking_spaces | Numerical | Parking spaces needed |
| 23 | days_in_waiting_list | Numerical | Days on waiting list |
| 24 | is_repeated_guest | Binary | Returning guest |
| 25 | arrival_day_of_week | Numerical | Day of week (0=Mon) |
| 26 | total_nights | Numerical | Total nights booked |
| 27 | babies | Numerical | Number of babies |

---

## 5. Model Specification

### Champion: ElasticNet

| Attribute | Value |
|-----------|-------|
| Type | ElasticNet (L1 + L2 regularization) |
| Alpha | 0.1 |
| L1_ratio | 0.5 |
| Max_iter | 5000 |
| Random_state | 42 |
| Pipeline | StandardScaler → ElasticNet |
| File | `models/pipeline_elasticnet_20260627_190014.pkl` |
| Size | 2.6KB |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Split | 80/20 temporal (no shuffle) |
| CV | TimeSeriesSplit (3-fold) |
| Rolling | 3 windows, 60% train |
| Metric | RMSE (primary), R2 (secondary) |

---

## 6. Metrics

### Primary Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **R²** | 0.3467 | Model explains 34.7% of variance |
| **RMSE** | 31.79 | Average error: ±$31.79 |
| **MAE** | 24.39 | Average absolute error: ±$24.39 |
| **MAPE** | 23.83% | Average percentage error: ±23.83% |

### Baseline Comparison

| Model | R² | RMSE | vs Naive |
|-------|-----|------|----------|
| Mean Predictor | 0.0000 | ~40.0 | Baseline |
| **ElasticNet** | **0.3467** | **31.79** | **Better** |
| GradientBoosting | 0.1428 | 36.41 | Worse |

---

## 7. Validation

### Temporal Split

```
Data: [2015 ─────────────────────── 2017]
Train: [2015 ─────────────── 2016] (80%)
Test:  [2017 ─────────────── 2017] (20%)
```

### TimeSeriesSplit (3-fold)

```
Fold 1: Train [2015-2016]     → Test [2016-2017]
Fold 2: Train [2015-2016.5]   → Test [2016.5-2017]
Fold 3: Train [2015-2017]     → Test [2017]
```

### Rolling Window (3 windows)

```
Window 1: Train [60%] → Test [10%]
Window 2: Train [75%] → Test [10%]
Window 3: Train [90%] → Test [10%]
```

---

## 8. Interface

### Streamlit Dashboard

| Tab | Function |
|-----|----------|
| Nueva Reserva | Input booking details, get price prediction |
| Mis Datos | View booking history |
| Analisis de Revenue | Basic revenue analysis |

### CLI Training

```bash
python -m src.optimus_price.training
```

---

## 9. Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| R² = 0.35 | Low predictive power | Accept as baseline |
| No location data | Can't predict location-based pricing | V2 scope |
| No competitor data | Can't adjust for market | V2 scope |
| No real-time | Batch only | V1 acceptable |
| No interpretability | Black box predictions | Coefficients partially address |

---

## 10. V2 Roadmap (Future Work)

> **NOT IMPLEMENTED** — These are aspirational goals.

| Feature | Status | Dependency |
|---------|--------|------------|
| Revenue optimization | Design only | Occupancy data |
| OTA scraping | Research phase | RASPAL integration |
| Real-time pricing | Not started | Competitor data |
| Multi-hotel support | Not started | Architecture redesign |
| API endpoints | Not started | FastAPI + PostgreSQL |
| SHAP explainability | Not started | Model integration |
| Drift monitoring | Not started | MLOps pipeline |

---

## 11. Acceptance Criteria

V1 is considered COMPLETE when:

- [x] ElasticNet model trained on real data
- [x] R² > 0.0 (better than random)
- [x] Temporal validation implemented
- [x] Feature importance available
- [x] Streamlit dashboard functional
- [x] Documentation accurate
- [x] No target leakage
- [x] Baseline naive comparison available

---

## 12. Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 2026 | Initial V1 spec |

---

*This document defines the V1 system. V2 aspirations are documented separately in `docs/archive/`.*
