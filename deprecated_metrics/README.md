# Deprecated Metrics

**Created**: June 2026
**Purpose**: Archive of metrics that are no longer valid

---

## Why These Metrics Are Deprecated

These metrics were computed on synthetic data or with target leakage. They do not reflect real model performance.

---

## Deprecated Files

| File | Original Metric | Issue | Deprecated Date |
|------|----------------|-------|-----------------|
| `metrics_benchmark.md` | RF R2=0.81, CatBoost R2=0.82 | Synthetic data era | 2026-06-26 |

---

## Current Valid Metrics

| Metric | Value | Source |
|--------|-------|--------|
| ElasticNet R2 | 0.3467 | benchmark_results.json |
| ElasticNet RMSE | 31.79 | benchmark_results.json |
| ElasticNet MAE | 24.39 | benchmark_results.json |
| ElasticNet MAPE | 23.83% | benchmark_results.json |

---

*Do not use metrics from this directory for any decisions.*
