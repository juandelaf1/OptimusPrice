# AUDITORÍA TÉCNICA — OPTIMUS PRICE V1

**Fecha**: Junio 2026
**Auditor**: Principal Product Architect + Lead ML Engineer
**Alcance**: Estado actual del repositorio, definición de producto, roadmap V1

---

## 1. ESTADO REAL DEL REPOSITORIO

### 1.1 Inventario del Código

| Componente | Archivo | Estado | Nota |
|------------|---------|--------|------|
| **Training Pipeline** | `src/optimus_price/training.py` | FUNCIONA | ElasticNet, temporal split, leakage check |
| **Data Processing** | `src/optimus_price/data_processing.py` | FUNCIONA | Limpieza básica, one-hot encoding |
| **Feature Builder** | `src/optimus_price/feature_builder.py` | FUNCIONA | 17 features temporales + booking behavior |
| **Occupancy Model** | `src/optimus_price/occupancy_model.py` | FUNCIONA | GradientBoostingClassifier, AUC=0.8575 |
| **Elasticity Engine** | `src/optimus_price/elasticity_engine.py` | FUNCIONA | Point/arc elasticity, revenue curves |
| **Revenue Optimizer** | `src/optimus_price/revenue_optimizer.py` | FUNCIONA | Combina occupancy + elasticity |
| **Evaluation** | `src/optimus_price/evaluation.py` | FUNCIONA | Feature importance, residuals |
| **Customer App** | `app_streamlit/app_cliente.py` | FUNCIONA | Streamlit, predicción + reserva |
| **Admin App** | `app_streamlit/app_adm_1.py` | FUNCIONA | Streamlit, dashboard admin |
| **Enhanced Optimus** | `enhanced_optimus.py` | PARCIAL | RASPAL integration, fallbacks removed |
| **Feature Enricher** | `feature_enricher.py` | PARCIAL | Competitor features, fallbacks removed |
| **Scraping Manager** | `scraping_manager.py` | PARCIAL | Multi-OTA scraper orchestrator |
| **Competitor Monitor** | `competitor_monitor.py` | PARCIAL | OTA comparison engine |
| **Monitoring Service** | `monitoring_service.py` | PARCIAL | Continuous monitoring daemon |

### 1.2 Inventario de Datos

| Dataset | Rows | Features | Estado | Uso |
|---------|------|----------|--------|-----|
| `hotel_reservations_real.csv` | 117,429 | 28 | **PRIMARIO** | Entrenamiento |
| `hotel_reservations_clean.csv` | 34,546 | ~30 | Legacy | One-hot encoding |
| `hotel_reservations_enriched.csv` | 34,546 | ~40 | Experimental | Competitor features |
| `hotel_reservations_fe.csv` | 34,579 | ~50 | Experimental | Feature-engineered |
| `hotel_bookings_kaggle.csv` | 119,390 | 36 | Raw | Fuente original |

### 1.3 Inventario de Modelos

| Modelo | Archivo | R² | RMSE | Estado |
|--------|---------|-----|------|--------|
| **ElasticNet** | `pipeline_elasticnet_20260627_190014.pkl` | 0.3467 | 31.79 | **CHAMPION** |
| GradientBoosting | `pipeline_gradientboosting_*.pkl` | 0.1428 | 36.41 | Baseline |
| LightGBM | (no saved) | 0.1512 | 36.23 | Baseline |
| XGBoost | (no saved) | 0.1411 | 36.45 | Baseline |
| CatBoost | (no saved) | 0.1118 | 37.06 | Baseline |
| RandomForest | `pipeline_randomforest_*.pkl` | -0.0249 | 39.82 | Deprecated |
| **OccupancyModel** | `occupancy_predictor.pkl` | AUC=0.8575 | - | Active |

### 1.4 Inventario de Documentación

| Documento | Estado | Contenido |
|-----------|--------|-----------|
| `README.md` | **DESACTUALIZADO** | Dice R²=0.9998, 41 features, RASPAL integration |
| `AGENTS.md` | **ACTUALIZADO** | R²=0.3467, 27 features, ElasticNet champion |
| `roadmap.md` | **ACTUALIZADO** | 9 phases, research prototype status |
| `ROADMAP_EXECUTION.md` | **ACTUALIZADO** | 37 task IDs, 4 completed |
| `PRODUCT_SPEC.md` | **DESACTUALIZADO** | Next.js + FastAPI + PostgreSQL + RASPAL |
| `DESIGN_SYSTEM.md` | DESCONOCIDO | No leído |
| `governance_status.md` | **ACTUALIZADO** | Score 5.25/10, known issues |
| `leakage_assessment.md` | **ACTUALIZADO** | Sprint 6 validation |
| `benchmark_final.md` | **ACTUALIZADO** | 6-model comparison |
| `champion_model_report.md` | **ACTUALIZADO** | ElasticNet specs |
| `feature_impact_report.md` | **ACTUALIZADO** | Feature importance |

---

## 2. INCONSISTENCIAS DETECTADAS

### 2.1 Inconsistencias Críticas

| Inconsistencia | Documento A | Documento B | Impacto |
|----------------|-------------|-------------|---------|
| **R² value** | README.md: R²=0.9998 | AGENTS.md: R²=0.3467 | ALTO — Usuario confiado en métrica falsa |
| **Feature count** | README.md: 41 features | AGENTS.md: 27 features | ALTO — Descripción incorrecta |
| **Architecture** | PRODUCT_SPEC.md: Next.js + FastAPI + PostgreSQL | Código actual: Streamlit | ALTO — Spec no refleja realidad |
| **Scraping** | README.md: RASPAL integration active | Código: fallbacks removed, scraping broken | ALTO — Funcionalidad fantasma |
| **Maturity** | README.md: "Revenue Intelligence Platform" | governance_status.md: "Research Prototype" | MEDIO — Expectativas desalineadas |

### 2.2 Inconsistencias Menores

| Inconsistencia | Detalle |
|----------------|---------|
| Dataset files | 4 CSVs en data/processed/, solo 1 es primario |
| Model files | Modelos deprecated ainda existen en models/ |
| Deprecated metrics | `deprecated_metrics/metrics_benchmark.md` con métricas de era synthetic |
| Orphan artifacts | `validation_report.json` y `retrain_report.json` con datos desactualizados |

### 2.3 Código Huérfano

| Archivo | Problema |
|---------|----------|
| `enhanced_optimus.py` | RASPAL integration, fallbacks removed, no funciona |
| `feature_enricher.py` | Competitor features, no hay competitor data |
| `scraping_manager.py` | Multi-OTA scraper, OTAs son JS SPAs |
| `competitor_monitor.py` | OTA comparison, no hay datos de competidores |
| `monitoring_service.py` | Monitoring daemon, no hay drift detection |
| `backend/` | FastAPI backend, no implementado |
| `frontend/` | Next.js frontend, no implementado |
| `configs/` | OTA scraping configs, scraping no funciona |

---

## 3. DEFINICIÓN CORREGIDA DE OPTIMUS PRICE V1

### 3.1 Lo que el sistema ES

Un sistema de **pricing predictivo** para hoteles que:
- Predice el precio histórico de habitaciones basado en features disponibles
- Ocupa un modelo ML (ElasticNet) para capturar patrones lineales
- Valida con split temporal correcto (80/20, TSCV, Rolling)
- Provee interpretabilidad básica (coefficients)

### 3.2 Lo que el sistema NO ES (aún)

- NO es un sistema de **recomendación de precio** (no optimiza revenue)
- NO tiene datos de **competencia** (scraping no funciona)
- NO tiene datos de **ubicación** (dataset Kaggle no los tiene)
- NO tiene datos de **marca/categoría** (dataset Kaggle no los tiene)
- NO es **real-time** (entrenamiento batch)
- NO es **multi-tenant** (un solo dataset)

### 3.3 Definición Forzada V1

```
Optimus Price V1 = Sistema de pricing predictivo que predice
el precio histórico de habitaciones hoteleras usando features
de reserva y estacionalidad, con validación temporal correcta
y output interpretable.
```

---

## 4. ARQUITECTURA V1 (3 CAPAS)

### 4.1 DATA LAYER

```
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Dataset Primario                               │   │
│  │  hotel_reservations_real.csv                    │   │
│  │  117,429 rows × 28 columns                     │   │
│  │  Fuente: Kaggle "Hotel Booking Demand"          │   │
│  │  Encoding: Label-encoded                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Features Válidas (27 baseline)                 │   │
│  │  - 14 numéricas (lead_time, guests, etc.)       │   │
│  │  - 8 categóricas (room_type, market, etc.)      │   │
│  │  - 3 temporales (arrival_month, week, day)      │   │
│  │  - 2 binarias (booking_status, repeated_guest)  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Features Eng (17 SAFE)                         │   │
│  │  - 9 temporales (sin/cos, season, quarter)      │   │
│  │  - 8 booking behavior (bins, ratios)            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  RESTRICCIONES:                                         │
│  - Sin scraping en tiempo real                          │
│  - Sin enriquecimiento no verificable                   │
│  - Sin features de target (rolling_mean, lag, etc.)     │
│  - Dataset versionado y auditado                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 MODEL LAYER

```
┌─────────────────────────────────────────────────────────┐
│                    MODEL LAYER                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Pipeline Reproducible                          │   │
│  │  StandardScaler → ElasticNet                    │   │
│  │  Alpha: 0.1, L1_ratio: 0.5, Max_iter: 5000     │   │
│  │  Random_state: 42 (fijo)                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Feature Engineering Controlado                 │   │
│  │  - build_temporal_features() → 9 features       │   │
│  │  - build_booking_behavior_features() → 8 feat   │   │
│  │  - NO build_temporal_aggregate_features()       │   │
│  │  - Total: 27 baseline + 17 engineered = 44      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Entrenamiento Batch                            │   │
│  │  - Split: 80/20 temporal (sin shuffle)          │   │
│  │  - CV: TimeSeriesSplit 3-fold                   │   │
│  │  - Rolling: 3 windows, 60% train                │   │
│  │  - Guardado: joblib + metadata YAML             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.3 DECISION LAYER

```
┌─────────────────────────────────────────────────────────┐
│                   DECISION LAYER                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Output: Predicción de Precio                   │   │
│  │  Input: Features de reserva + estacionalidad    │   │
│  │  Output: avg_price_per_room (predicho)          │   │
│  │  Formato: JSON con precio + confianza           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Interpretación: Coefficients                   │   │
│  │  - room_type_value: +11.15 (mayor precio)      │   │
│  │  - month_sin: -9.59 (estacionalidad)           │   │
│  │  - lead_time: -8.47 (anticipación = menor precio)│   │
│  │  - total_guests: +6.81 (más huéspedes = mayor) │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Lógica Transparente                           │   │
│  │  - No black box decisioning                     │   │
│  │  - Coefficients visibles                        │   │
│  │  - Feature importance rankable                  │   │
│  │  - SHAP (futuro) para interpretabilidad         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  RESTRICCIONES:                                         │
│  - NO optimización multi-objetivo                      │
│  - NO pricing dinámico en tiempo real                   │
│  - NO recomendación de precio (solo predicción)         │
│  - Output claro y accionable                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. DATASET Y FEATURES VÁLIDAS PARA V1

### 5.1 Dataset Primario

| Atributo | Valor |
|----------|-------|
| Archivo | `data/processed/hotel_reservations_real.csv` |
| Rows | 117,429 |
| Features | 27 (label-encoded) |
| Target | `avg_price_per_room` |
| Temporal range | 2015-2017 |
| Hoteles | 2 (Resort Hotel, City Hotel) |
| Fuente | Kaggle "Hotel Booking Demand" |

### 5.2 Features Válidas (27 baseline)

| Feature | Tipo | Importancia | Disponible en predicción |
|---------|------|-------------|--------------------------|
| room_type_value | Num | Alta (+11.15) | SÍ |
| arrival_year | Num | Alta (+8.65) | SÍ |
| market_segment_value | Num | Alta (-5.58) | SÍ |
| total_guests | Num | Media (+6.81) | SÍ |
| children | Num | Media (+7.45) | SÍ |
| arrival_month | Num | Media (+2.52) | SÍ |
| lead_time | Num | Media (-8.47) | SÍ |
| booking_status_Not_Canceled | Bin | Media (-4.44) | SÍ |
| arrival_week_number | Num | Media (+2.00) | SÍ |
| distribution_channel_value | Num | Baja (+2.29) | SÍ |
| meal_plan_value | Num | Baja (+3.46) | SÍ |
| deposit_type_value | Num | Baja (+4.59) | SÍ |
| adults | Num | Baja (+2.71) | SÍ |
| total_of_special_requests | Num | Baja (+2.02) | SÍ |
| arrival_date | Num | Baja (+1.33) | SÍ |
| booking_changes | Num | Baja (+1.20) | SÍ |
| customer_type_value | Num | Baja (-1.16) | SÍ |
| previous_cancellations | Num | Baja (-1.08) | SÍ |
| stays_in_weekend_nights | Num | Baja (-1.06) | SÍ |
| previous_bookings_not_canceled | Num | Baja (-0.90) | SÍ |
| stays_in_week_nights | Num | Baja (+0.75) | SÍ |
| required_car_parking_spaces | Num | Baja (+0.68) | SÍ |
| days_in_waiting_list | Num | Baja (+1.67) | SÍ |
| is_repeated_guest | Num | Baja (-1.67) | SÍ |
| arrival_day_of_week | Num | ~0 | SÍ |
| total_nights | Num | ~0 | SÍ |
| babies | Num | ~0 | SÍ |

### 5.3 Features Eng SAFE (17)

| Feature | Fuente | Target-Derived | Disponible |
|---------|--------|----------------|------------|
| month_sin | arrival_month | NO | SÍ |
| month_cos | arrival_month | NO | SÍ |
| week_sin | arrival_week_number | NO | SÍ |
| week_cos | arrival_week_number | NO | SÍ |
| quarter | arrival_month | NO | SÍ |
| season | arrival_month | NO | SÍ |
| is_high_season | arrival_month | NO | SÍ |
| is_weekend_arrival | arrival_day_of_week | NO | SÍ |
| days_until_peak | arrival_month | NO | SÍ |
| lead_time_bin | lead_time | NO | SÍ |
| short_stay | stays_in_week* | NO | SÍ |
| medium_stay | stays_in_week* | NO | SÍ |
| long_stay | stays_in_week* | NO | SÍ |
| stay_bucket | stays_in_week* | NO | SÍ |
| booking_window | lead_time | NO | SÍ |
| guest_density | adults, children | NO | SÍ |
| room_intensity | adults, room_type | NO | SÍ |

### 5.4 Features PROHIBIDAS en V1

| Feature | Razón |
|---------|-------|
| rolling_mean_7/30/90 | Usa target variable (leakage) |
| lag_7/30/90 | Usa target variable (leakage) |
| adr_trend | Usa target variable (leakage) |
| pickup | Usa target variable (leakage) |
| booking_velocity | Usa cumsum/index (prediction-time unavailable) |
| occupancy_trend | Usa booking_status (safe, pero excluido por consistencia) |
| competitor_* | No hay datos de competidores |
| location_* | No hay datos de ubicación |
| brand_* | No hay datos de marca |

---

## 6. MODELO(S) RECOMENDADOS PARA V1

### 6.1 Champion: ElasticNet

| Atributo | Valor |
|----------|-------|
| Tipo | ElasticNet (L1 + L2 regularization) |
| Alpha | 0.1 |
| L1_ratio | 0.5 |
| Max_iter | 5000 |
| Random_state | 42 |
| Features | 27 baseline (o 44 con engineered) |
| R² | 0.3467 (baseline) / 0.3483 (engineered) |
| RMSE | 31.79 |
| MAE | 24.39 |
| MAPE | 23.83% |
| Model Size | 2.6KB |
| Train Time | 0.27s |

### 6.2 Por qué ElasticNet

1. **Interpretable**: Coefficients directos
2. **Robust**: No overfittea como GB/RF
3. **Rápido**: 0.27s de entrenamiento
4. **Pequeño**: 2.6KB
5. **Validado**: R²=0.3467 en 3 estrategias de validación

### 6.3 Baseline Naive (Obligatorio)

| Modelo | Descripción | R² esperado |
|--------|-------------|-------------|
| **Mean Predictor** | Predice el precio promedio | 0.0 |
| **Last Value** | Predice el último precio conocido | ~0.0 |
| **Seasonal Mean** | Predice promedio por mes | ~0.1-0.2 |

**Comparación obligatoria**: ElasticNet debe superar al baseline naive.

---

## 7. MÉTRICAS CORRECTAS PARA V1

### 7.1 Métricas Secundarias (ML)

| Métrica | Fórmula | Valor Actual | Target V1 |
|---------|---------|--------------|-----------|
| MAE | mean(\|y - ŷ\|) | 24.39 | < 25 |
| RMSE | √mean((y - ŷ)²) | 31.79 | < 32 |
| MAPE | mean(\|y - ŷ\| / y) × 100 | 23.83% | < 24% |

### 7.2 Métrica Principal (Performance vs Baseline)

| Métrica | Fórmula | Target V1 |
|---------|---------|-----------|
| **R² improvement vs naive** | R²_model - R²_naive | > 0.3 |
| **MAE improvement vs naive** | MAE_naive - MAE_model | > 10 |

### 7.3 Métricas de Negocio (Secundarias)

| Métrica | Fórmula | Interpretación |
|---------|---------|----------------|
| Pricing accuracy | 1 - MAPE/100 | % de precisión del precio |
| Error absoluto promedio | MAE | Cuánto se equivoca en € |

---

## 8. ROADMAP V1 (ORDENADO Y PRIORIZADO)

### Fase 1 — Corrección (CRÍTICA) — 1 semana

| # | Acción | Dependencia | Effort | Impacto |
|---|--------|-------------|--------|---------|
| 1.1 | **Eliminar README.md desactualizado** | Ninguna | 1h | CRÍTICO |
| 1.2 | **Crear README.md nuevo** con estado real | 1.1 | 2h | CRÍTICO |
| 1.3 | **Eliminar código huérfano** (enhanced_optimus.py, feature_enricher.py, etc.) | Ninguna | 2h | ALTO |
| 1.4 | **Eliminar modelos deprecated** de models/ | Ninguna | 1h | MEDIO |
| 1.5 | **Eliminar archivos huérfanos** (validation_report.json, retrain_report.json) | Ninguna | 1h | MEDIO |
| 1.6 | **Definir baseline naive** (Mean Predictor) | Ninguna | 2h | ALTO |
| 1.7 | **Comparar ElasticNet vs naive** | 1.6 | 2h | ALTO |
| 1.8 | **Validar features SAFE** (sin leakage) | Ninguna | 2h | ALTO |
| 1.9 | **Eliminar build_temporal_aggregate_features** del pipeline | 1.8 | 1h | ALTO |
| 1.10 | **Documentar PROHIBICIONES** en AGENTS.md | Ninguna | 1h | MEDIO |

**Entregable**: README.md limpio, baseline naive definido, comparación ElasticNet vs naive.

### Fase 2 — Modelo Estable — 1 semana

| # | Acción | Dependencia | Effort | Impacto |
|---|--------|-------------|--------|---------|
| 2.1 | **Reentrenar ElasticNet** con features SAFE (27 baseline) | 1.9 | 1h | ALTO |
| 2.2 | **Validar con TSCV 3-fold** | 2.1 | 1h | ALTO |
| 2.3 | **Validar con Rolling 3 windows** | 2.1 | 1h | ALTO |
| 2.4 | **Guardar modelo** con metadata completa | 2.1 | 1h | MEDIO |
| 2.5 | **Crear feature importance ranking** | 2.1 | 1h | MEDIO |
| 2.6 | **Documentar coefficients** en model card | 2.5 | 1h | MEDIO |
| 2.7 | **Eliminar features ~0** (arrival_day_of_week, total_nights, babies) | 2.5 | 1h | BAJO |
| 2.8 | **Comparar 27f vs 44f** (baseline vs engineered) | 2.1 | 2h | MEDIO |

**Entregable**: Modelo reentrenado, validado, documentado.

### Fase 3 — Producto Mínimo — 1 semana

| # | Acción | Dependencia | Effort | Impacto |
|---|--------|-------------|--------|---------|
| 3.1 | **Crear predicción CLI** | 2.1 | 2h | ALTO |
| 3.2 | **Crear predicción Streamlit básica** | 2.1 | 4h | ALTO |
| 3.3 | **Documentar output format** | 3.1 | 1h | MEDIO |
| 3.4 | **Agregar interpretabilidad** (coefficients visibles) | 2.5 | 2h | MEDIO |
| 3.5 | **Eliminar apps Streamlit complejas** (app_adm_1.py, etc.) | Ninguna | 1h | BAJO |
| 3.6 | **Crear AGENTS.md definitivo** | Todas | 2h | ALTO |

**Entregable**: Sistema funcional con output claro.

---

## 9. COSAS PROHIBIDAS EN V1

### 9.1 Prohibido por Arquitectura

| Prohibido | Razón |
|-----------|-------|
| Scraping OTA en tiempo real | OTAs son JS SPAs, no funciona |
| Dashboards complejos multiusuario | Complejidad innecesaria |
| LLM pipelines | No aporta al problema core |
| Sistemas de monitoreo avanzados | No hay drift detection |
| Optuna / tuning agresivo | El problema es el dataset, no los hiperparámetros |
| Arquitecturas distribuidas | Complejidad innecesaria |
| Simulaciones de competencia en tiempo real | No hay datos de competidores |
| PostgreSQL / FastAPI / Next.js | Stack incorrecto para V1 |
| WebSocket / real-time updates | No hay datos en tiempo real |
| Multi-tenant architecture | Un solo dataset |

### 9.2 Prohibido por Dataset

| Prohibido | Razón |
|-----------|-------|
| Features de ubicación | No hay datos en dataset |
| Features de marca/categoría | No hay datos en dataset |
| Features de competencia | No hay datos en dataset |
| Features de demanda real | No hay datos de occupancy |
| Features de weather/eventos | No hay datos externos |
| Rolling mean / lag features |usan target variable (leakage) |
| booking_velocity | Prediction-time unavailable |

### 9.3 Prohibido por Metodología

| Prohibido | Razón |
|-----------|-------|
| Random split (sin shuffle) | Datos temporales, shuffle rompe temporalidad |
| Métricas sin baseline naive | No hay referencia de comparación |
| R² sin contexto | R²=0.35 no es interpretable solo |
| Features sin validación de leakage | Sprint 6 mostró problemas |
| Entrenamiento sin reproducibility | Sin random_state, sin version logging |

---

## 10. RIESGOS SI NO SE SIMPLIFICA EL SISTEMA

### 10.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Consecuencia |
|--------|--------------|---------|--------------|
| **R²=0.35 insuficiente para producción** | ALTA | ALTO | Pricing recommendations son poco confiables |
| **Dataset insuficiente** | ALTA | ALTO | Modelo no generaliza a otros hoteles |
| **Leakage no detectado** | MEDIA | CRÍTICO | Métricas infladas, modelo inútil |
| **Código huérfano causa confusión** | ALTA | MEDIO | Desarrollador no sabe qué está activo |
| **Documentación desactualizada** | ALTA | MEDIO | Expectativas desalineadas con realidad |
| **Sin baseline naive** | MEDIA | ALTO | No se puede evaluar si el modelo es útil |

### 10.2 Riesgos de Producto

| Riesgo | Probabilidad | Impacto | Consecuencia |
|--------|--------------|---------|--------------|
| **Usuario espera "Revenue Intelligence"** | ALTA | ALTO | Expectativa vs realidad = frustración |
| **Output no es accionable** | ALTA | ALTO | Usuario no usa el sistema |
| **Sin interpretabilidad** | ALTA | MEDIO | Usuario no confía en predicciones |
| **Sin métricas de negocio** | ALTA | MEDIO | Usuario no puede evaluar valor |

### 10.3 Riesgos de Proyecto

| Riesgo | Probabilidad | Impacto | Consecuencia |
|--------|--------------|---------|--------------|
| **Scope creep** | ALTA | ALTO | Nunca se completa V1 |
| **Complejidad innecesaria** | ALTA | MEDIO | Desarrollo lento, bugs |
| **Stack incorrecto** | MEDIA | ALTO | Reescritura completa |
| **Sin Validación** | MEDIA | CRÍTICO | Modelo en producción sin validar |

---

## RESUMEN EJECUTIVO

### Estado Actual

| Dimensión | Estado | Acción |
|-----------|--------|--------|
| **Código core** | FUNCIONAL | Mantener training.py, feature_builder.py |
| **Dataset** | INSUFICIENTE | Aceptar limitations, trabajar con lo que hay |
| **Modelo** | ACEPTABLE para V1 | ElasticNet, R²=0.35, interpretable |
| **Validación** | CORRECTA | Temporal split + TSCV + Rolling |
| **Documentación** | DESACTUALIZADA | Reescribir README.md, AGENTS.md |
| **Producto** | MAL DEFINIDO | Cambiar de "Revenue Intelligence" a "Pricing Predictor" |
| **Código huérfano** | EXISTE | Eliminar enhanced_optimus.py, etc. |

### Veredicto

El proyecto tiene una base técnica sólida pero está **sobredimensionado** para lo que realmente hace.

**La prioridad #1 es simplificar**: eliminar código huérfano, reescribir documentación, definir baseline naive.

**La prioridad #2 es estabilizar**: reentrenar con features SAFE, validar correctamente, comparar con naive.

**La prioridad #3 es producir**: output claro, interpretabilidad, documentación consistente.

Todo lo demás (Next.js, FastAPI, PostgreSQL, RASPAL, WebSocket, etc.) es **prohibido en V1**.

---

*Generado por auditoría técnica. Última actualización: Junio 2026.*
