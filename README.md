<p align="center">
  <img src="docs/img/optimus_price_banner.png" alt="Optimus Price" width="100%">
</p>

<p align="center">
  <b>Hotel Pricing Predictor — Research Prototype</b><br>
  ML-powered price prediction · Historical data analysis · Interpretable models
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-7C8595?logo=python">
  <img src="https://img.shields.io/badge/Streamlit-7C8595?logo=streamlit">
  <img src="https://img.shields.io/badge/scikit--learn-7C8595?logo=scikit-learn">
  <img src="https://img.shields.io/badge/license-MIT-7C8595">
</p>

---

## What This Is

**Optimus Price** is a machine learning system that predicts hotel room prices based on historical booking data. It uses a simple, interpretable ElasticNet model trained on real booking data from Kaggle.

**This is a research prototype, not a production system.**

---

## Current State (V1 — FROZEN)

| Metric | Value |
|--------|-------|
| **Champion Model** | ElasticNet (alpha=0.024, l1_ratio=0.725) |
| **R²** | 0.3467 |
| **RMSE** | 31.63 |
| **MAE** | 24.39 |
| **MAPE** | 23.83% |
| **Features** | 27 (label-encoded) |
| **Dataset** | 117,429 bookings (Kaggle) |
| **UI** | Streamlit |
| **Maturity** | Research Prototype |

**V1 is FROZEN** — No further development. Historical Kaggle baseline only.

---

## V2 Status — Market Intelligence (IN PROGRESS)

| Component | Status |
|-----------|--------|
| **Data Model Redesign** | ✅ Complete — `market_index`, `price_bands`, `demand_signals`, `seasonality_index` |
| **INE Ingester** | ✅ Complete — Parses CSV, creates seasonality_index |
| **Google Trends Ingester** | ✅ Complete — Parses CSV exports |
| **Market Context Provider** | ✅ Complete — Connects V2 to V1 predictions |
| **V2 Database** | ✅ Complete — SQLite, 4 tables, segment-aware |
| **V2 Tests** | ✅ 10/10 passing |
| **Real Data Ingestion** | 🔄 **IN PROGRESS** — INE API (table 2066), IBESTAT, CAIB open data |
| **V2 Dashboard** | ❌ Rejected by user — needs rebuild |
| **OTA Scraping** | ❌ **ABANDONED** — All 12 attempts returned empty (JS SPA + anti-bot) |

**V2 Strategy**: Multi-fuente (INE primary, Google Trends proxy, Airbnb limited, user data manual)

---

## Quick Start (V1)

```bash
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final
pip install -r requirements.txt

# Train model (V1 frozen)
python -m src.optimus_price.training

# Run V1 dashboard
streamlit run app_streamlit/app_cliente.py
```

---

## Architecture

```
Optimus_Price_Final/
├── src/optimus_price/           # V1 — FROZEN
│   ├── training.py              # Model training (ElasticNet champion)
│   ├── data_processing.py       # Data loading and cleaning
│   ├── feature_builder.py       # Feature engineering (27 features)
│   ├── evaluation.py            # Model evaluation
│   ├── occupancy_model.py       # Occupancy prediction (V2 stub)
│   ├── elasticity_engine.py     # Price elasticity (V2 stub)
│   ├── revenue_optimizer.py     # Revenue optimization (V2 stub)
│   ├── prediction_service.py    # V1 + optional V2 market_context
│   └── time_series_enricher.py  # Seasonal decomposition (Phase 3)
├── src/v2_pipeline/             # V2 — IN PROGRESS
│   ├── market_db.py             # 4-table schema (market_index, price_bands, demand_signals, seasonality_index)
│   ├── ine_ingester.py          # INE CSV parser + seasonality
│   ├── gtrends_ingester.py      # Google Trends CSV parser
│   ├── market_context.py        # V2 context for V1 predictions
│   ├── aggregator.py            # Market aggregates computation
│   ├── validator.py             # Data validation
│   └── ingester.py              # Legacy (market_prices table)
├── app_streamlit/
│   ├── app_cliente.py           # V1 dashboard with market context tab
│   └── app_market_intelligence.py  # V2 dashboard (REJECTED — needs rebuild)
├── models/                      # Trained models
├── data/
│   ├── processed/               # V1: hotel_reservations_real.csv
│   └── v2_market/               # V2: raw/ + processed/market_intelligence.db
├── scripts/                     # Analysis & training scripts
├── docs/                        # Documentation
├── tests/
│   └── test_v2_pipeline.py      # 10 tests passing
└── archive/                     # Dead V2 code (scraping, monitoring, etc.)
```

---

## V1 ML Pipeline

1. **Data Loading** — `hotel_reservations_real.csv` (117K rows, 27 features)
2. **Feature Engineering** — Temporal features (sin/cos encoding), booking behavior
3. **Training** — ElasticNet with StandardScaler pipeline (Optuna optimized)
4. **Validation** — Temporal split (80/20), TimeSeriesSplit (3-fold), Rolling window
5. **Evaluation** — RMSE, MAE, R², MAPE vs baselines

---

## Why ElasticNet Wins

| Model | R² | RMSE | Notes |
|-------|-----|------|-------|
| **ElasticNet (optimized)** | **0.3467** | **31.63** | **Champion — interpretable, fast, small** |
| GradientBoosting | 0.1428 | 36.41 | Overfits, worse than linear |
| LightGBM | 0.1512 | 36.23 | Overfits |
| XGBoost | 0.1411 | 36.45 | Overfits |
| CatBoost | 0.1118 | 37.06 | Overfits |
| RandomForest | -0.0249 | 39.82 | Negative R² |

**Root cause**: Weak nonlinear signal + multicollinearity (arrival_month/week_number r=0.995). Tree models overfit 48x more than ElasticNet.

---

## V2 Phases Completed

### Phase 2: Baseline Comparison ✅
- ML (ElasticNet RMSE=31.79) vs 5 baselines
- Best baseline: Room Type RMSE=36.97
- **ML improves +14% RMSE, +0.23 R²**

### Phase 3: Time-Series Enrichment ✅
- `time_series_enricher.py`: Additive decomposition, cyclical encoding, seasonal factors
- **Marginal impact (+0%)** — arrival_month already captures seasonality

### Phase 6: Hyperparameter Optimization ✅
- Optuna 10-trial search
- Optimized: alpha=0.024, l1_ratio=0.725
- **RMSE=31.63 (+0.5% improvement)**

---

## V2 Documentation

| Document | Status |
|----------|--------|
| `docs/V2_REALITY_ASSESSMENT.md` | Complete — 25% maturity, scraping broken |
| `docs/V2_DATA_MODEL_REDESIGN.md` | Complete — New 4-table model |
| `docs/V2_SOURCE_STRATEGY.md` | Complete — Multi-fuente strategy |
| `docs/v2_market_map.md` | Complete — 6 Mallorca segments |
| `docs/v2_readiness_checklist.md` | Complete — 52 items |

---

## V2 Data Sources (Target)

| Source | Data | Status |
|--------|------|--------|
| **INE API** (table 2066) | Occupancy by CCAA, establishments, beds | 🔄 Downloading |
| **IBESTAT** | Monthly hotel survey: open establishments, plazas, travelers, overnight stays, occupancy, ADR, RevPAR | 🔄 Downloading |
| **Portal Estadísticas Govern CAIB** | 2008-2024 historical series | 🔄 Downloading |
| **Datos Abiertos CAIB** | Open data catalog | 🔄 Exploring |
| **FEHM** | Hotel federation data | 🔄 Exploring |
| **Google Trends** | Search interest (demand proxy) | ✅ Ingester ready |
| **Airbnb (limited)** | Listing prices (auxiliary) | ✅ Ingester ready |

---

## Limitations (V1)

1. **R² is low (0.35)** — Dataset lacks location, brand, star rating features
2. **No live competitor data** — OTAs are JS SPAs, cannot be scraped
3. **No real-time pricing** — Batch training only
4. **No revenue optimization** — Predicts price, doesn't optimize revenue
5. **No model interpretability** — SHAP not yet implemented
6. **No drift monitoring** — Model degrades silently

---

## Deployment

```bash
docker build -t optimus-price .
docker run -p 8501:8501 optimus-price
```

---

## Documentation

| Document | Status | Description |
|----------|--------|-------------|
| `AGENTS.md` | **Current** | Operational handbook |
| `roadmap.md` | **Current** | Product roadmap |
| `docs/TECHNICAL_AUDIT.md` | **Current** | Full technical audit |
| `docs/leakage_assessment.md` | **Current** | Leakage validation |
| `docs/champion_model_report.md` | **Current** | Model specification |
| `docs/benchmark_final.md` | **Current** | Model comparison |
| `docs/V2_REALITY_ASSESSMENT.md` | **Current** | V2 audit — scraping dead |
| `docs/V2_DATA_MODEL_REDESIGN.md` | **Current** | New V2 data model |
| `docs/V2_SOURCE_STRATEGY.md` | **Current** | Multi-fuente strategy |
| `docs/PRODUCT_SPEC.md` | **Archived** | V2 Vision (not implemented) |
| `docs/DESIGN_SYSTEM.md` | **Archived** | V2 Design (not implemented) |

---

## Contributing

### Code Style

- Python 3.8+
- Type hints preferred
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
```

---

<p align="center">
  <sub>Built with Python, Pandas, Scikit-Learn, and Streamlit</sub><br>
  <sub>Juan de la Fuente — juandelafuentelarrocca@gmail.com</sub><br>
  <sub>Version 1.0 — June 2026</sub>
</p>