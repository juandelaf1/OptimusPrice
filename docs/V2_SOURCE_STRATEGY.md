# V2 SOURCE STRATEGY

**Date**: June 28, 2026
**Status**: Propuesta — requiere aprobación
**Principio**: "Multi-fuente y resiliente, no dependiente de una sola plataforma"

---

## 1. ANÁLISIS DE FUENTES

### 1.1 Fuentes Evaluadas

| Fuente | Tipo | Datos | Calendario | Accesibilidad | Coste | Veredicto |
|--------|------|-------|------------|---------------|-------|-----------|
| **INE Tourist Survey** | Pública | Ocupación, precios, demanda | Mensual/anual | CSV gratuito | Gratis | ✅ PRIMARIA |
| **INE Tourist Accommodation** | Pública | Establecimientos, plazas | Anual | CSV gratuito | Gratis | ✅ PRIMARIA |
| **Observatorio Turismo Baleares** | Pública | Demanda, tendencias | Trimestral | PDF/CSV | Gratis | ✅ SECUNDARIA |
| **Google Trends** | Pública | Interés búsquedas | Semanal | CSV export | Gratis | ✅ SECUNDARIA |
| **AEMET** | Pública | Meteorología | Diaria | API gratuita | Gratis | ✅ COMPLEMENTARIA |
| **Eurostat** | Pública | Turismo UE | Anual | API/CSV | Gratis | ⚠️ Muy agregada |
| **Airbnb (search)** | Limitada | Precios listing | On-demand | Scraping limitado | Bajo | ⚠️ AUXILIAR |
| **AirDNA** | Comercial | Mercado alquiler | Mensual | API limitada | Medio | ⚠️ AUXILIAR |
| **Booking.com** | Restringida | Precios | On-demand | Scraping agresivo | Alto | ❌ NO FIABLE |
| **Expedia** | Restringida | Precios | On-demand | HTTP 429 | Alto | ❌ NO FIABLE |
| **Datos usuario** | Manual | Competidores | Manual | Upload CSV | Gratis | ✅ VALIOSA |

### 1.2 Clasificación por Fiabilidad

```
FIABILIDAD ALTA (datos verificados, públicos)
├── INE Tourist Survey (40+ años de datos)
├── INE Tourist Accommodation (datos oficiales)
├── AEMET (datos meteorológicos verificados)
└── Google Trends (datos de tendencia estables)

FIABILIDAD MEDIA ( datos reales pero limitados)
├── Observatorio Turismo Baleares (trimestral)
├── Eurostat (anual, muy agregado)
├── Airbnb search (volátil pero real)
└── AirDNA (comercial, limitado)

FIABILIDAD BAJA ( scraping inestable)
├── Booking.com (anti-bot agresivo)
├── Expedia (HTTP 429 frecuente)
└── Hotels.com (scraping no probado)
```

---

## 2. ESTRATEGIA POR TIPO DE DATO

### 2.1 Precios de Mercado

| Fuente | Método | Cobertura | Actualización |
|--------|--------|-----------|---------------|
| INE Tourist Survey | CSV download | Nacional/regional | Trimestral |
| Airbnb search (limitado) | Scraping 100/día | Por zona | Semanal |
| Upload CSV (usuario) | Manual | Por hotel | Manual |
| Inside Airbnb Dataset | Download anual | Ciudades | Anual |

**Resultado esperado**: Precio medio por zona, rango de precios, distribución.

### 2.2 Ocupación / Demanda

| Fuente | Método | Cobertura | Actualización |
|--------|--------|-----------|---------------|
| INE Tourist Accommodation | CSV download | Nacional/regional | Anual |
| Google Trends | CSV export | Por query | Semanal |
| AEMET (proxy: weather) | API | Nacional | Diaria |
| Eventos locales (manual) | Input manual | Por evento | Cuando ocurra |

**Resultado esperado**: Estimación de ocupación, tendencia de demanda, impacto estacional.

### 2.3 Tendencias / Estacionalidad

| Fuente | Método | Cobertura | Actualización |
|--------|--------|-----------|---------------|
| INE histórico (5+ años) | CSV download | Nacional | Anual |
| Google Trends | CSV export | Global | Semanal |
| Datos del usuario | Upload | Por hotel | Manual |

**Resultado esperado**: Índice de estacionalidad, factores de demanda, tendencias.

### 2.4 Competidores / Benchmarking

| Fuente | Método | Cobertura | Actualización |
|--------|--------|-----------|---------------|
| Datos del usuario | Upload CSV | Por hotel | Manual |
| Airbnb search (limitado) | Scraping | Por zona | Semanal |
| Booking.com (nombres) | Búsqueda manual | Por zona | Mensual |

**Resultado esperado**: Posicionamiento relativo, comparación de segmentos.

---

## 3. PIPELINE DE RECOLECCIÓN

### 3.1 Fuentes Automáticas

```
┌──────────────────────────────────────────────────────┐
│              FUENTES AUTOMÁTICAS                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  INE Stats  │───▶│  CSV Parser │───▶ market_   │
│  │  (trimestral)│    │             │    index      │
│  └─────────────┘    └─────────────┘                │
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  Google     │───▶│  Trends     │───▶ demand_   │
│  │  Trends     │    │  Parser     │    signals    │
│  └─────────────┘    └─────────────┘                │
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  AEMET      │───▶│  Weather    │───▶ demand_   │
│  │  API        │    │  Aggregator │    signals    │
│  └─────────────┘    └─────────────┘                │
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  Airbnb     │───▶│  Scraper    │───▶ price_    │
│  │  (limitado) │    │  (100/día)  │    bands      │
│  └─────────────┘    └─────────────┘                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 3.2 Fuentes Manuales

```
┌──────────────────────────────────────────────────────┐
│              FUENTES MANUALES                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  Upload CSV │───▶│  Validator  │───▶ market_   │
│  │  (usuario)  │    │             │    index      │
│  └─────────────┘    └─────────────┘                │
│                                                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │  Input Form │───▶│  Parser     │───▶ demand_   │
│  │  (manual)   │    │             │    signals    │
│  └─────────────┘    └─────────────┘                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 3.3 Frecuencia de Actualización

| Fuente | Frecuencia | Horario | Responsable |
|--------|------------|---------|-------------|
| INE Tourist Survey | Trimestral | Publicación INE | Automático |
| Google Trends | Semanal | Lunes 06:00 | Automático |
| AEMET | Diaria | 08:00 | Automático |
| Airbnb scraping | Semanal | Domingo 02:00 | Automático |
| Upload usuario | On-demand | Cuando el usuario suba | Manual |
| Inside Airbnb | Anual | Publicación dataset | Manual |

---

## 4. IMPLEMENTACIÓN POR FASE

### 4.1 Fase 1: Datos Abiertos (Semanas 1-3)

**Objetivo**: Llenar `market_index` con datos reales de INE

| Tarea | Esfuerzo | Dependencia |
|-------|----------|-------------|
| Descargar CSVs INE turismo (2015-2025) | 1 día | Ninguna |
| Crear parser para formatos INE | 2 días | CSV descargado |
| Llenar `market_index` con datos INE | 1 día | Parser |
| Crear `seasonality_index` con 5+ años | 1 día | market_index |
| Calcular `price_bands` por región | 1 día | market_index |
| Dashboard básico con datos INE | 2 días | Todas |

**Resultado**: Dashboard con 10+ años de datos turísticos de España/Mallorca.

### 4.2 Fase 2: Señales de Demanda (Semanas 3-5)

**Objetivo**: Agregar `demand_signals` con Google Trends + AEMET

| Tarea | Esfuerzo | Dependencia |
|-------|----------|-------------|
| Configurar Google Trends export | 1 día | Ninguna |
| Crear parser Google Trends | 1 día | Export |
| Integrar AEMET API | 2 días | API key |
| Llenar demand_signals | 1 día | Parsers |
| Calcular correlación demanda-precios | 1 día | demand_signals |

**Resultado**: Señales de demanda en tiempo casi-real.

### 4.3 Fase 3: Scraping Limitado (Semanas 5-7)

**Objetivo**: Agregar `price_bands` con datos Airbnb

| Tarea | Esfuerzo | Dependencia |
|-------|----------|-------------|
| Implementar scraper Airbnb (rate-limited) | 3 días | Ninguna |
| Configurar 100 requests/día, delay 5s | 0.5 días | Scraper |
| Llenar price_bands por zona | 2 días | Scraper |
| Validar calidad vs INE | 1 día | price_bands |
| Monitorear rate limits | Continuo | Infraestructura |

**Resultado**: Precios actuales de Airbnb por zona de Mallorca.

### 4.4 Fase 4: Datos de Usuario (Semanas 7-8)

**Objetivo**: Permitir que el usuario suba sus datos

| Tarea | Esfuerzo | Dependencia |
|-------|----------|-------------|
| Crear formulario upload CSV | 2 días | Frontend |
| Crear parser CSV flexible | 1 día | Formulario |
| Validar y merge con datos existentes | 1 día | Parser |
| Dashboard con datos propios | 1 día | Merge |

**Resultado**: El usuario puede ver sus datos junto a datos de mercado.

---

## 5. VALIDACIÓN DE CALIDAD

### 5.1 Reglas de Calidad por Fuente

| Fuente | Regla | Acción si falla |
|--------|-------|-----------------|
| INE | Formato CSV válido, columnas esperadas | Rechazar lote |
| Google Trends | Valores 0-100, fechas válidas | Interpolar |
| AEMET | Temperatura -20 a 50°C, precipitación ≥0 | Usar última válida |
| Airbnb | Precio >0, ubicación en Mallorca | Descartar listing |
| Upload usuario | Columnas requeridas, precio >0 | Mostrar error |

### 5.2 Métricas de Calidad

| Métrica | Target | Medición |
|---------|--------|----------|
| Completitud | >90% campos no nulos | Por batch |
| Consistencia | <5% valores fuera de rango | Por batch |
| Freshness | <30 días desde captura | Por registro |
| Cobertura | >3 regiones con datos | Por fecha |
| Concordancia | <10% desviación entre fuentes | Cross-validation |

---

## 6. COSTE OPERATIVO

### 6.1 Costes Fijos

| Componente | Coste | Frecuencia |
|------------|-------|------------|
| INE data | Gratis | Trimestral |
| Google Trends | Gratis | Semanal |
| AEMET API | Gratis (<1M requests) | Diaria |
| Hosting DB | ~5€/mes | Mensual |
| **Total fijo** | **~5€/mes** | |

### 6.2 Costes Variables

| Componente | Coste | Condiciones |
|------------|-------|-------------|
| Airbnb scraping | Gratis (rate-limited) | <100 requests/día |
| AirDNA API | ~50€/mes | Si se necesita |
| **Total variable** | **0-50€/mes** | |

### 6.3 Comparativa con Scraping Masivo

| Enfoque | Coste mensual | Fiabilidad | Mantenimiento |
|---------|---------------|------------|---------------|
| Scraping Booking.com | ~200€ (proxies + LLM) | Baja (anti-bot) | Alto |
| Scraping Airbnb | ~50€ (proxies) | Media (rate limits) | Medio |
| **Multi-fuente abierta** | **~5€** | **Alta** | **Bajo** |
| **Recomendado** | **~5-50€** | **Alta** | **Bajo** | |

---

## 7. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Airbnb bloquea scraping | Alta | Medio | Usar Inside Airbnb dataset como fallback |
| INE cambia formato CSV | Baja | Bajo | Versionar parsers |
| Google Trends API cambia | Media | Bajo | Usar export manual |
| Datos insuficientes para modelo | Media | Alto | Usar datos agregados nacionales |
| Mercado Mallorca muy pequeño | Baja | Medio | Expandir a Baleares |

---

## 8. MÉTRICAS DE ÉXITO

### 8.1 Fase 1 (Datos Abiertos)

| Métrica | Target |
|---------|--------|
| Registros en market_index | >1000 |
| Cobertura temporal | >5 años |
| Regiones cubiertas | >3 |
| Fuentes integradas | >2 |

### 8.2 Fase 2 (Señales Demanda)

| Métrica | Target |
|---------|--------|
| demand_signals records | >500 |
| Fuentes de demanda | >2 |
| Correlación demanda-precios | >0.3 |

### 8.3 Fase 3 (Scraping Limitado)

| Métrica | Target |
|---------|--------|
| price_bands records | >100 |
| Zonas con datos actuales | >3 |
| Rate limit violations | 0 |

### 8.4 Fase 4 (Datos Usuario)

| Métrica | Target |
|---------|--------|
| Uploads exitosos | >10 |
|.merge con datos existentes | Exitoso |
| Dashboard funcional | Sí |

---

*Este documento es una propuesta. Requiere aprobación antes de implementar.*
