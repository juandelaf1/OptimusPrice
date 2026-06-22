<p align="center">
  <img src="docs/img/optimus_price_banner.png" alt="Optimus Price" width="100%">
</p>

<p align="center">
  <b>Revenue Intelligence Platform for Independent Hotels</b><br>
  ML-powered pricing · Real-time market data · OTA competitor monitoring
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-7C8595?logo=python">
  <img src="https://img.shields.io/badge/Streamlit-7C8595?logo=streamlit">
  <img src="https://img.shields.io/badge/scikit--learn-7C8595?logo=scikit-learn">
  <img src="https://img.shields.io/badge/raspal_scrapper-7C8595">
  <img src="https://img.shields.io/badge/license-MIT-7C8595">
</p>

---

## Product

**Optimus Price** combina machine learning con scraping web en tiempo real para optimizar precios de habitaciones y maximizar ingresos hoteleros.

- **ML Pricing Engine** — GradientBoosting con 41 features (R²=0.9998)
- **Real-Time Market Intel** — Precios vivos de Booking, Expedia, Hotels.com, Trivago vía RASPAL
- **Competitor Analysis** — Detección automática de gaps de precio con alertas
- **Continuous Monitoring** — Servicio de monitoreo cada 15 minutos
- **Role-Based UI** — Portal cliente + Dashboard admin (Streamlit)

---

## Quick Start

```bash
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final
pip install -r requirements.txt
pip install raspal[all]
raspal setup

streamlit run app_streamlit/app_cliente.py    # Customer portal
streamlit run app_streamlit/app_adm_1.py      # Admin dashboard
```

---

## Architecture

```
Optimus_Price_Final/
├── src/optimus_price/          ML Pipeline (20,800+ lines)
├── app_streamlit/              Streamlit interfaces
├── enhanced_optimus.py         RASPAL integration
├── competitor_monitor.py       OTA comparison engine
├── monitoring_service.py       Continuous monitoring daemon
├── scraping_manager.py         Multi-OTA scraper orchestrator
├── feature_enricher.py         Competitor feature engineering
├── configs/                    OTA scraping YAML configs
├── models/                     Trained model (41 features)
└── data/                       Datasets + monitoring logs
```

---

## RASPAL Integration

| Engine | Purpose | Status |
|--------|---------|--------|
| stealth | OTA scraping con evasión Cloudflare | Active |
| scrapling | Extracción con selectolax | Active |
| LLMExtractor | Parsing vía Ollama (llama3.2) | Active |
| AutoThrottle | Rate limiting adaptativo | Active |

---

## ML Pipeline

1. **Feature Engineering** — 26 baseline + 15 competitor features
2. **Model** — GradientBoosting Regressor (Optuna-optimized)
3. **Performance** — RMSE 0.38, R² 0.9998
4. **Enriched Training** — Datos con precios de competidores simulados vía RASPAL

---

## Deployment

```bash
docker build -t optimus-price .
docker run -p 8501:8501 optimus-price
```

---

## Revenue Impact

| Channel | Commission | Net Revenue |
|---------|-----------|-------------|
| Direct (Optimus Price) | 0% | **€100** |
| OTA (15%) | 15% | €85 |
| OTA (30%) | 30% | €70 |

---

<p align="center">
  <sub>Built with Python, Pandas, Scikit-Learn, Streamlit &amp; raspal_scrapper</sub><br>
  <sub>Juan de la Fuente — juandelafuentelarrocca@gmail.com</sub><br>
  <sub>Version 2.0 — June 2026</sub>
</p>
