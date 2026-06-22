# Metrics Benchmark

> Saved before retraining with the fixed feature pipeline.
> Source: notebooks `03_Entrenamiento_Evaluacion_un_modelo.ipynb` and `04_ent_ev_varios_modelos.ipynb`

## Notebook 3 – Single Model (Random Forest)

| Model | RMSE | R² |
|---|---|---|
| Random Forest (no tuning) | 11.78 | 0.81 |
| Random Forest (Optuna) | **11.04** | **0.84** |

## Notebook 4 – Multi-Model Comparison

### Test Set Performance

| Model | RMSE | MAE | R² |
|---|---|---|---|
| Linear Regression | 24.67 | 17.89 | 0.50 |
| Decision Tree | 19.86 | 8.85 | 0.68 |
| **Random Forest** | **15.20** | **7.51** | **0.81** |
| XGBoost | 15.77 | 9.45 | 0.80 |
| **CatBoost** | **14.62** | **8.03** | **0.82** |

### Cross-Validation (average RMSE)

| Model | CV RMSE |
|---|---|
| Linear Regression | 24.26 |
| Decision Tree | 19.34 |
| Random Forest | 14.79 |
| XGBoost | 15.22 |
| **CatBoost** | **14.23** |
