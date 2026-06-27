# OPTIMUS PRICE — Product Roadmap

**Current Status**: Research Prototype
**Champion Model**: ElasticNet (R2=0.3467)
**Last Updated**: June 2026

---

## Vision

Build an ML-powered hotel revenue management system that optimizes pricing using real data, validated models, and reproducible pipelines.

## Current State

### Implemented

- ElasticNet pricing model (champion)
- Occupancy prediction model
- Revenue optimization engine
- Price elasticity engine
- Benchmarking framework (6 models)
- Governance audit system
- Docker deployment
- Streamlit dashboards

### Partially Implemented

- Competitor intelligence (fallbacks removed, needs real data source)
- OTA scraping (OTAs are JS SPAs, cannot be scraped directly)
- Monitoring (basic, no drift detection)

### Not Implemented

- Optuna hyperparameter optimization
- SHAP explainability
- Temporal feature engineering
- MLOps pipeline
- Drift monitoring
- Model registry automation

---

## Roadmap Phases

### Phase 0: Governance Hardening

**Status**: IN PROGRESS
**Objective**: Create single source of truth for all artifacts

| Deliverable | Status |
|-------------|--------|
| metrics_registry.md | PENDING |
| model_registry.yaml | PENDING |
| dataset_registry.yaml | PENDING |
| artifact_registry.yaml | PENDING |
| benchmark_results.json | EXISTS |
| feature_analysis.json | EXISTS |
| governance_status.md | PENDING |

**Success Criteria**:
- All metrics reproducible
- All artifacts cataloged
- No conflicting metrics
- Contributor can understand project state in <15 minutes

**Dependencies**: None
**Effort**: 1 day
**Risk**: LOW

---

### Phase 1: Benchmark Stabilization

**Status**: COMPLETED
**Objective**: Validate ElasticNet as champion model

| Deliverable | Status |
|-------------|--------|
| benchmark_results.json | EXISTS |
| benchmark_validation_report.md | EXISTS |
| champion_model_report.md | PENDING |
| feature_reduction_report.md | PENDING |

**Completed Work**:
- 6-model comparison (ElasticNet, GB, XGB, LGB, CatBoost, RF)
- TSCV, Rolling, Walk-Forward validation
- Feature ablation study
- Multicollinearity analysis
- Overfitting analysis

**Success Criteria**:
- ElasticNet remains champion after ablation
- All validation strategies confirm superiority
- Root cause of GB underperformance documented

**Dependencies**: None
**Effort**: 2 days (COMPLETED)
**Risk**: LOW

---

### Phase 2: Feature Engineering

**Status**: PENDING
**Objective**: Improve R2 from 0.35 to 0.45+

| Task | Status |
|------|--------|
| Temporal features (month_sin, month_cos) | PENDING |
| Holiday flags | PENDING |
| Rolling windows (7d, 14d, 30d) | PENDING |
| Lag features (booking lead time) | PENDING |
| Interaction features | PENDING |

**Success Criteria**:
- R2 improves by >= 0.05
- No new multicollinearity introduced
- Feature importance stable across folds

**Dependencies**: Phase 1
**Effort**: 1 week
**Risk**: MEDIUM

---

### Phase 3: Time-Series Enrichment

**Status**: PENDING
**Objective**: Capture temporal patterns

| Task | Status |
|------|--------|
| Seasonality decomposition | PENDING |
| Trend extraction | PENDING |
| Cyclical encoding | PENDING |
| Rolling statistics | PENDING |

**Success Criteria**:
- Temporal features improve R2 by >= 0.03
- Model captures seasonal pricing patterns
- Validation confirms no data leakage

**Dependencies**: Phase 2
**Effort**: 1 week
**Risk**: MEDIUM

---

### Phase 4: Market Intelligence

**Status**: PENDING
**Objective**: Integrate competitor and market data

| Task | Status |
|------|--------|
| Competitor price scraping (if feasible) | PENDING |
| Market segment analysis | PENDING |
| Demand forecasting | PENDING |
| Event-driven pricing | PENDING |

**Success Criteria**:
- Competitor features improve R2 by >= 0.05
- No target leakage introduced
- Data source is sustainable

**Dependencies**: Phase 2
**Effort**: 2 weeks
**Risk**: HIGH (OTAs block scraping)

---

### Phase 5: Elasticity Optimization

**Status**: PENDING
**Objective**: Optimize pricing using elasticity curves

| Task | Status |
|------|--------|
| Point elasticity calculation | EXISTS |
| Arc elasticity calculation | EXISTS |
| Revenue curve optimization | EXISTS |
| Sensitivity analysis | PENDING |
| Dynamic pricing rules | PENDING |

**Success Criteria**:
- Optimal price recommendation validated
- Revenue gain >= 10% in simulation
- Elasticity estimates stable

**Dependencies**: Phase 1
**Effort**: 1 week
**Risk**: LOW

---

### Phase 6: Hyperparameter Optimization

**Status**: PENDING
**Objective**: Tune models with Optuna

| Task | Status |
|------|--------|
| Optuna search space definition | PENDING |
| 50-trial optimization | PENDING |
| Cross-validation strategy | PENDING |
| Best params export | PENDING |

**Success Criteria**:
- Best params saved to best_params.json
- Optimization report generated
- Model performance improves or matches champion

**Dependencies**: Phase 1
**Effort**: 3 days
**Risk**: LOW

---

### Phase 7: MLOps

**Status**: PENDING
**Objective**: Production-ready model management

| Task | Status |
|------|--------|
| Model registry | PENDING |
| Drift monitoring | PENDING |
| Automated retraining | PENDING |
| A/B testing framework | PENDING |
| Logging and observability | PENDING |

**Success Criteria**:
- Model performance tracked over time
- Drift detected within 24 hours
- Retraining triggered automatically

**Dependencies**: Phase 6
**Effort**: 2 weeks
**Risk**: MEDIUM

---

### Phase 8: Productization

**Status**: PENDING
**Objective**: Production deployment

| Task | Status |
|------|--------|
| API endpoint | PENDING |
| Authentication | PENDING |
| Rate limiting | PENDING |
| Documentation | PENDING |
| Monitoring dashboard | PENDING |

**Success Criteria**:
- API serves predictions
- Authentication works
- Rate limiting prevents abuse
- Documentation complete

**Dependencies**: Phase 7
**Effort**: 2 weeks
**Risk**: MEDIUM

---

## Success Metrics

### Technical KPIs

| Metric | Current | Target |
|--------|---------|--------|
| R2 | 0.3467 | 0.50 |
| RMSE | 31.79 | 25.00 |
| MAPE | 23.83% | 18.00% |
| Model Size | 2.6KB | <10KB |
| Inference Time | <0.01ms | <1ms |

### Process KPIs

| Metric | Current | Target |
|--------|---------|--------|
| Metrics Reproducible | Partial | 100% |
| Artifacts Cataloged | Partial | 100% |
| Tests Passing | Yes | Yes |
| Documentation Accurate | No | Yes |

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| OTA scraping blocked | HIGH | Use alternative data sources |
| Feature engineering introduces leakage | MEDIUM | Validate each feature |
| Model overfits to training data | MEDIUM | Cross-validation |
| Data quality degrades | LOW | Monitoring |

---

## Timeline

| Phase | Duration | Start |
|-------|----------|-------|
| Phase 0 | 1 day | Now |
| Phase 1 | 2 days | COMPLETED |
| Phase 2 | 1 week | After Phase 0 |
| Phase 3 | 1 week | After Phase 2 |
| Phase 4 | 2 weeks | After Phase 2 |
| Phase 5 | 1 week | After Phase 1 |
| Phase 6 | 3 days | After Phase 1 |
| Phase 7 | 2 weeks | After Phase 6 |
| Phase 8 | 2 weeks | After Phase 7 |

**Total estimated**: 10-12 weeks

---

*Document Version: 2.0*
*Last Updated: June 2026*
*Based on: Governance audit findings*
