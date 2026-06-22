# OPTIMUS PRICE — Product Specification v2.0

## Stack
```
Frontend:  Next.js 14+ (App Router, TypeScript)
Styling:   Tailwind CSS + shadcn/ui
Charts:    Recharts
Backend:   FastAPI (Python 3.11+)
DB:        PostgreSQL
Real-time: WebSocket (via FastAPI WebSockets / Socket.io)
Scraping:  RASPAL (worker independiente)
ML:        Código existente (src/optimus_price/)
Deploy:    Docker Compose → Vercel (FE) + Railway/Fly.io (BE)
```

---

## 1. Architecture

```
┌─────────────────────────────────────────────────┐
│                   Browser                        │
│  ┌───────────────────────────────────────────┐  │
│  │        Next.js 14 App (RSC)               │  │
│  │  ┌─────┐ ┌──────┐ ┌──────┐ ┌──────────┐ │  │
│  │  │Dash │ │Monitor│ │Admin │ │ Settings │ │  │
│  │  └─────┘ └──────┘ └──────┘ └──────────┘ │  │
│  └───────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / WebSocket
                       ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                      │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ REST API │ │WebSocket │ │ ML Engine      │  │
│  │ /api/v1  │ │ /ws/*    │ │ (Python exist.)│  │
│  └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Auth JWT │ │PostgreSQL│ │ RASPAL Worker  │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 2. User Personas

### 2.1 Hotel Manager (Admin)
- Objetivo: Maximizar revenue, monitorizar competencia, ajustar precios
- Funcionalidad: Dashboard KPIs, override precios, ver actividad clientes, alerts
- Frecuencia: Diario / varias veces al día

### 2.2 Hotel Guest (Customer)
- Objetivo: Reservar habitación al mejor precio
- Funcionalidad: Ver precios, reservar, historial de reservas
- Frecuencia: Una vez / reserva

### 2.3 Super Admin (Propietario / DevOps)
- Objetivo: Monitorear sistema, gestionar usuarios, ver logs
- Funcionalidad: Health checks, métricas de uso, gestión de hoteles

---

## 3. UI Structure

### 3.1 Layout Global
```
┌──────────────────────────────────────────┐
│ Sidebar (Logo + Nav)  │  Top Bar (User)  │
│                       │                  │
│  ▌ Optimus Price      │  Notifications⚡ │
│                       │  Juan ▼          │
│  ┌─────────────────┐  │                  │
│  │ ● Dashboard     │  ├──────────────────┤
│  │ ○ Market Monitor│  │                  │
│  │ ○ Reservations  │  │   MAIN CONTENT   │
│  │ ○ Price Sim     │  │                  │
│  │ ○ Settings      │  │                  │
│  └─────────────────┘  │                  │
└──────────────────────────────────────────┘
```

### 3.2 Pages

#### A. Dashboard (Página Principal)

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Recommended  │ Revenue      │ Occupancy    │ Active       │
│ Price        │ Impact       │ Forecast     │ Alerts       │
│ ─────────    │ ─────────    │ ─────────    │ ─────────    │
│ €184         │ +30%         │ 87%          │ 3            │
│ ▲ +12.4%     │ €24.5K pot.  │ High Demand  │ 2 critical   │
│ High Confid. │              │              │              │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌──────────────────────────────────┬──────────────────────────┐
│ Price Trends (7 días)            │ Market Intelligence      │
│ ┌────────────────────────────┐   │ ┌────────────────────┐  │
│ │  ▁▃▆█▇▆▅                  │   │ │ Booking.com  €169  │  │
│ │  ────────────────────      │   │ │ Expedia      €172  │  │
│ │  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔    │   │ │ Hotels.com   €175  │  │
│ └────────────────────────────┘   │ │ Trivago      €168  │  │
│                                  │ │ ───────────────── │  │
│                                  │ │ ★ OPT AI    €184  │  │
│                                  │ └────────────────────┘  │
└──────────────────────────────────┴──────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ Recent Customer Activity                                    │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Juan Pérez   2 guests · 3 nights · Aug 15     €540  ✔ │ │
│ │ María Gómez  1 guest  · 2 nights · Sep 1      €320  ✔ │ │
│ │ ...                                                  │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

#### B. Market Monitor

```
┌────────────────────────────────────────────────────────────┐
│ Live Competitor Prices (auto-refresh cada 30s)             │
│ ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│ │  OTA     │  Ayer    │  Hoy     │  Gap     │  Trend   │  │
│ ├──────────┼──────────┼──────────┼──────────┼──────────┤  │
│ │ Booking  │  €165    │  €169    │  +2.4%   │  ▲       │  │
│ │ Expedia  │  €170    │  €172    │  +1.2%   │  ▲       │  │
│ │ Hotels   │  €178    │  €175    │  -1.7%   │  ▼       │  │
│ │ Trivago  │  €166    │  €168    │  +1.2%   │  ▲       │  │
│ │ ★ OPT    │  €180    │  €184    │  +2.2%   │  ▲       │  │
│ └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                                                             │
│ Price Position Chart                                        │
│ ┌────────────────────────────────────────────────────────┐ │
│ │  ▼ Below        ● At Market        ▲ Above            │ │
│ │  ─────────────────────────────────────────             │ │
│ │             ████████████████████                       │ │
│ │  OPT ▲─────────────────────────►                      │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

#### C. How It Works (Backend Tab)

```
┌────────────────────────────────────────────────────────────┐
│ Architecture Pipeline                                      │
│                                                             │
│ ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐        │
│ │ RASPAL │──▶│Python  │──▶│FastAPI │──▶│Next.js │        │
│ │Worker  │   │ML Eng. │   │REST API│   │ UI     │        │
│ └────────┘   └────────┘   └────────┘   └────────┘        │
│      │            │            │            │              │
│      ▼            ▼            ▼            ▼              │
│ ┌────────────────────────────────────────────────────┐    │
│ │              PostgreSQL                             │    │
│ │  hotel_reservations | price_queries | alerts       │    │
│ └────────────────────────────────────────────────────┘    │
│                                                             │
│ Key Metrics (último entrenamiento)                          │
│ ┌──────────────┬──────────────┬──────────────┐            │
│ │ Model        │ Features     │ R² Score     │            │
│ │ GradientBoos │ 41 (26+15)   │ 0.9998       │            │
│ └──────────────┴──────────────┴──────────────┘            │
│                                                             │
│ Data Flow:                                                  │
│ 1. RASPAL scrappea Booking, Expedia, Hotels, Trivago      │
│ 2. ML Engine predice precio óptimo con 41 features        │
│ 3. WebSocket envía actualizaciones a UI en tiempo real    │
│ 4. Admin ajusta precios → override impacta predicciones   │
│ 5. Cliente reserva → feedback loop → retrain ML           │
└────────────────────────────────────────────────────────────┘
```

#### D. Price Simulator

```
┌────────────────────────────────────────────────────────────┐
│ Price Scenario Simulator                                   │
│                                                             │
│ ┌─────────────────────┐  ┌─────────────────────┐          │
│ │ Lead Time: 30 días  │  │ Room Type: Suite    │          │
│ │ Guests: 2           │  │ Meal Plan: Desayuno │          │
│ │ Nights: 3           │  │ Season: Alta        │          │
│ └─────────────────────┘  └─────────────────────┘          │
│                                                             │
│ Result:                                                     │
│ ┌──────────────────────────┬──────────────────────────┐    │
│ │ Base Price               │ Optimized Price          │    │
│ │ ────────────             │ ──────────────           │    │
│ │ €168                     │ €184 ▲ +9.5%             │    │
│ │                          │ ★ Recommended            │    │
│ └──────────────────────────┴──────────────────────────┘    │
│                                                             │
│ What-If Analysis                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │  Change variable → see impact instantly                 │ │
│ │  ┌───────────────────────────────────────┐             │ │
│ │  │ Month: ■■■■■■■■□□ August              │             │ │
│ │  │ Occupancy: ■■■■■■■■□□ 78%             │             │ │
│ │  │ Competitor Avg: ■■■■■■■□□□ €172       │             │ │
│ │  └───────────────────────────────────────┘             │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints

### 4.1 Auth
```
POST   /api/v1/auth/login          # JWT login
POST   /api/v1/auth/register       # Register hotel
POST   /api/v1/auth/refresh        # Refresh token
```

### 4.2 Predictions
```
POST   /api/v1/predict             # Precio con ML (26 features)
POST   /api/v1/predict/enriched    # Precio con 41 features (+competidores)
GET    /api/v1/predict/history     # Historial de predicciones
```

### 4.3 Competitors
```
GET    /api/v1/competitors/prices?hotel_id=X    # Últimos precios OTA
GET    /api/v1/competitors/trends?hotel_id=X    # Tendencia 7 días
POST   /api/v1/competitors/check                # Trigger scraping manual
```

### 4.4 Reservations
```
GET    /api/v1/reservations                     # Lista (admin)
POST   /api/v1/reservations                     # Nueva reserva
GET    /api/v1/reservations/{id}                # Detalle
```

### 4.5 Admin
```
GET    /api/v1/admin/stats                      # KPIs dashboard
POST   /api/v1/admin/override                   # Price override
GET    /api/v1/admin/alerts                     # Alertas activas
```

### 4.6 WebSocket
```
WS     /ws/prices/{hotel_id}                    # Precios en vivo
WS     /ws/alerts/{hotel_id}                    # Alertas en vivo
WS     /ws/admin/notifications                  # Notificaciones admin
```

---

## 5. Database Schema (PostgreSQL)

```sql
-- Hotels (multi-tenant)
CREATE TABLE hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Users (admin + guest)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    email TEXT UNIQUE NOT NULL,
    role TEXT CHECK (role IN ('admin', 'guest', 'superadmin')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Reservations
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    user_id UUID REFERENCES users(id),
    guest_name TEXT, email TEXT, phone TEXT,
    check_in DATE NOT NULL, check_out DATE NOT NULL,
    nights INT, guests INT, room_type TEXT,
    meal_plan TEXT, lead_time INT, season TEXT,
    base_price DECIMAL(10,2), final_price DECIMAL(10,2),
    override_pct DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Price Queries (cada vez que alguien pide precio)
CREATE TABLE price_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    session_id TEXT, features JSONB,
    predicted_price DECIMAL(10,2),
    market_adjustment DECIMAL(5,2),
    final_price DECIMAL(10,2),
    source TEXT, created_at TIMESTAMPTZ DEFAULT now()
);

-- Competitor Snapshots
CREATE TABLE competitor_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    ota TEXT NOT NULL,
    price DECIMAL(10,2),
    currency TEXT DEFAULT 'EUR',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Price Overrides
CREATE TABLE price_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    user_id UUID REFERENCES users(id),
    modifier_pct DECIMAL(5,2),
    reason TEXT, active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID REFERENCES hotels(id),
    type TEXT, severity TEXT,
    message TEXT, read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_competitor_hotel_ota ON competitor_prices(hotel_id, ota, created_at DESC);
CREATE INDEX idx_queries_hotel_date ON price_queries(hotel_id, created_at DESC);
CREATE INDEX idx_reservations_hotel ON reservations(hotel_id, created_at DESC);
```

---

## 6. Component Tree (Next.js)

```
layout.tsx                    # Root layout + providers
├── sidebar.tsx               # Nav sidebar
├── topbar.tsx                # User menu + notifications
├── page.tsx                  # Dashboard
│   ├── kpi-cards.tsx         # 4 KPI cards (Recommended Price, Revenue, etc.)
│   ├── price-chart.tsx       # 7-day price trend (Recharts)
│   ├── market-intel.tsx      # Competitor prices card
│   └── activity-feed.tsx     # Recent customer activity
├── monitor/
│   ├── page.tsx              # Market Monitor
│   ├── competitor-table.tsx  # OTA price comparison table
│   └── price-position.tsx    # Position chart
├── reservations/
│   ├── page.tsx              # Reservations list
│   └── reservation-row.tsx   # Single reservation
├── simulator/
│   ├── page.tsx              # Price simulator
│   └── what-if.tsx           # What-if analysis controls
├── how-it-works/
│   └── page.tsx              # Architecture + pipeline explanation
├── settings/
│   └── page.tsx              # Hotel settings, profile
└── components/ui/
    ├── card.tsx              # shadcn card base
    ├── chart.tsx             # Recharts wrapper
    └── badge.tsx             # Status badges
```

---

## 7. Color System (mantiene el design system actual)

```
--background: #0F1720
--card:       #111827
--border:     #242D3D
--text:       #FFFFFF
--text-sec:   #B0B8C5
--text-muted: #7C8595
--accent:     #A3B18A (Sage Green)
--danger:     #EF4444
--warning:    #F59E0B

Typography: Inter (headings) + Geist (body)
Icons: Lucide React
```

---

## 8. Implementation Phases

### Phase A — Backend API (FastAPI)
1. Project scaffold + Docker
2. DB models + Alembic migrations
3. Auth endpoints (JWT)
4. ML prediction endpoint (wrapper del código existente)
5. CRUD reservations + price_queries
6. WebSocket endpoint para precios en vivo

### Phase B — Frontend (Next.js)
1. Project scaffold + Tailwind + shadcn/ui
2. Layout (sidebar + topbar + theme)
3. Dashboard page (KPI cards + charts)
4. Market Monitor page (competitor table)
5. Reservations page
6. Simulator page
7. How It Works page

### Phase C — Real-time + Workers
1. RASPAL worker integrado como microservicio
2. WebSocket bridge RASPAL → Next.js
3. Alert system (price drop >10%, competitor change)
4. Auto-refresh dashboard (30s polling / WebSocket push)

### Phase D — Production
1. Docker Compose full stack
2. CI/CD (GitHub Actions)
3. Vercel + Railway deploy
4. Monitoring + logging

---

## 9. Key Principles

- **Producto real** — No prototipo, no demo, no notebook
- **Spec-driven** — Cada componente se especifica antes de codificar
- **Data first** — Dashboard es el protagonista, no el código
- **Tiempo real** — WebSocket para todo lo que cambia
- **ML es backend** — El código Python existente es el motor, no la UI
- **RASPAL es worker** — Corre independiente, alimenta la DB
- **Mobile responsive** — Next.js lo da gratis con Tailwind
