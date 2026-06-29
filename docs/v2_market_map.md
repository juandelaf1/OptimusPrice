# V2 MARKET MAP — Mallorca Segmentation

**Version**: 1.0
**Status**: ACTIVE
**Last Updated**: June 2026

---

## 1. Overview

Mallorca is segmented into 6 distinct market clusters based on:
- Tourist profile
- Property type mix
- Price range
- Seasonality patterns
- OTA dependency

---

## 2. Market Segments

### 2.1 PALMA URBANO

| Attribute | Value |
|-----------|-------|
| **Code** | `palma_urbano` |
| **Profile** | Urban tourism, business travelers, cultural visitors |
| **Property Mix** | 60% hotels (3-4★), 30% apartments, 10% boutique |
| **Price Range** | €80 — €250/night |
| **Peak Season** | Jun-Sep (summer), Nov-Dec (Christmas markets) |
| **Low Season** | Jan-Feb |
| **OTA Dependency** | HIGH (85%+ bookings via OTAs) |
| **Key Areas** | Casco Antiguo, El Terreno, Paseo Marítimo, Santa Catalina |
| **Demand Type** | Year-round with summer peak |
| **Typical Stay** | 3-5 nights |
| **Booking Window** | 14-60 days |

### 2.2 PLAYA COSTA TURÍSTICA

| Attribute | Value |
|-----------|-------|
| **Code** | `playa_costa` |
| **Profile** | Beach resorts, family vacations, sun & beach |
| **Property Mix** | 70% hotels (3-5★), 20% apartments, 10% villas |
| **Price Range** | €100 — €400/night |
| **Peak Season** | Jun-Sep (beach season) |
| **Low Season** | Nov-Mar |
| **OTA Dependency** | VERY HIGH (90%+ bookings via OTAs) |
| **Key Areas** | Playa de Palma, Can Pastilla, S'Arenal, Cala Major |
| **Demand Type** | Strong seasonal (summer dominant) |
| **Typical Stay** | 7-14 nights |
| **Booking Window** | 30-120 days |

### 2.3 MAGALUF / PALMANOVA

| Attribute | Value |
|-----------|-------|
| **Code** | `magaluf_party` |
| **Profile** | Party tourism, young adults, nightlife |
| **Property Mix** | 50% hotels (2-3★), 40% apartments, 10% hostels |
| **Price Range** | €40 — €180/night |
| **Peak Season** | May-Oct (party season) |
| **Low Season** | Nov-Apr |
| **OTA Dependency** | HIGH (80%+ bookings via OTAs) |
| **Key Areas** | Magaluf, Palmanova, Santa Ponsa |
| **Demand Type** | Strong seasonal (May-Oct) |
| **Typical Stay** | 3-7 nights |
| **Booking Window** | 7-45 days |

### 2.4 ALCUDIA / POLLENSA

| Attribute | Value |
|-----------|-------|
| **Code** | `alcudia_family` |
| **Profile** | Family vacations, mid-range resorts, cultural tourism |
| **Property Mix** | 55% hotels (3-4★), 30% apartments, 15% villas |
| **Price Range** | €90 — €300/night |
| **Peak Season** | Jun-Sep (family summer) |
| **Low Season** | Nov-Mar |
| **OTA Dependency** | HIGH (85%+ bookings via OTAs) |
| **Key Areas** | Alcudia, Puerto Alcudia, Pollensa, Cala San Vicente |
| **Demand Type** | Strong seasonal (family summer) |
| **Typical Stay** | 7-14 nights |
| **Booking Window** | 30-120 days |

### 2.5 INTERIOR RURAL (AGROTURISMO)

| Attribute | Value |
|-----------|-------|
| **Code** | `interior_rural` |
| **Profile** | Rural tourism, agroturism, nature lovers, luxury retreats |
| **Property Mix** | 80% rural hotels/agroturismos, 15% villas, 5% apartments |
| **Price Range** | €120 — €500/night |
| **Peak Season** | Apr-Oct (extended season) |
| **Low Season** | Nov-Mar (but less dramatic drop) |
| **OTA Dependency** | MEDIUM (60% OTAs, 40% direct) |
| **Key Areas** | Sóller, Deià, Valldemossa, Binissalem, Santa Maria |
| **Demand Type** | Extended season (spring-fall) |
| **Typical Stay** | 4-7 nights |
| **Booking Window** | 21-90 days |

### 2.6 LUXURY VILLAS (HIGH-END)

| Attribute | Value |
|-----------|-------|
| **Code** | `luxury_villas` |
| **Profile** | High-end travelers, luxury villas, private experiences |
| **Property Mix** | 90% villas, 5% luxury hotels, 5% fincas |
| **Price Range** | €300 — €1500/night |
| **Peak Season** | May-Sep (luxury summer) |
| **Low Season** | Nov-Mar |
| **OTA Dependency** | LOW (40% OTAs, 60% direct/brokers) |
| **Key Areas** | Andratx, Calvià, Son Vida, Costa de la Calma, Es Capdellà |
| **Demand Type** | Seasonal but high-value |
| **Typical Stay** | 7-21 nights |
| **Booking Window** | 30-180 days |

---

## 3. Segment Summary

| Segment | Code | Price Range | Peak | OTA Dep. | Target Listings |
|---------|------|-------------|------|----------|-----------------|
| Palma Urbano | `palma_urbano` | €80-250 | Jun-Sep | HIGH | 200 |
| Playa Costa | `playa_costa` | €100-400 | Jun-Sep | VERY HIGH | 200 |
| Magaluf Party | `magaluf_party` | €40-180 | May-Oct | HIGH | 150 |
| Alcudia Family | `alcudia_family` | €90-300 | Jun-Sep | HIGH | 200 |
| Interior Rural | `interior_rural` | €120-500 | Apr-Oct | MEDIUM | 100 |
| Luxury Villas | `luxury_villas` | €300-1500 | May-Sep | LOW | 100 |
| **TOTAL** | | | | | **950** |

---

## 4. Scraping Priority by Segment

| Priority | Segment | Rationale |
|----------|---------|-----------|
| 1 | `playa_costa` | Highest OTA density, easiest to scrape |
| 2 | `alcudia_family` | High OTA density, family segment |
| 3 | `palma_urbano` | Year-round data, urban hotels |
| 4 | `magaluf_party` | Distinct seasonal pattern |
| 5 | `interior_rural` | Lower OTA dependency, harder |
| 6 | `luxury_villas` | Lowest OTA dependency, highest value |

---

## 5. Data Collection Strategy by Segment

### 5.1 Playa Costa (Priority 1)

| Source | Target | Method |
|--------|--------|--------|
| Booking.com | 150 hotels | Search: "Mallorca beach hotels" |
| Airbnb | 50 apartments | Search: "Playa de Palma" |
| **Total** | **200 listings** | |

### 5.2 Alcudia Family (Priority 2)

| Source | Target | Method |
|--------|--------|--------|
| Booking.com | 150 hotels | Search: "Alcudia hotels" |
| Airbnb | 50 apartments | Search: "Alcudia apartments" |
| **Total** | **200 listings** | |

### 5.3 Palma Urbano (Priority 3)

| Source | Target | Method |
|--------|--------|--------|
| Booking.com | 150 hotels | Search: "Palma de Mallorca hotels" |
| Airbnb | 50 apartments | Search: "Palma apartments" |
| **Total** | **200 listings** | |

---

## 6. Seasonality Calendar

```
MONTH    | PALMA | PLAYA | MAGALUF | ALCUDIA | RURAL | LUXURY
---------|-------|-------|---------|---------|-------|-------
January  |  LOW  |  VLOW |   VLOW  |   VLOW  |  LOW  |  LOW
February |  LOW  |  VLOW |   VLOW  |   VLOW  |  LOW  |  LOW
March    |  MED  |  LOW  |   LOW   |   LOW   |  MED  |  LOW
April    |  MED  |  MED  |   MED   |   MED   |  HIGH |  MED
May      |  HIGH |  HIGH |   HIGH  |   HIGH  |  HIGH |  HIGH
June     |  HIGH |  VHIGH|   VHIGH |   VHIGH |  HIGH |  VHIGH
July     |  VHIGH|  PEAK |   PEAK  |   PEAK  |  VHIGH|  PEAK
August   |  VHIGH|  PEAK |   PEAK  |   PEAK  |  VHIGH|  PEAK
September|  HIGH |  HIGH |   HIGH  |   HIGH  |  HIGH |  HIGH
October  |  MED  |  MED  |   MED   |   MED   |  MED  |  MED
November |  MED  |  LOW  |   LOW   |   LOW   |  LOW  |  LOW
December |  MED  |  LOW  |   LOW   |   LOW   |  LOW  |  LOW
```

---

## 7. Geographic Coordinates (for scraping)

| Segment | Center Lat | Center Lng | Radius (km) |
|---------|------------|------------|-------------|
| `palma_urbano` | 39.5696 | 2.6502 | 5 |
| `playa_costa` | 39.5000 | 2.8000 | 15 |
| `magaluf_party` | 39.5089 | 2.4447 | 5 |
| `alcudia_family` | 39.8266 | 3.1215 | 10 |
| `interior_rural` | 39.7000 | 2.9000 | 20 |
| `luxury_villas` | 39.5500 | 2.4500 | 15 |

---

*This market map defines the V2 data collection segments. Scraping is segment-aware.*
