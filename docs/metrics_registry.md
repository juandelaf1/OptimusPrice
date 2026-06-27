# Metrics Registry

**Last Updated**: June 2026
**Source of Truth**: This file

---

## Price Model Metrics

| Metric | Value | Formula | Unit | Source |
|--------|-------|---------|------|--------|
| R2 | 0.3467 | 1 - SS_res/SS_tot | dimensionless | benchmark_results.json |
| RMSE | 31.79 | sqrt(mean(y - y_hat)^2) | same as target ($) | benchmark_results.json |
| MAE | 24.39 | mean(|y - y_hat|) | same as target ($) | benchmark_results.json |
| MAPE | 23.83% | mean(|y - y_hat|/y) * 100 | percentage | benchmark_results.json |

## Occupancy Model Metrics

| Metric | Value | Formula | Unit | Source |
|--------|-------|---------|------|--------|
| Accuracy | 79.4% | correct/total | percentage | validation_report.json |
| AUC-ROC | 0.8575 | area under ROC curve | dimensionless | validation_report.json |
| Brier Score | 0.1442 | mean((p - y)^2) | dimensionless | validation_report.json |

## Validation Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Temporal Split R2 | 0.3467 | benchmark_validation_report.md |
| TSCV R2 (3-fold) | 0.2158 +/- 0.0647 | benchmark_validation_report.md |
| Rolling R2 (3 windows) | 0.2650 +/- 0.0574 | benchmark_validation_report.md |

## Deprecated Metrics

| Metric | Value | Reason | Deprecated By |
|--------|-------|--------|---------------|
| R2 (leaked) | 0.9998 | Target leakage from competitor features | R2 = 0.3467 |
| RMSE (leaked) | 0.38 | Target leakage from competitor features | RMSE = 31.79 |
| RF R2 | 0.81 | From synthetic data era | ElasticNet R2 = 0.3467 |
| CatBoost R2 | 0.82 | From synthetic data era | ElasticNet R2 = 0.3467 |

## Metrics Not Yet Generated

| Metric | Status | Blocker |
|--------|--------|---------|
| Optuna best params | Pending | Phase 6 |
| SHAP values | Pending | Phase 6 |
| Feature importance (permutation) | Pending | Phase 6 |
| Drift metrics | Pending | Phase 7 |
| Inference latency (production) | Pending | Phase 8 |

---

*This file is the single source of truth for all metrics.*
