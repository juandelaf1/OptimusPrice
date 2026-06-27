# ROADMAP_EXECUTION.md

**Generated**: June 2026
**Source**: Governance audit + Scientific validation

---

## Phase 0: Governance Hardening

### OP-001: Create metrics registry

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 2h |
| Dependencies | None |
| Acceptance | All metrics documented with formulas and units |
| Artifact | `metrics_registry.md` |

### OP-002: Create model registry

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1h |
| Dependencies | None |
| Acceptance | All models cataloged with versions and params |
| Artifact | `model_registry.yaml` |

### OP-003: Create dataset registry

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1h |
| Dependencies | None |
| Acceptance | All datasets documented with sources and stats |
| Artifact | `dataset_registry.yaml` |

### OP-004: Create artifact registry

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1h |
| Dependencies | None |
| Acceptance | All artifacts cataloged with locations |
| Artifact | `artifact_registry.yaml` |

### OP-005: Create governance status report

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 2h |
| Dependencies | OP-001, OP-002, OP-003, OP-004 |
| Acceptance | Governance score calculated, issues listed |
| Artifact | `governance_status.md` |

---

## Phase 1: Benchmark Stabilization

### OP-010: Run 6-model benchmark

| Field | Value |
|-------|-------|
| Status | COMPLETED |
| Priority | HIGH |
| Effort | 4h |
| Dependencies | None |
| Acceptance | All models compared under identical conditions |
| Artifact | `reports/benchmark_results.json` |

### OP-011: Validate ElasticNet as champion

| Field | Value |
|-------|-------|
| Status | COMPLETED |
| Priority | HIGH |
| Effort | 8h |
| Dependencies | OP-010 |
| Acceptance | ElasticNet wins in holdout, TSCV, rolling |
| Artifact | `benchmark_validation_report.md` |

### OP-012: Perform feature ablation

| Field | Value |
|-------|-------|
| Status | COMPLETED |
| Priority | HIGH |
| Effort | 4h |
| Dependencies | OP-010 |
| Acceptance | Impact of each feature documented |
| Artifact | `benchmark_validation_report.md` |

### OP-013: Investigate why ElasticNet wins

| Field | Value |
|-------|-------|
| Status | COMPLETED |
| Priority | HIGH |
| Effort | 4h |
| Dependencies | OP-010 |
| Acceptance | Root cause documented (linear signal, multicollinearity) |
| Artifact | `benchmark_validation_report.md` |

### OP-014: Generate champion model report

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2h |
| Dependencies | OP-011 |
| Acceptance | Model specs, coefficients, performance documented |
| Artifact | `champion_model_report.md` |

### OP-015: Generate feature reduction report

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2h |
| Dependencies | OP-012 |
| Acceptance | Redundant features identified, removal plan documented |
| Artifact | `feature_reduction_report.md` |

---

## Phase 2: Feature Engineering

### OP-020: Create temporal features

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1d |
| Dependencies | OP-015 |
| Acceptance | month_sin, month_cos, holiday flags added |
| Artifact | Updated `data_processing.py` |

### OP-021: Create rolling window features

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-020 |
| Acceptance | 7d, 14d, 30d rolling stats computed |
| Artifact | Updated `data_processing.py` |

### OP-022: Create lag features

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-020 |
| Acceptance | Lag-1, lag-7 features added |
| Artifact | Updated `data_processing.py` |

### OP-023: Create interaction features

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | LOW |
| Effort | 1d |
| Dependencies | OP-020 |
| Acceptance | Key interactions identified and added |
| Artifact | Updated `data_processing.py` |

### OP-024: Validate feature engineering

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1d |
| Dependencies | OP-020, OP-021, OP-022, OP-023 |
| Acceptance | R2 improves by >= 0.05, no leakage |
| Artifact | Feature engineering report |

---

## Phase 3: Time-Series Enrichment

### OP-030: Seasonality decomposition

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2d |
| Dependencies | OP-024 |
| Acceptance | Seasonal patterns extracted and validated |
| Artifact | Updated `data_processing.py` |

### OP-031: Trend extraction

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-030 |
| Acceptance | Trend features computed |
| Artifact | Updated `data_processing.py` |

### OP-032: Cyclical encoding

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-030 |
| Acceptance | cyclical features validated |
| Artifact | Updated `data_processing.py` |

---

## Phase 4: Market Intelligence

### OP-040: Research competitor data sources

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 2d |
| Dependencies | None |
| Acceptance | Viable data sources identified |
| Artifact | Data source analysis |

### OP-041: Implement competitor feature pipeline

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 3d |
| Dependencies | OP-040 |
| Acceptance | Competitor features available without leakage |
| Artifact | Updated `data_processing.py` |

### OP-042: Market segment analysis

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2d |
| Dependencies | OP-041 |
| Acceptance | Segment-specific pricing models |
| Artifact | Market analysis report |

---

## Phase 5: Elasticity Optimization

### OP-050: Validate elasticity engine

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | None |
| Acceptance | Point and arc elasticity validated |
| Artifact | Elasticity validation report |

### OP-051: Sensitivity analysis

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2d |
| Dependencies | OP-050 |
| Acceptance | Price sensitivity curves documented |
| Artifact | Sensitivity report |

### OP-052: Dynamic pricing rules

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 2d |
| Dependencies | OP-051 |
| Acceptance | Pricing rules implemented and tested |
| Artifact | Updated `revenue_optimizer.py` |

---

## Phase 6: Hyperparameter Optimization

### OP-060: Define Optuna search space

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | None |
| Acceptance | Search space documented |
| Artifact | Optuna config |

### OP-061: Run 50-trial optimization

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-060 |
| Acceptance | best_params.json generated |
| Artifact | `best_params.json` |

### OP-062: Generate optimization report

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-061 |
| Acceptance | Optimization history documented |
| Artifact | `optimization_report.md` |

---

## Phase 7: MLOps

### OP-070: Implement model registry

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 2d |
| Dependencies | OP-002 |
| Acceptance | Models versioned and tracked |
| Artifact | Model registry system |

### OP-071: Implement drift monitoring

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 3d |
| Dependencies | OP-070 |
| Acceptance | Drift detected within 24h |
| Artifact | Drift monitoring system |

### OP-072: Implement automated retraining

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 3d |
| Dependencies | OP-071 |
| Acceptance | Retraining triggered on drift |
| Artifact | Retraining pipeline |

### OP-073: Implement A/B testing

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | LOW |
| Effort | 3d |
| Dependencies | OP-072 |
| Acceptance | Model comparison framework works |
| Artifact | A/B testing system |

---

## Phase 8: Productization

### OP-080: Create API endpoint

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 2d |
| Dependencies | OP-070 |
| Acceptance | API serves predictions |
| Artifact | API endpoint |

### OP-081: Add authentication

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | HIGH |
| Effort | 1d |
| Dependencies | OP-080 |
| Acceptance | Authentication works |
| Artifact | Auth system |

### OP-082: Add rate limiting

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-080 |
| Acceptance | Rate limiting prevents abuse |
| Artifact | Rate limiter |

### OP-083: Write API documentation

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | MEDIUM |
| Effort | 1d |
| Dependencies | OP-080 |
| Acceptance | API docs complete |
| Artifact | API documentation |

### OP-084: Create monitoring dashboard

| Field | Value |
|-------|-------|
| Status | PENDING |
| Priority | LOW |
| Effort | 2d |
| Dependencies | OP-071 |
| Acceptance | Dashboard shows model health |
| Artifact | Monitoring dashboard |

---

## Summary

| Phase | Tasks | Completed | Pending | Effort |
|-------|-------|-----------|---------|--------|
| Phase 0 | 5 | 0 | 5 | 1d |
| Phase 1 | 6 | 4 | 2 | 2d |
| Phase 2 | 5 | 0 | 5 | 5d |
| Phase 3 | 3 | 0 | 3 | 4d |
| Phase 4 | 3 | 0 | 3 | 7d |
| Phase 5 | 3 | 0 | 3 | 5d |
| Phase 6 | 3 | 0 | 3 | 3d |
| Phase 7 | 4 | 0 | 4 | 11d |
| Phase 8 | 5 | 0 | 5 | 7d |
| **Total** | **37** | **4** | **33** | **45d** |

---

*Generated from governance audit findings*
