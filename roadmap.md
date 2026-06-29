# OPTIMUS PRICE — Product Roadmap

**Status**: V1 — FROZEN
**Champion**: ElasticNet + NoScaler (RMSE=31.48, R²=0.3594)
**Last Updated**: June 2026

---

## V1 — FROZEN (No Further Development)

### Achieved

- [x] ElasticNet champion (alpha=0.024, l1_ratio=0.725)
- [x] NoScaler proven optimal (vs Standard, Robust, MinMax)
- [x] No overfitting (Gap R² = 0.004)
- [x] 19 engineered features tested → discarded (add noise)
- [x] 9 INE Baleares features tested → discarded (wrong geography)
- [x] Optuna hyperparameter optimization completed
- [x] Streamlit dashboard
- [x] Docker deployment

### What Was Ruled Out

| Approach | Result | Reason |
|----------|--------|--------|
| Feature engineering | ❌ Worsens model | Transforms redundant noise |
| INE external data | ❌ Worsens model | Kaggle dataset is Portugal, not Spain |
| Dropping week_number | ❌ Slightly worse | L1 handles VIF naturally |
| GradientBoosting | ❌ Overfits severely | Gap R² = 0.70 |

---

## V2 — IN PROGRESS

### Completed

- [x] V2 audit (scraping dead, 25% maturity)
- [x] Dead V2 code archived
- [x] Data model redesigned (4 tables)
- [x] INE ingester built
- [x] Google Trends ingester built
- [x] Market context provider built
- [x] V2 tests (10/10 passing)
- [x] INE Baleares data downloaded (329 monthly obs, 1998-2026)

### Pending (blocked by real Baleares hotel data)

- [ ] Real data ingestion into market_intelligence.db
- [ ] V2 dashboard redesign
- [ ] Market context → V1 predictions integration

### Key Blockers

1. **No Baleares hotel price dataset** — INE occupancy is ready but needs matching price data
2. **OTA scraping impossible** — All 12 attempts blocked by anti-bot
3. **V2 dashboard rejected** — Needs complete rethink

---

## Sprint ML Conclusions (June 2026)

The ElasticNet model on 27 raw features with NoScaler is the optimal configuration for V1:

- **No more V1 improvements possible** with current data
- **Feature engineering adds noise** — 19 features increased RMSE by 0.47
- **INE Baleares data can't help V1** — wrong geographic region
- **V2 needs real Mallorca hotel data** to unlock INE/IBESTAT value

---

## Metrics

### V1 Frozen

| Metric | Value | Status |
|--------|-------|--------|
| RMSE | 31.48 | ✅ Frozen |
| R² | 0.3594 | ✅ Frozen |
| MAE | 24.22 | ✅ Frozen |
| MAPE | 23.87% | ✅ Frozen |
| Gap R² | 0.004 | ✅ No overfitting |

### V2 Targets

| Metric | Current | Target |
|--------|---------|--------|
| R² | N/A | > 0.50 |
| RMSE | N/A | < 25.0 |
| Real data sources | 1 (INE) | 4+ (INE, IBESTAT, CAIB, FEHM) |

---

*V1 Frozen. June 2026.*
