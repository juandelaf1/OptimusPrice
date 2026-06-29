# V2 REALITY ASSESSMENT

**Date**: June 28, 2026
**Status**: Auditoría completa — sin cambios al código
**Author**: Arquitecto Principal

---

## 1. VEREDICTO EJECUTIVO

**V2 está al 25% de madurez.** La infraestructura base funciona (esquema DB, ingester, validador, agregador), pero la capa crítica de recolección de datos está completamente rota. No existe ni un solo registro real de datos de mercado de Mallorca.

| Área | Madurez | Estado |
|------|---------|--------|
| Esquema de base de datos | 90% | Funcional, 6 registros test |
| Ingestión (ingester.py) | 85% | Funcional, validación por segmento |
| Validación (validator.py) | 80% | Funcional, reglas de calidad implementadas |
| Agregación (aggregator.py) | 70% | Funcional, nunca ejecutado con datos reales |
| Scraping / collectors | 5% | Roto — raspal no declarado, resultados vacíos |
| Feature enricher | 30% | Diseño correcto, sin datos de entrada |
| Modelos V2 (occupancy, elasticity, revenue) | 40% | Funcionan con datos Kaggle, no con datos reales |
| Tests automatizados | 0% | No existen tests V2 |
| **OVERALL** | **~25%** | |

---

## 2. INVENTARIO COMPLETO

### 2.1 Lo que FUNCIONA

| Componente | Archivo | Líneas | Estado |
|------------|---------|--------|--------|
| MarketDatabase | `src/v2_pipeline/ingester.py` | 317 | ✅ Funcional |
| MarketDataValidator | `src/v2_pipeline/validator.py` | 141 | ✅ Funcional |
| MarketAggregator | `src/v2_pipeline/aggregator.py` | 206 | ✅ Funcional |
| Esquema DB (2 tablas, 5 índices) | `ingester.py` SCHEMA_SQL | — | ✅ Production-ready |
| Segments (6 válidos) | `ingester.py` VALID_SEGMENTS | — | ✅ Configurados |
| OccupancyPredictor | `src/optimus_price/occupancy_model.py` | 415 | ⚠️ Datos Kaggle |
| PriceElasticityEngine | `src/optimus_price/elasticity_engine.py` | 485 | ⚠️ Cascada Kaggle |
| RevenueOptimizer | `src/optimus_price/revenue_optimizer.py` | 331 | ⚠️ Cascada Kaggle |
| FeatureEnricher | `feature_enricher.py` | 272 | ⚠️ Sin datos de entrada |

### 2.2 Lo que está ROTO

| Componente | Archivo | Problema |
|------------|---------|----------|
| EnhancedOptimusPrice | `enhanced_optimus.py` | Import de `raspal` falla al cargar módulo |
| ScrapingManager | `scraping_manager.py` | `raspal` no en requirements.txt, paths hardcodeados |
| OTAPriceComparator | `competitor_monitor.py` | Depende de scraping roto + `schedule` no instalado |
| MonitoringService | `monitoring_service.py` | Depende de scraping roto + `schedule` no instalado |
| v2_daily_scrape.py | (no existe) | Referenciado en docs pero nunca creado |
| scraper.py (v2_pipeline) | (no existe) | Referenciado en docs pero nunca creado |
| backfill.py (v2_pipeline) | (no existe) | Referenciado en docs pero nunca creado |

### 2.3 Lo que NO EXISTE

| Componente | Evidence |
|------------|----------|
| Directorio `data/v2_market/raw/` | No creado |
| Datos reales de Mallorca | DB tiene 6 registros test, 0 reales |
| Datos de competidores reales | JSONs de scrape tienen `parsed: {}` en los 12 intentos |
| `market_aggregates` con datos | Tabla existe, 0 filas |
| Tests automatizados V2 | Solo `tests/test_imports.py` (3 trivial tests V1) |
| `raspal` en requirements.txt | Dependencia crítica no declarada |
| Config Airbnb | Referenciada en v2_scraping.yaml, no existe archivo YAML |
| Orquestación (Airflow, cron, etc.) | No existe programador de tareas |

---

## 3. ANÁLISIS DE DEPENDENCIAS

### 3.1 Cadena de dependencias V2 (actual)

```
v2_scraping.yaml  ──────(nunca leído por código)──────► NADA
                               │
enhanced_optimus.py ────(import raspal)────► RASPAL (no instalado)
       │                                         │
       │                                    OTAs JS SPA
       │                                         │
       │                                    HTTP 429 / parsed: {}
       │                                         │
       ▼                                         ▼
feature_enricher.py ◄──── (sin datos) ◄── scraped/*.json (vacíos)
       │
       │ (sin features de competidores generadas)
       ▼
Modelos V2 (occupancy → elasticity → revenue)
       │
       │ (entrenados con Kaggle, no datos reales)
       ▼
Revenue Intelligence (no funcional)
```

### 3.2 Cadena de dependencias V2 (diseñada)

```
OTAs (Booking, Airbnb, Expedia)
       │
       ▼
Scraper (RASPAL) ──► raw/*.csv
       │
       ▼
Validator ──► market_prices.db
       │
       ▼
Aggregator ──► market_aggregates
       │
       ▼
Feature Enricher ──► enriched dataset
       │
       ▼
V2 Model Training ──► V2 model
       │
       ▼
Revenue Optimization
```

### 3.3 Lo que bloquea el camino

| Bloqueo | Impacto | Solución |
|---------|---------|----------|
| `raspal` no instalado | No funciona enhanced_optimus.py ni scraping_manager.py | Instalar o reemplazar |
| OTAs son JS SPA | Scraping tradicional no extrae datos | Usar fuentes alternativas |
| Sin datos reales de Mallorca | Modelos V2 no son entrenables | Recolección multi-fuente |
| Paths hardcodeados Windows | No portable | Usar rutas relativas |
| Sin tests V2 | No hay validación de regresión | Crear tests mínimos |

---

## 4. ANÁLISIS DE VIABILIDAD

### 4.1 Componente: MarketDatabase + Ingestion

**Veredicto: VIABLE ✅**

El esquema está bien diseñado. Soporta segmentación por 6 zonas, tiene índices correctos, la ingester valida segmentos, y el batch insert funciona. Solo necesita datos reales para llenarse.

### 4.2 Componente: Scraping OTA (Booking, Airbnb)

**Veredicto: NO VIABLE como fuente principal ❌**

Evidencia:
- Los 12 intentos de scrape en `real_data_20260626_191636.json` devolvieron `parsed: {}`
- Expedia devolvió HTTP 429 (rate limit)
- Las OTAs son SPAs JavaScript, el scraping estático no funciona
- RASPAL con LLM extraction no logró parsear los datos
- Booking.com y Airbnb tienen protección anti-bot agresiva

**Conclusión**: El scraping OTA es una señal auxiliar, NO la base del sistema.

### 4.3 Componente: Feature Enricher (competitor features)

**Veredicto: VIABLE SI hay datos de entrada ⚠️**

El diseño es correcto: extrae estadísticas de precios de competidores por fecha, sin leakage del target. Pero necesita CSVs con columnas `hotel_id, ota, price, check_in_date` en `data/scraped/`. Actualmente no hay ninguno.

### 4.4 Componente: Occupancy/Elasticity/Revenue Models

**Veredicto: ARQUITECTURA VÁLIDA, DATOS INVÁLIDOS ⚠️**

Los módulos están bien escritos matemáticamente. El occupancy model usa CalibratedClassifierCV para probabilidades calibradas. El elasticity engine implementa point y arc elasticity correctamente. El revenue optimizer combina ambos para encontrar óptimos.

PROBLEMA: Todos están entrenados con datos Kaggle (hotel bookings 2015-2017), que no representan el mercado de Mallorca 2024-2026.

### 4.5 Componente: enhanced_optimus.py + scraping_manager.py

**Veredicto: MUERTO, NO REPARABLE en su forma actual ❌**

- Import-level dependency en `raspal` (falla al cargar el módulo)
- Paths hardcodeados a `C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final`
- `_train()` es un stub
- `_process_web_training_data()` retorna `[]`
- `predict_with_market_context()` no aplica ajuste de mercado

**Recomendación**: No reparar. Reescribir con enfoque multi-fuente.

---

## 5. BRECHA ENTRE DOCS Y REALIDAD

| Documento | Lo que dice | Realidad |
|-----------|-------------|----------|
| `V2_DATA_SPEC.md` | Pipeline con scraper.py, backfill.py | No existen |
| `v2_readiness_checklist.md` | 69% completo | 25% real |
| `v2_scraping.yaml` | Config con segmentos y rate limits | Ningún código lo lee |
| `AGENTS.md` | "V2 data pipeline scaffolded" | Esquema funciona, datos vacíos |
| `benchmark_v2.md` | R²=0.5884 con 55 features | Features de target leakage |
| `roadmap.md` | V2 phases defined | Sin datos, no avanzable |

---

## 6. QUÉ NO HACER

| Acción | Razón |
|--------|-------|
| Reparar `enhanced_optimus.py` | Depende de raspal y scraping roto |
| Reparar `scraping_manager.py` | Mismo problema |
| Crear `v2_daily_scrape.py` | Sin scraping funcional, no tiene sentido |
| Crear `backfill.py` | No hay fuente de datos para backfill |
| Entrenar modelos V2 con datos actuales | Solo hay 6 registros test |
| Añadir más features engineered | Ya hay target leakage identificado |
| Implementar FastAPI / Next.js | Prematuro, sin datos |
| Crear orquestación (Airflow) | Sin pipeline funcional |

---

## 7. QUÉ SÍ HACER

| Acción | Prioridad | Esfuerzo |
|--------|-----------|----------|
| Definir fuentes de datos realistas (no-OTA) | ALTA | Bajo |
| Rediseñar data model V2 (market_index, no precios individuales) | ALTA | Medio |
| Crear estrategia de datos abiertos (INE, turismo, etc.) | ALTA | Bajo |
| Evaluar datasets históricos adicionales | MEDIA | Bajo |
| Crear tests mínimos para pipeline V2 | MEDIA | Bajo |
| Limpiar código muerto (enhanced_optimus, scraping_manager) | BAJA | Bajo |
| Separar claramente V1 vs V2 en docs | ALTA | Bajo |

---

## 8. RESUMEN PARA DECISIONES

**Pregunta clave**: ¿Se puede construir V2 con datos reales?

**Respuesta**: Sí, PERO no con la estrategia actual de scraping OTA.

**Alternativas realistas**:
1. **Datasets abiertos turísticos** — INE, observatorios turísticos, datos públicos de demanda
2. **Airbnb (limitado)** — Menos agresivo que Booking, possível con rate limiting cuidadoso
3. **Datos históricos adicionales** — Kaggle tiene más datasets de hospitalidad
4. **Simulación controlada** — Para validar arquitectura antes de datos reales
5. **Datos proporcionados por el usuario** — Los hoteles pueden subir sus propios datos de competidores

**La estrategia correcta V2 NO es scraping masivo. Es multi-fuente con énfasis en inteligencia de mercado, no en precios individuales.**

---

*Documento generado como parte de la auditoría V2. No se modificó ningún archivo de código.*
