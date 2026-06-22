# Optimus Price (OPT-PR-001)
## AI-Powered Hotel Revenue Management System

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.2.2-F7931E?logo=scikit-learn)
![RASPAL](https://img.shields.io/badge/RASPAL-0.4%2B-purple)
![License](https://img.shields.io/badge/license-MIT-green)

**Optimus Price** is an AI-powered hotel revenue management system that combines **machine learning** with **real-time web scraping** to optimize room pricing and maximize revenue.

> Integrates ML-powered predictions with live competitor monitoring via RASPAL_SCRAPER.

---

## Features

- **ML Pricing Engine** — Random Forest with hyperparameter optimization (Optuna)
- **Real-Time Market Intel** — Live OTA price monitoring via RASPAL
- **Competitor Analysis** — Automatic price gap detection and recommendations
- **Role-Based UI** — Admin dashboard + customer portal (Streamlit)
- **Continuous Monitoring** — 15-min interval competitor price tracking
- **AI Extraction** — LLM-based price parsing from OTA pages
- **Docker Ready** — Containerized deployment with CI/CD

---

## Quick Start

```bash
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final
pip install -r requirements.txt
pip install raspal[all]
raspal setup

# Launch customer portal
streamlit run app_streamlit/app_cliente.py

# Launch admin dashboard
streamlit run app_streamlit/app_adm_1.py
```

---

## System Architecture

```
Optimus_Price_Final/
├── src/optimus_price/          # ML Pipeline
│   ├── data_generator.py       # Data generation (6,535 lines)
│   ├── data_processing.py      # Feature engineering (2,607 lines)
│   ├── training.py             # Model training (7,857 lines)
│   └── evaluation.py           # Model evaluation (3,850 lines)
├── app_streamlit/              # User Interfaces
│   ├── app_cliente.py          # Customer portal
│   └── app_adm_1.py            # Admin dashboard
├── enhanced_optimus.py         # RASPAL integration + enhanced pipeline
├── competitor_monitor.py       # OTA price comparison engine
├── models/                     # Trained ML models (.pkl)
├── data/                       # Raw and processed datasets
├── notebooks/                  # EDA and modeling notebooks
├── Dockerfile                  # Container deployment
├── requirements.txt            # Python dependencies
├── roadmap.md                  # 12-week product roadmap
└── AGENTS.md                   # Technical documentation
```

---

## RASPAL Integration

The system uses **RASPAL_SCRAPER** for web data collection:

| Component | Purpose | Engine |
|-----------|---------|--------|
| Fetcher | URL fetching | stealth, auto, scrapling, playwright |
| LLMExtractor | Price extraction | Ollama (llama3.2) |
| AutoThrottle | Rate limiting | 1-60s adaptive delay |
| Cache | Request caching | SQLite |

### Monitor Competitor Prices

```python
from enhanced_optimus import EnhancedOptimusPrice
from competitor_monitor import OTAPriceComparator

system = EnhancedOptimusPrice()
monitor = OTAPriceComparator(system)

# Analyze price gaps
result = monitor.analyze_price_gap({
    "hotel_id": "hotel-001",
    "total_guests": 2,
    "total_nights": 3,
    "season": "peak_season"
})
```

---

## ML Model Pipeline

1. **Feature Engineering** — total_guests, total_nights, seasonality, location
2. **Algorithm** — Random Forest Regressor
3. **Optimization** — Optuna hyperparameter tuning (cross-validated)
4. **Evaluation** — RMSE, MAE, R² metrics
5. **Persistence** — Model saved as `.pkl` for production inference

---

## Deployment

```bash
# Docker
docker build -t optimus-price .
docker run -p 8501:8501 optimus-price

# Or docker-compose
docker-compose up -d
```

---

## Roadmap

| Phase | Focus | Timeline |
|-------|-------|----------|
| 1 | Configure hotel-pricing scraping pipelines | Week 1-2 |
| 2 | Enhance ML model with scraped data | Week 3-4 |
| 3 | Deploy competitor monitoring service | Week 5-6 |
| 4 | Streamlit dashboards + alerts | Week 7-9 |
| 5 | Production hardening + scaling | Week 10-12 |

See full details in [roadmap.md](roadmap.md).

---

## Revenue Impact

| Booking Channel | Gross Revenue | Commission | Net Revenue |
|----------------|--------------|------------|-------------|
| Direct (Optimus Price) | €100 | 0% | €100 |
| OTA (15%) | €100 | 15% | €85 |
| OTA (30%) | €100 | 30% | €70 |

---

## Contact

**Juan de la Fuente** — juandelafuentelarrocca@gmail.com

---

*Version 1.0 — June 2026*
