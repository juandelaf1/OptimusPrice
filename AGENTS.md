# OPTIMUS PRICE — Operational Handbook

**Maturity**: Research Prototype
**Champion Model**: ElasticNet
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

## Current State

### Champion Model: ElasticNet

| Metric | Value |
|--------|-------|
| R2 | 0.3467 |
| RMSE | 31.79 |
| MAE | 24.39 |
| MAPE | 23.83% |
| Model Size | 2.6KB |
| Train Time | 0.27s |

### Dataset

- **Source**: Kaggle "Hotel Booking Demand"
- **File**: `data/processed/hotel_reservations_real.csv`
- **Rows**: 117,429
- **Features**: 27 (label-encoded)
- **Target**: `avg_price_per_room`

### Comparison vs Other Models

| Model | R2 | RMSE | Train Time | Status |
|-------|-----|------|------------|--------|
| **ElasticNet** | **0.3467** | **31.79** | **0.27s** | **CHAMPION** |
| GradientBoosting | 0.1428 | 36.41 | 34.13s | Challenger |
| LightGBM | 0.1512 | 36.23 | 3.06s | Baseline |
| XGBoost | 0.1411 | 36.45 | 1.31s | Baseline |
| CatBoost | 0.1118 | 37.06 | 2.74s | Baseline |
| RandomForest | -0.0249 | 39.82 | 10.78s | Deprecated |

---

## Repository Structure

### ACTIVE — Implemented and working

| Path | Purpose |
|------|---------|
| `src/optimus_price/training.py` | Model training pipeline (ElasticNet primary) |
| `src/optimus_price/evaluation.py` | Model evaluation, feature importance |
| `src/optimus_price/data_processing.py` | Data loading, cleaning, feature prep |
| `src/optimus_price/occupancy_model.py` | Occupancy prediction (79.4% accuracy) |
| `src/optimus_price/elasticity_engine.py` | Price elasticity calculation |
| `src/optimus_price/revenue_optimizer.py` | Revenue optimization engine |
| `app_streamlit/app_cliente.py` | Customer-facing dashboard |
| `app_streamlit/app_adm_1.py` | Admin dashboard |
| `scripts/model_benchmark.py` | 6-model benchmark framework |
| `scripts/feature_analysis.py` | Feature correlation/leakage analysis |

### PARTIAL — Exists but incomplete

| Path | Status |
|------|--------|
| `enhanced_optimus.py` | Competitor intelligence (fallbacks removed) |
| `feature_enricher.py` | Feature enrichment (fallbacks removed) |
| `backend/app/services/` | API backend (synthetic fallbacks removed) |

### DEPRECATED — Do not use

| Path | Reason |
|------|--------|
| `src/optimus_price/data_generator.py` | Deleted — was synthetic data |
| `models/pipeline_randomforest_*.pkl` | Replaced by ElasticNet |
| `models/pipeline_gradientboosting_*.pkl` | Replaced by ElasticNet |

### FUTURE — Not yet implemented

- Optuna hyperparameter optimization
- SHAP explainability
- Temporal feature engineering
- MLOps pipeline
- Drift monitoring

---

## ML Pipeline

### Training

```bash
# Train all models and select champion
python -m src.optimus_price.training
```

### Key Functions

| Function | File | Purpose |
|----------|------|---------|
| `load_processed_data()` | training.py | Load real.csv, remove leaked features |
| `train_all_models()` | training.py | Train all registered models |
| `select_best_model()` | training.py | Select by RMSE |
| `get_feature_importance()` | training.py | Coefficients (EN) or importances (trees) |
| `evaluate_model()` | training.py | RMSE, MAE, R2, MAPE |
| `time_series_cv_score()` | training.py | TimeSeriesSplit CV |

### Model Registry

```python
MODEL_REGISTRY = {
    "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=200, max_depth=6),
    "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=15),
}
```

### Why ElasticNet Wins

1. **Weak nonlinear signal** — GB performs worse than linear regression
2. **Multicollinearity** — arrival_month/arrival_week_number at r=0.995
3. **Overfitting** — GB generalization gap 0.689 vs EN 0.014 (48x)
4. **Feature redundancy** — Tree models split redundantly on correlated features

---

## Data

### Datasets

| File | Rows | Encoding | Use |
|------|------|----------|-----|
| `hotel_reservations_real.csv` | 117,429 | Label-encoded | **PRIMARY** |
| `hotel_reservations_clean.csv` | 34,546 | One-hot | Legacy |
| `hotel_reservations_enriched.csv` | 34,546 | One-hot + extra | Experimental |
| `hotel_reservations_fe.csv` | 34,579 | Feature-engineered | Experimental |

### Features (27)

| Feature | Type | Importance |
|---------|------|------------|
| room_type_value | Numerical | High (EN coef: +11.06) |
| arrival_year | Numerical | High (EN coef: +9.37) |
| market_segment_value | Numerical | High (EN coef: -7.27) |
| total_guests | Numerical | Medium |
| children | Numerical | Medium |
| arrival_month | Numerical | Medium |
| lead_time | Numerical | Medium |
| booking_status_Not_Canceled | Binary | Medium |
| arrival_week_number | Numerical | Medium |
| distribution_channel_value | Numerical | Low |

### Target Leakage Protection

Competitor features (`competitor_avg_price`, etc.) are automatically removed by `load_processed_data()`.

---

## Validation

### Strategies Used

1. **Temporal Split**: 80/20 chronological (no shuffle)
2. **TimeSeriesSplit**: 3-fold expanding window
3. **Rolling Window**: 3 windows, 60% train / 10% test
4. **Walk Forward**: Expanding window, 5 steps

### Key Results

| Strategy | EN R2 | GB R2 | Winner |
|----------|-------|-------|--------|
| Holdout | 0.3467 | 0.1428 | ElasticNet |
| TSCV | 0.2158 | 0.1103 | ElasticNet |
| Rolling | 0.2650 | 0.1643 | ElasticNet |

---

## Infrastructure

### Docker

```bash
docker-compose up -d
```

### CI/CD

- `.github/workflows/ci.yml` — lint + test

### Dashboards

- `app_streamlit/app_cliente.py` — Customer portal
- `app_streamlit/app_adm_1.py` — Admin dashboard

---

## Limitations

1. **R2 is low** (0.35) — dataset lacks location, brand, star rating
2. **No live competitor data** — OTAs are JS SPAs, cannot be scraped
3. **No temporal features** — seasonality partially captured but not optimized
4. **No model interpretability** — SHAP not yet implemented
5. **No drift monitoring** — model degrades silently

---

## Roadmap

See `roadmap.md` for full phased plan.

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | IN PROGRESS | Governance hardening |
| 1 | COMPLETED | Benchmark stabilization |
| 2 | PENDING | Feature engineering |
| 3 | PENDING | Time-series enrichment |
| 4 | PENDING | Market intelligence |
| 5 | PENDING | Elasticity optimization |
| 6 | PENDING | Hyperparameter optimization |
| 7 | PENDING | MLOps |
| 8 | PENDING | Productization |

---

## Contributing

### Code Style

- Python 3.11+
- Type hints required
- No comments unless asked
- Follow existing patterns

### Testing

```bash
pytest tests/ -v
```

### Commit Convention

```
docs: documentation changes
fix: bug fixes
feat: new features
ml: model changes
governance: audit/registry changes
```

---

*Document Version: 2.0*
*Last Updated: June 2026*
*Based on: Governance audit findings*
