# OPTIMUS PRICE V1 — Product Documentation

**Version**: 1.0
**Status**: ACTIVE
**Last Updated**: June 2026

---

## 1. What Is This Product?

**Optimus Price V1** is a hotel pricing prediction system that estimates the expected price of a room based on historical booking data.

**It is NOT:**
- A revenue optimization system
- A real-time pricing engine
- A competitor monitoring tool
- A booking management system

**It IS:**
- A prediction tool that outputs a price estimate
- A system that explains which factors drive the price
- A system that quantifies uncertainty via confidence ranges

---

## 2. User Flow

### 2.1 Customer Portal

```
┌─────────────────────────────────────────────────────────┐
│  1. INPUT                                                │
│  ├── Personal data (name, email, phone)                  │
│  ├── Booking dates (arrival, departure)                  │
│  └── Preferences (room type, guests, meal plan)          │
│                                                          │
│  2. PROCESS                                              │
│  ├── System builds feature vector                        │
│  ├── ElasticNet model predicts price                     │
│  └── Confidence range calculated from RMSE               │
│                                                          │
│  3. OUTPUT                                               │
│  ├── Predicted price per night (EUR)                     │
│  ├── Total price for stay (EUR)                          │
│  ├── Confidence range (low — high)                       │
│  └── Top 5 factors driving the price                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| Nombre completo | Yes | Customer name |
| Email | Yes | Customer email |
| Telefono | Yes | Customer phone |
| Nacionalidad | No | Defaults to "Espanola" |
| Fecha de llegada | Yes | Arrival date |
| Fecha de salida | Yes | Departure date |
| Plan de comidas | Yes | None / Breakfast / Dinner / All-Inclusive |
| Tipo de habitacion | Yes | Individual / Double / Twin / Triple / Suite / Family |
| Numero de huespedes | Yes | 1-10 guests |
| Estacionamiento | No | Parking required checkbox |
| Solicitudes especiales | No | Free text (comma-separated) |

---

## 3. Output Format

### 3.1 Standardized V1 Output

```json
{
  "predicted_price": 120.45,
  "confidence_range": {
    "low": 88.66,
    "high": 152.24
  },
  "key_drivers": [
    {"feature": "Room Type", "impact": 45.20},
    {"feature": "Season", "impact": 30.15},
    {"feature": "Lead Time", "impact": -15.30},
    {"feature": "Guests", "impact": 12.40},
    {"feature": "Meal Plan", "impact": 8.50}
  ],
  "model_info": {
    "model": "ElasticNet",
    "r2": 0.3467
  }
}
```

### 3.2 Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `predicted_price` | float | Estimated price per night in EUR |
| `confidence_range.low` | float | Lower bound of estimate (predicted - RMSE) |
| `confidence_range.high` | float | Upper bound of estimate (predicted + RMSE) |
| `key_drivers` | list | Top 5 features influencing the price |
| `key_drivers[].feature` | string | Feature name |
| `key_drivers[].impact` | float | Impact on price in EUR (+ = increases, - = decreases) |
| `model_info.model` | string | Model name (ElasticNet) |
| `model_info.r2` | float | Model R² score |

### 3.3 Confidence Range

The confidence range is calculated as:
- `low = max(0, predicted_price - RMSE)`
- `high = predicted_price + RMSE`

Where RMSE = 31.79 (model root mean squared error).

**Interpretation**: The actual price typically falls within this range (~68% of the time).

---

## 4. Key Drivers

The system explains which factors influence the predicted price:

| Driver | Interpretation |
|--------|----------------|
| **Room Type** | Suite rooms cost more than standard rooms |
| **Season** | High season (summer, holidays) increases price |
| **Lead Time** | Last-minute bookings may cost more or less |
| **Guests** | More guests may increase price |
| **Meal Plan** | All-inclusive costs more than no meals |
| **Market Segment** | Different channels have different pricing |
| **Deposit Type** | Non-refundable rates may be cheaper |
| **Special Requests** | Additional requests may increase price |

---

## 5. Model Information

### 5.1 Champion Model: ElasticNet

| Attribute | Value |
|-----------|-------|
| Type | ElasticNet (L1 + L2 regularization) |
| R² | 0.3467 |
| RMSE | 31.79 |
| MAE | 24.39 |
| MAPE | 23.83% |
| Features | 27 |
| Training Data | 117,429 bookings |

### 5.2 What R²=0.35 Means

- The model explains **35% of price variance**
- 65% of variance comes from factors not in the dataset (location, brand, star rating, etc.)
- Predictions are estimates, not exact prices
- Always use the confidence range for decision-making

---

## 6. Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **No location data** | Can't predict location-based pricing | Use as relative estimate |
| **No competitor data** | Can't adjust for market | Monitor competitors separately |
| **No real-time** | Batch training only | Retrain periodically |
| **R²=0.35** | Low explanatory power | Use confidence range |
| **No brand data** | Can't differentiate hotels | Treat as generic hotel |

---

## 7. Technical Stack

| Component | Technology |
|-----------|------------|
| Model | ElasticNet (scikit-learn) |
| Pipeline | StandardScaler → ElasticNet |
| Interface | Streamlit |
| Database | SQLite |
| Training | Batch (CLI) |

---

## 8. Deployment

### 8.1 Run Customer Portal

```bash
streamlit run app_streamlit/app_cliente.py
```

### 8.2 Run Admin Dashboard

```bash
streamlit run app_streamlit/app_adm_1.py
```

### 8.3 Retrain Model

```bash
python -m src.optimus_price.training
```

---

## 9. API (Programmatic Use)

### 9.1 Python

```python
from src.optimus_price.prediction_service import predict_price

result = predict_price({
    "room_type_value": 1,
    "arrival_month": 7,
    "lead_time": 30,
    "total_guests": 2,
    "adults": 2,
    "total_nights": 5,
    "meal_plan_value": 1,
    # ... other features
})

print(result["predicted_price"])  # 120.45
print(result["confidence_range"])  # {"low": 88.66, "high": 152.24}
print(result["key_drivers"])      # [{"feature": "Room Type", "impact": 45.20}]
```

### 9.2 Output Format

```python
{
    "predicted_price": float,      # EUR per night
    "confidence_range": {
        "low": float,              # Lower bound
        "high": float              # Upper bound
    },
    "key_drivers": [
        {"feature": str, "impact": float}
    ],
    "model_info": {
        "model": str,              # "ElasticNet"
        "r2": float                # 0.3467
    }
}
```

---

## 10. FAQ

### Q: How accurate is the prediction?

A: The model has R²=0.35, meaning it explains 35% of price variance. The confidence range (±€31.79) captures ~68% of actual prices.

### Q: Why is the confidence range wide?

A: The dataset lacks key pricing factors (location, brand, star rating). The range reflects this uncertainty.

### Q: Can I use this for real pricing decisions?

A: Use as a starting point, not a final answer. Combine with market knowledge, competitor prices, and business judgment.

### Q: How often should I retrain?

A: Retrain when new booking data is available (monthly recommended).

### Q: What factors most influence price?

A: Room type, season, lead time, guests, and meal plan are the top 5 drivers.

---

*This document defines the V1 product. V2 aspirations are documented in `docs/archive/`.*
