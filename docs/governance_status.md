# Governance Status Report

**Generated**: June 2026
**Audit Scope**: Full repository governance
**Maturity Level**: Research Prototype

---

## Repository Overview

| Attribute | Value |
|-----------|-------|
| Name | Optimus Price |
| Purpose | Hotel revenue management ML system |
| Maturity | Research Prototype |
| Champion Model | ElasticNet |
| Primary Dataset | hotel_reservations_real.csv (117,429 rows) |
| Total Artifacts | 37 tracked |

---

## Datasets

| Dataset | Rows | Encoding | Status |
|---------|------|----------|--------|
| hotel_reservations_real.csv | 117,429 | Label-encoded | **PRIMARY** |
| hotel_reservations_clean.csv | 34,546 | One-hot | Legacy |
| hotel_reservations_enriched.csv | 34,546 | One-hot | Experimental |
| hotel_reservations_fe.csv | 34,579 | Feature-engineered | Experimental |
| hotel_bookings_kaggle.csv | 119,390 | Raw | Raw source |

---

## Models

### Champion

| Attribute | Value |
|-----------|-------|
| Model | ElasticNet |
| R2 | 0.3467 |
| RMSE | 31.79 |
| File | pipeline_elasticnet_20260627_190014.pkl |
| Size | 2.6KB |

### All Models

| Model | R2 | RMSE | Status |
|-------|-----|------|--------|
| ElasticNet | 0.3467 | 31.79 | CHAMPION |
| GradientBoosting | 0.1428 | 36.41 | Baseline |
| LightGBM | 0.1512 | 36.23 | Baseline |
| XGBoost | 0.1411 | 36.45 | Baseline |
| CatBoost | 0.1118 | 37.06 | Baseline |
| RandomForest | -0.0249 | 39.82 | Deprecated |
| OccupancyModel | AUC=0.8575 | - | Active |

---

## Benchmarks

| Strategy | ElasticNet | GradientBoosting | Winner |
|----------|------------|------------------|--------|
| Holdout R2 | 0.3467 | 0.1428 | ElasticNet |
| TSCV R2 | 0.2158 | 0.1103 | ElasticNet |
| Rolling R2 | 0.2650 | 0.1643 | ElasticNet |

---

## Metrics

### Active Metrics

| Metric | Value | Source |
|--------|-------|--------|
| R2 | 0.3467 | benchmark_results.json |
| RMSE | 31.79 | benchmark_results.json |
| MAE | 24.39 | benchmark_results.json |
| MAPE | 23.83% | benchmark_results.json |
| Accuracy (occupancy) | 79.4% | validation_report.json |
| AUC-ROC (occupancy) | 0.8575 | validation_report.json |

### Deprecated Metrics

| Metric | Old Value | New Value | Reason |
|--------|-----------|-----------|--------|
| R2 | 0.9998 | 0.3467 | Target leakage removed |
| RMSE | 0.38 | 31.79 | Target leakage removed |
| RF R2 | 0.81 | -0.0249 | Synthetic data era |

---

## Artifacts

### Active Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| ElasticNet model | models/pipeline_elasticnet_20260627_190014.pkl | Active |
| Production alias | models/pipeline_trained_model.pkl | Active |
| Occupancy model | models/occupancy_predictor.pkl | Active |
| Benchmark results | reports/benchmark_results.json | Active |
| Feature analysis | reports/feature_analysis.json | Active |
| Validation report | benchmark_validation_report.md | Active |

### Deprecated Artifacts

| Artifact | Path | Reason |
|----------|------|--------|
| GB model | models/pipeline_gradientboosting_20260626_192846.pkl | Replaced by ElasticNet |
| RF model | models/pipeline_randomforest_20260627_184318.pkl | Negative R2 |

### Orphan Artifacts

| Artifact | Path | Issue |
|----------|------|-------|
| validation_report.json | validation_report.json | Says "production_ready" with GB as champion |
| retrain_report.json | retrain_report.json | Contains leaked metrics |

---

## Deprecated Metrics

| Metric | Location | Issue |
|--------|----------|-------|
| R2=0.9998 | README.md, AGENTS.md (old) | Target leakage |
| RMSE=0.38 | README.md, AGENTS.md (old) | Target leakage |
| RF R2=0.81 | data/reports/metrics_benchmark.md | Synthetic data |
| CatBoost R2=0.82 | data/reports/metrics_benchmark.md | Synthetic data |
| 10M rows | README.md, roadmap.md (old) | Actual: 117K |
| 41 features | README.md, roadmap.md (old) | Actual: 27 |

---

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| validation_report.json outdated | HIGH | Pending update |
| retrain_report.json has leaked metrics | HIGH | Pending cleanup |
| No sklearn version logged | MEDIUM | Pending implementation |
| No train/test indices saved | MEDIUM | Pending implementation |
| No artifact schema | MEDIUM | Pending implementation |
| benchmark_results.json missing ElasticNet CV | LOW | Partial data |

---

## Reproducibility Gaps

| Gap | Impact | Phase |
|-----|--------|-------|
| No sklearn version in artifacts | Cannot reproduce exact results | Phase 7 |
| No random seed logged | Results may vary | Phase 7 |
| No train/test indices saved | Cannot verify split | Phase 7 |
| No full params in artifacts | Cannot rebuild model | Phase 7 |

---

## Governance Score

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Reproducibility | 4/10 | 25% | 1.00 |
| Documentation consistency | 7/10 | 20% | 1.40 |
| Metric provenance | 5/10 | 20% | 1.00 |
| Versioning | 3/10 | 15% | 0.45 |
| Benchmark coverage | 8/10 | 10% | 0.80 |
| Artifact completeness | 6/10 | 10% | 0.60 |
| **TOTAL** | | | **5.25/10** |

### Score Breakdown

- **Reproducibility (4/10)**: Models saved but no version/seed/params logged
- **Documentation (7/10)**: AGENTS.md and roadmap.md updated, some stale docs remain
- **Provenance (5/10)**: benchmark_results.json exists, but no sklearn version
- **Versioning (3/10)**: No semantic versioning, no model versioning
- **Benchmarks (8/10)**: 6-model comparison with 3 validation strategies
- **Artifacts (6/10)**: Main artifacts tracked, some orphans remain

---

## Open Actions

| Action | Priority | Phase |
|--------|----------|-------|
| Update validation_report.json | HIGH | Sprint 2 |
| Clean retrain_report.json | HIGH | Sprint 2 |
| Add sklearn version to artifacts | MEDIUM | Phase 7 |
| Save train/test indices | MEDIUM | Phase 7 |
| Implement model versioning | MEDIUM | Phase 7 |
| Remove deprecated model files | LOW | Sprint 2 |

---

## Single Source of Truth

| Item | Value | File |
|------|-------|------|
| Champion Model | ElasticNet | model_registry.yaml |
| Primary Dataset | hotel_reservations_real.csv | dataset_registry.yaml |
| R2 | 0.3467 | metrics_registry.md |
| RMSE | 31.79 | metrics_registry.md |
| MAE | 24.39 | metrics_registry.md |
| MAPE | 23.83% | metrics_registry.md |
| Validation | Temporal, TSCV, Rolling | benchmark_validation_report.md |
| Maturity | Research Prototype | This file |

---

*Generated by governance audit. Review quarterly.*
