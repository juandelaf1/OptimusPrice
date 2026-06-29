# OPTIMUS PRICE — Operational Handbook

**Maturity**: Research Prototype
**Version**: V1 — FROZEN
**Champion Model**: ElasticNet (NoScaler)
**Last Updated**: June 2026

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final

# 2. Install
pip install -r requirements.txt

# 3. Train model
python -m src.optimus_price.training

# 4. Run dashboard
streamlit run app_streamlit/app_cliente.py
```

---

## V1 — FROZEN (Kaggle Baseline)

### V1 Champion: ElasticNet + NoScaler

| Metric | Value |
|--------|-------|
| RMSE | 31.48 |
| MAE | 24.22 |
| R² | 0.3594 |
| MAPE | 23.87% |
| Gap R² | 0.004 |
| Features | 27 raw (no engineering) |
| Alpha | 0.024 |
| L1 Ratio | 0.725 |
| Scaler | None (NoScaler) |

### Why NoScaler?

- 27 features are already on similar scales (counts/small integers)
- StandardScaler amplifies noise in low-variance features
- StandardScaler: RMSE=31.63, NoScaler: RMSE=31.48
- RobustScaler: RMSE=31.68, MinMaxScaler: RMSE=32.21

### Why Feature Engineering Failed

| Approach | Test RMSE | R² | Gap R² |
|----------|:---------:|:--:|:------:|
| Baseline (27 raw) | **31.48** | **0.359** | **0.004** |
| + 19 engineered features | 31.95 | 0.340 | 0.213 |
| + 9 INE Baleares features | 34.22 | 0.243 | 0.306 |

All feature engineering attempts increased overfitting. The raw features capture the signal optimally. External INE data applies to V2 (Baleares), not V1 (Portugal Kaggle).

### Multicollinearity

| Features | r | VIF | Action |
|----------|:-:|:---:|--------|
| arrival_month ↔ arrival_week_number | 0.995 | 104 | ⏳ ElasticNet L1 handles it |
| arrival_month ↔ arrival_year | -0.526 | 1.51 | ✅ Tolerable |

VIF>100 but ElasticNet L1 regularization zeroes out redundant features naturally. Dropping `arrival_week_number` slightly hurts performance (RMSE 31.48 → 31.62).

---

## V2 — IN PROGRESS (Mallorca/Baleares)

| Component | Status |
|-----------|--------|
| Data model | ✅ redesigned (4 tables) |
| INE ingester | ✅ built (needs real data) |
| Google Trends ingester | ✅ built |
| Market context provider | ✅ built |
| V2 tests | ✅ 10/10 passing |
| **Real data ingestion** | 🔄 pending |
| **V2 dashboard** | ❌ rejected by user |

### V2 depends on real Baleares hotel price data
INE Baleares occupancy data is downloaded but cannot improve V1 (Portugal dataset). For V2, it will be the primary demand driver.

---

## Sprint ML — Conclusions (June 2026)

1. **ElasticNet + NoScaler + 27 raw features = V1 optimal**
2. Feature engineering adds noise, not signal
3. No overfitting in ElasticNet (Gap R² = 0.004)
4. GradientBoosting overfits severely (Gap R² = 0.70)
5. INE Baleares data inapplicable to V1 (wrong geography)
6. V2 is the real path: Mallorca properties + INE + IBESTAT
7. RobustScaler, StandardScaler, MinMaxScaler all ≈ NoScaler

---

## Repository Structure

### V1 — FROZEN

| Path | Purpose |
|------|---------|
| `src/optimus_price/training.py` | ElasticNet + NoScaler pipeline |
| `src/optimus_price/evaluation.py` | Model evaluation |
| `src/optimus_price/data_processing.py` | Data loading |
| `src/optimus_price/feature_builder.py` | Feature engineering (NOT USED in V1) |
| `app_streamlit/app_cliente.py` | Customer dashboard |
| `models/pipeline_trained_model.pkl` | Frozen V1 champion |

### V2 — IN PROGRESS

| Path | Purpose |
|------|---------|
| `src/v2_pipeline/market_db.py` | 4-table schema |
| `src/v2_pipeline/ine_ingester.py` | INE parser |
| `src/v2_pipeline/gtrends_ingester.py` | Google Trends parser |
| `src/v2_pipeline/market_context.py` | V2 context for V1 |
| `data/v2_market/raw/ine/baleares_occupation_data.csv` | Extracted INE data |

### DATA — Not versioned (in .gitignore)

| Path | Reason |
|------|--------|
| `data/v2_market/processed/` | DB files |
| `data/v2_market/raw/ine/*.csv` | Large CSVs |
| `data/v2_market/raw/airbnb/*.csv` | Generated data |
| `data/v2_market/raw/google_trends/*.csv` | Generated data |
| `data/scraped/` | Scraped artifacts |
| `*.db` | SQLite databases |

---

## Testing

```bash
pytest tests/ -v
```

---

## Infrastructure

```bash
docker build -t optimus-price .
docker run -p 8501:8501 optimus-price
```

---

*Document Version: 4.0 — V1 Frozen*
*Last Updated: June 2026*
