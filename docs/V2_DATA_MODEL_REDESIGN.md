# V2 DATA MODEL REDESIGN

**Date**: June 28, 2026
**Status**: Propuesta — requiere aprobación antes de implementar
**Principio**: "Construir algo que funcione con datos imperfectos, luego mejorar la calidad"

---

## 1. PROBLEMA ACTUAL

El modelo actual (`market_prices`) está diseñado para:
- Precios individuales por listing
- Scraping diario de OTAs
- Un listing = una propiedad en Booking/Airbnb

**Esto NO es viable** porque:
- Las OTAs no permiten scraping estable
- Los precios individuales son volátiles y dependen de la fuente
- No se puede garantizar cobertura suficiente por listing

---

## 2. NUEVO ENFOQUE: MARKET INDEX, NO PRECIOS INDIVIDUALES

### 2.1 Filosofía

En lugar de intentar capturar el precio de cada propiedad, construir **índices de mercado agregados** que representen la tendencia general del mercado.

**Analogía**: No necesitas saber el precio de cada casa en una zona para saber si los precios están subiendo o bajando. Un índice de zona te da esa información.

### 2.2 Modelo de Datos Rediseñado

```
┌─────────────────────────────────────────────────────────┐
│                    V2 DATA MODEL (REDESIGNED)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐     ┌─────────────────┐          │
│  │  market_index    │     │ price_bands     │          │
│  │  (por región)    │     │ (rangos)        │          │
│  └────────┬────────┘     └────────┬────────┘          │
│           │                        │                    │
│           ▼                        ▼                    │
│  ┌─────────────────┐     ┌─────────────────┐          │
│  │ demand_signals  │     │ seasonality     │          │
│  │ (proxy)         │     │ _index          │          │
│  └────────┬────────┘     └────────┬────────┘          │
│           │                        │                    │
│           ▼                        ▼                    │
│  ┌─────────────────────────────────────────┐          │
│  │           market_context                │          │
│  │  (vista unificada para el modelo V2)    │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. TABLAS PROPUESTAS

### 3.1 `market_index` — Índice de precios por región

```sql
CREATE TABLE market_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    index_date DATE NOT NULL,              -- Fecha del índice
    period TEXT NOT NULL,                  -- 'daily', 'weekly', 'monthly'
    
    -- Regional
    region TEXT NOT NULL,                  -- 'mallorca', 'costa_del_sol', etc.
    subregion TEXT,                        -- 'palma', 'alcudia', 'magaluf'
    segment TEXT NOT NULL,                 -- 'palma_urbano', 'playa_costa', etc.
    
    -- Accommodation filter
    accommodation_type TEXT,               -- 'hotel', 'apartment', 'villa', NULL=all
    
    -- Index values
    price_index REAL NOT NULL,             -- Índice normalizado (100=base)
    avg_price REAL,                        -- Precio promedio absoluto (EUR)
    median_price REAL,                     -- Mediana
    price_change_pct REAL,                 -- Cambio vs período anterior
    
    -- Confidence
    sample_size INTEGER NOT NULL,          -- Número de observaciones
    confidence_level TEXT,                 -- 'high', 'medium', 'low'
    
    -- Source
    source TEXT NOT NULL,                  -- 'ine', 'airbnb_api', 'manual', 'dataset'
    source_url TEXT,                       -- URL de la fuente
    data_freshness_days INTEGER,           -- Días desde que los datos son válidos
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(index_date, period, region, subregion, segment, accommodation_type)
);
```

### 3.2 `price_bands` — Bandas de precios por zona

```sql
CREATE TABLE price_bands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    band_date DATE NOT NULL,
    season TEXT NOT NULL,                  -- 'peak', 'high', 'shoulder', 'low'
    
    -- Regional
    region TEXT NOT NULL,
    subregion TEXT,
    segment TEXT NOT NULL,
    
    -- Price bands
    budget_max REAL,                       -- Límite superior del rango bajo
    mid_min REAL,                          -- Límite inferior del rango medio
    mid_max REAL,                          -- Límite superior del rango medio
    premium_min REAL,                      -- Límite inferior del rango alto
    
    -- Distribution
    budget_pct REAL,                       -- % de propiedades en rango bajo
    mid_pct REAL,                          -- % en rango medio
    premium_pct REAL,                      -- % en rango alto
    
    -- Source
    source TEXT NOT NULL,
    sample_size INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(band_date, season, region, subregion, segment)
);
```

### 3.3 `demand_signals` — Señales de demanda (proxy)

```sql
CREATE TABLE demand_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    signal_date DATE NOT NULL,
    
    -- Regional
    region TEXT NOT NULL,
    subregion TEXT,
    
    -- Demand indicators
    search_volume_index REAL,              -- Volumen de búsquedas (normalizado)
    booking_pace REAL,                     -- Velocidad de reservas (proxy)
    occupancy_estimate REAL,               -- Estimación de ocupación (%)
    event_impact REAL,                     -- Impacto de eventos locales
    
    -- Source
    source TEXT NOT NULL,                  -- 'google_trends', 'airdna', 'manual'
    source_metric TEXT,                    -- Nombre del metric en la fuente
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(signal_date, region, subregion, source)
);
```

### 3.4 `seasonality_index` — Índice de estacionalidad

```sql
CREATE TABLE seasonality_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal
    month INTEGER NOT NULL,                -- 1-12
    day_of_week INTEGER,                   -- 0-6 (NULL= todos)
    
    -- Regional
    region TEXT NOT NULL,
    segment TEXT NOT NULL,
    
    -- Seasonality values
    seasonality_factor REAL NOT NULL,      -- 1.0=normal, >1=peak, <1=low
    avg_occupancy REAL,                    -- Ocupación promedio histórica
    avg_price_index REAL,                  -- Índice de precios promedio
    
    -- Historical basis
    years_of_data INTEGER,                 -- Años de datos históricos
    data_sources TEXT,                     -- Fuentes utilizadas
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(month, day_of_week, region, segment)
);
```

### 3.5 `market_context` — Vista unificada (materializada o vista)

```sql
CREATE VIEW market_context AS
SELECT 
    mi.index_date,
    mi.region,
    mi.subregion,
    mi.segment,
    mi.price_index,
    mi.avg_price,
    mi.price_change_pct,
    pb.budget_max,
    pb.mid_min,
    pb.mid_max,
    pb.premium_min,
    ds.search_volume_index,
    ds.occupancy_estimate,
    si.seasonality_factor,
    mi.sample_size,
    mi.confidence_level
FROM market_index mi
LEFT JOIN price_bands pb ON 
    mi.index_date = pb.band_date 
    AND mi.region = pb.region 
    AND mi.segment = pb.segment
LEFT JOIN demand_signals ds ON 
    mi.index_date = ds.signal_date 
    AND mi.region = ds.region
LEFT JOIN seasonality_index si ON 
    EXTRACT(MONTH FROM mi.index_date) = si.month 
    AND mi.region = si.region 
    AND mi.segment = si.segment;
```

---

## 4. COMPARACIÓN: MODELO ACTUAL vs REDISEÑADO

| Aspecto | Actual (market_prices) | Rediseñado (market_index) |
|---------|----------------------|--------------------------|
| Granularidad | Listing individual | Región/zona |
| Frecuencia | Diaria (scraping) | Diaria/semanal/mensual |
| Fuente principal | Scraping OTAs | Multi-fuente (abierta + limitada) |
| Volatilidad | Alta (cambia por listing) | Baja (agregado estable) |
| Cobertura | Depende de scraping | Garantizable con datos abiertos |
| Mantenimiento | Alto (scraping continuo) | Bajo (actualización periódica) |
| Modelabilidad | Difícil (ruido por listing) | Más fácil (tendencias claras) |

---

## 5. FUENTES DE DATOS REALISTAS

### 5.1 Fuentes Abiertas (prioridad ALTA)

| Fuente | Tipo | Cobertura | Frecuencia | Acceso |
|--------|------|-----------|------------|--------|
| **INE (Instituto Nacional Estadística)** | Estadísticas turísticas | España | Mensual | CSV/API gratuita |
| **INE Tourist Accommodation Survey** | Ocupación, precios medios | Nacional/regional | Mensual | CSV |
| **Observatorio Turístico de Mallorca** | Demanda turística | Baleares | Trimestral | PDF/CSV |
| **Eurostat** | Turismo UE | Europa | Anual | API CSV |
| **AEMET** | Datos meteorológicos | España | Diaria | API gratuita |
| **Google Trends** | Interés en búsquedas | Global | Semanal | CSV export |
| **AirDNA** (parcial gratuito) | Mercado alquiler vacacional | Global | Mensual | API (limitada) |

### 5.2 Scraping Limitado (prioridad MEDIA)

| Fuente | Dificultad | Riesgo | Estrategia |
|--------|------------|--------|------------|
| **Airbnb (search results)** | MEDIA | Rate limiting | 100 requests/día, delay 5s |
| **Booking.com (listings)** | ALTA | Anti-bot agresivo | Solo names + prices, no deep scrape |
| **Google Hotels** | MEDIA | Cambios frecuentes | Fallback, no primary |

### 5.3 Datasets Históricos (prioridad MEDIA)

| Dataset | Source | Rows | Uso |
|---------|--------|------|-----|
| Hotel Booking Demand | Kaggle | 119K | V1 baseline (ya usado) |
| Airbnb Listings | Inside Airbnb | ~10K por ciudad | Precios históricos |
| Hotels.com Dataset | Kaggle | ~50K | Validación cruzada |

### 5.4 Datos del Usuario (prioridad ALTA)

| Tipo | Descripción | Implementación |
|------|-------------|----------------|
| **Upload CSV** | El usuario sube sus datos de competidores | Formulario en dashboard |
| **API manual** | El usuario ingresa precios de mercado | Input manual |
| **Conexión PMS** | Integración con sistema de gestión hotelera | Futuro |

---

## 6. ESTRATEGIA DE IMPLEMENTACIÓN

### 6.1 Fase 1: Datos Abiertos (2-3 semanas)

1. Descargar datos INE de turismo (gratis, CSV)
2. Crear pipeline de ingests para INE
3. Llenar `market_index` con datos históricos INE
4. Calcular `seasonality_index` con datos INE (5+ años)
5. Visualizar en dashboard

### 6.2 Fase 2: Scraping Limitado (2-3 semanas)

1. Implementar scraper Airbnb (rate-limited, 100/día)
2. Llenar `price_bands` con datos Airbnb
3. Agregar Google Trends como `demand_signals`
4. Validar calidad vs datos INE

### 6.3 Fase 3: Datos de Usuario (1-2 semanas)

1. Crear formulario de upload CSV
2. Parsear y validar datos del usuario
3. Merge con datos existentes
4. Actualizar market_index

### 6.4 Fase 4: Integración con V1 (1 semana)

1. Market context como input para predicciones V1
2. Ajuste de predicciones V1 por contexto de mercado
3. Dashboard unificado V1 + V2

---

## 7. MODELO V2: CÓMO APRENDERÍA

### 7.1 Input para el modelo V2

```python
# Features del mercado (de market_context)
market_features = {
    'price_index': 112.5,           # Índice de precios (+12.5% vs base)
    'price_change_pct': 3.2,        # Cambio reciente
    'occupancy_estimate': 0.78,     # Ocupación estimada
    'seasonality_factor': 1.35,     # Factor estacional (peak)
    'search_volume_index': 1.45,    # Interés en búsquedas
    'budget_max': 85,               # Límite rango bajo
    'premium_min': 250,             # Límite rango alto
}

# Features del hotel (del usuario o V1)
hotel_features = {
    'star_rating': 4,
    'property_type': 'hotel',
    'bedrooms': 20,
    'location_segment': 'playa_costa',
    'competitor_count': 15,
}

# Target: price_per_night (o revenue_per_room)
```

### 7.2 Output del modelo V2

```python
prediction = {
    'recommended_price': 145.0,
    'market_position': 'mid',           # 'budget', 'mid', 'premium'
    'confidence': 'high',
    'drivers': [
        'Market index +12.5% (strong demand)',
        'Seasonality factor 1.35 (peak season)',
        'Occupancy estimate 78% (healthy market)',
    ],
    'price_range': {
        'conservative': 130,
        'recommended': 145,
        'aggressive': 165,
    }
}
```

---

## 8. DECISIONES REQUERIDAS

| Decisión | Opciones | Recomendación |
|----------|----------|---------------|
| ¿Usar SQLite o PostgreSQL? | SQLite (actual) vs PostgreSQL | SQLite para MVP, migrar después |
| ¿Vista materializada o query on-demand? | View vs table | Vista para simplicidad |
| ¿Frecuencia de actualización? | Diaria vs semanal vs mensual | Semanal para datos abiertos |
| ¿Quién llena los datos? | Automático vs manual vs híbrido | Híbrido (automático + upload) |
| ¿Mantener market_prices? | Eliminar vs mantener como raw | Mantener como tabla raw auxiliar |

---

*Este documento es una propuesta. Requiere aprobación antes de implementar.*
