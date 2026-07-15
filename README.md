# OptimusPrice

ML-driven hotel revenue management with Random Forest price prediction (R-squared = 0.92).

[Full Case Study](https://juandelaf1.github.io/projects/optimus-price)

## Overview

OptimusPrice predicts optimal hotel room prices using Random Forest trained on public Airbnb data. It covers the full ML lifecycle: feature engineering, Optuna hyperparameter tuning, evaluation, and an interactive Streamlit dashboard.

## Key Results

- **R-squared = 0.92** price prediction accuracy on test data
- **MAPE = 14.5%** on held-out test set
- **Optuna** hyperparameter optimization
- **Interactive dashboard** for what-if price analysis

## Stack

Python - scikit-learn - Optuna - Pandas - Streamlit - Docker

## Limitations

- Trained on public Airbnb data, not proprietary hotel data
- Does not incorporate real-time demand, events, or competitor pricing
- Research prototype, not production-deployed

---

*Full case study with data preparation, feature importance, and model selection at juandelaf1.github.io/projects/optimus-price*