"""
Sprint ML: Feature engineering + multicollinearity fix + NoScaler
Tests the proposed improvements before modifying training.py
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.optimus_price.feature_builder import (
    build_temporal_features,
    build_booking_behavior_features,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'hotel_reservations_real.csv')

print('=' * 70)
print('SPRINT ML — Feature Engineering + Multicollinearity Fix')
print('=' * 70)

# 1. Load
df = pd.read_csv(DATA_PATH)
target = 'avg_price_per_room'
print(f'\nLoaded: {df.shape}')

# 2. Baseline: current state (remove competitor leakage only)
X_raw = df.drop(columns=[target])
leaked = [c for c in X_raw.columns if 'competitor' in c.lower()]
if leaked:
    X_raw = X_raw.drop(columns=leaked)
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y, test_size=0.2, random_state=42, shuffle=False
)

pipe = Pipeline([('scaler', StandardScaler()), ('model', ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42))])
pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)
baseline_rmse = np.sqrt(mean_squared_error(y_test, pred))
baseline_r2 = r2_score(y_test, pred)
print(f'\nBASELINE (current state, StandardScaler):')
print(f'  RMSE={baseline_rmse:.4f}, R2={baseline_r2:.4f}')

# 3. Apply feature engineering (temporal + booking behavior only — NO temporal aggregates)
print('\n' + '-' * 70)
print('APPLYING FEATURE ENGINEERING...')
print('-' * 70)

df_fe = build_temporal_features(df)
df_fe = build_booking_behavior_features(df_fe)
print(f'Shape after feature engineering: {df_fe.shape}')

# 4. Drop arrival_week_number (VIF > 100)
print(f'\nColumns before drop: {df_fe.shape[1]}')
df_fe = df_fe.drop(columns=['arrival_week_number'])
print(f'Columns after dropping arrival_week_number: {df_fe.shape[1]}')

# Drop non-numeric columns
non_numeric = df_fe.select_dtypes(include=['object']).columns.tolist()
print(f'Dropping non-numeric columns: {non_numeric}')
df_fe = df_fe.drop(columns=non_numeric)

X_eng = df_fe.drop(columns=[target])
y_eng = df_fe[target]

# Check new features
new_cols = [c for c in X_eng.columns if c not in X_raw.columns]
dropped = [c for c in X_raw.columns if c not in X_eng.columns]
print(f'New features added: {new_cols}')
print(f'Features removed: {dropped}')
print(f'Total features: {X_eng.shape[1]}')

# 5. Train-test split
X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(
    X_eng, y_eng, test_size=0.2, random_state=42, shuffle=False
)

# 6. Train with NO scaler (best from our test)
print('\n' + '-' * 70)
print('TRAINING WITH NO SCALER (best performing)')
print('-' * 70)
model_no = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
model_no.fit(X_train_e, y_train_e)
pred_train_no = model_no.predict(X_train_e)
pred_test_no = model_no.predict(X_test_e)

train_rmse_no = np.sqrt(mean_squared_error(y_train_e, pred_train_no))
test_rmse_no = np.sqrt(mean_squared_error(y_test_e, pred_test_no))
train_r2_no = r2_score(y_train_e, pred_train_no)
test_r2_no = r2_score(y_test_e, pred_test_no)

print(f'Train RMSE={train_rmse_no:.4f}, Test RMSE={test_rmse_no:.4f}')
print(f'Train R2={train_r2_no:.4f}, Test R2={test_r2_no:.4f}')
print(f'Gap R2={abs(train_r2_no - test_r2_no):.4f}')

# 7. Train with StandardScaler for comparison
print('\n' + '-' * 70)
print('TRAINING WITH STANDARDSCALER')
print('-' * 70)
pipe_s = Pipeline([('scaler', StandardScaler()), ('model', ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42))])
pipe_s.fit(X_train_e, y_train_e)
pred_train_s = pipe_s.predict(X_train_e)
pred_test_s = pipe_s.predict(X_test_e)

train_rmse_s = np.sqrt(mean_squared_error(y_train_e, pred_train_s))
test_rmse_s = np.sqrt(mean_squared_error(y_test_e, pred_test_s))
train_r2_s = r2_score(y_train_e, pred_train_s)
test_r2_s = r2_score(y_test_e, pred_test_s)

print(f'Train RMSE={train_rmse_s:.4f}, Test RMSE={test_rmse_s:.4f}')
print(f'Train R2={train_r2_s:.4f}, Test R2={test_r2_s:.4f}')
print(f'Gap R2={abs(train_r2_s - test_r2_s):.4f}')

# 8. TimeSeriesSplit CV on engineered data
print('\n' + '-' * 70)
print('TIMESERIES CROSS-VALIDATION (engineered + NoScaler)')
print('-' * 70)
tscv = TimeSeriesSplit(n_splits=5)
cv_rmse, cv_r2 = [], []
for train_idx, val_idx in tscv.split(X_eng):
    X_tr, X_val = X_eng.iloc[train_idx], X_eng.iloc[val_idx]
    y_tr, y_val = y_eng.iloc[train_idx], y_eng.iloc[val_idx]
    m = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
    m.fit(X_tr, y_tr)
    yp = m.predict(X_val)
    cv_rmse.append(np.sqrt(mean_squared_error(y_val, yp)))
    cv_r2.append(r2_score(y_val, yp))

print(f'CV RMSE: {np.mean(cv_rmse):.4f} +/- {np.std(cv_rmse):.4f}')
print(f'CV R2:   {np.mean(cv_r2):.4f} +/- {np.std(cv_r2):.4f}')

# 9. Feature importance
print('\n' + '-' * 70)
print('TOP 10 FEATURE COEFFICIENTS (NoScaler)')
print('-' * 70)
coef_df = pd.DataFrame({
    'feature': X_eng.columns,
    'coef': model_no.coef_,
    'abs_coef': np.abs(model_no.coef_),
}).sort_values('abs_coef', ascending=False)
print(coef_df.head(10).to_string(index=False))

# 10. Summary comparison
print('\n' + '=' * 70)
print('SUMMARY: BASELINE vs IMPROVED')
print('=' * 70)
print(f'{"Metric":<25} {"Baseline":<15} {"Improved":<15} {"Delta":<15}')
print('-' * 70)
print(f'{"Test RMSE":<25} {baseline_rmse:<15.4f} {test_rmse_no:<15.4f} {(baseline_rmse - test_rmse_no):<15.4f}')
baseline_r2 = r2_score(y_test, pipe.predict(X_test))
print(f'{"Test R2":<25} {baseline_r2:<15.4f} {test_r2_no:<15.4f} {(test_r2_no - baseline_r2):<15.4f}')
print(f'{"Gap R2":<25} {"N/A":<15} {abs(train_r2_no - test_r2_no):<15.4f} {"":<15}')
print(f'{"Features":<25} {X_raw.shape[1]:<15} {X_eng.shape[1]:<15} {X_eng.shape[1] - X_raw.shape[1]:<15}')
print(f'{"CV RMSE mean":<25} {"N/A":<15} {np.mean(cv_rmse):<15.4f} {"":<15}')
