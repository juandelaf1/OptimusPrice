"""
Test: just drop arrival_week_number, no feature engineering
Compares: 27 original features vs 26 (drop week_number)
"""
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'processed', 'hotel_reservations_real.csv'))
target = 'avg_price_per_room'

print('=' * 70)
print('TEST: Eliminar arrival_week_number (sin feature engineering)')
print('=' * 70)

# Original 27 features
X = df.drop(columns=[target])
y = df[target]

# 1. Baseline: 27 features, NoScaler
print('\n1. Baseline (27 features, NoScaler)')
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
m = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
m.fit(X_tr.values, y_tr)
p_tr, p_te = m.predict(X_tr.values), m.predict(X_te.values)
print(f'  Train RMSE={np.sqrt(mean_squared_error(y_tr, p_tr)):.4f}, R2={r2_score(y_tr, p_tr):.4f}')
print(f'  Test  RMSE={np.sqrt(mean_squared_error(y_te, p_te)):.4f}, R2={r2_score(y_te, p_te):.4f}')
print(f'  Gap R2={abs(r2_score(y_tr, p_tr) - r2_score(y_te, p_te)):.4f}')
print(f'  Coef zero: {np.sum(m.coef_ == 0)}/{len(m.coef_)}')

# 2. Drop week_number: 26 features, NoScaler
print('\n2. Drop arrival_week_number (26 features, NoScaler)')
X2 = X.drop(columns=['arrival_week_number'])
X_tr2, X_te2 = X2.iloc[:len(y_tr)], X2.iloc[len(y_tr):]
m2 = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
m2.fit(X_tr2.values, y_tr)
p_tr2, p_te2 = m2.predict(X_tr2.values), m2.predict(X_te2.values)
print(f'  Train RMSE={np.sqrt(mean_squared_error(y_tr, p_tr2)):.4f}, R2={r2_score(y_tr, p_tr2):.4f}')
print(f'  Test  RMSE={np.sqrt(mean_squared_error(y_te, p_te2)):.4f}, R2={r2_score(y_te, p_te2):.4f}')
print(f'  Gap R2={abs(r2_score(y_tr, p_tr2) - r2_score(y_te, p_te2)):.4f}')
print(f'  Coef zero: {np.sum(m2.coef_ == 0)}/{len(m2.coef_)}')

# 3. Drop week_number: 26 features, StandardScaler
print('\n3. Drop arrival_week_number (26 features, StandardScaler)')
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
pipe = Pipeline([('scaler', StandardScaler()), ('model', ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42))])
pipe.fit(X_tr2, y_tr)
p_tr3 = pipe.predict(X_tr2)
p_te3 = pipe.predict(X_te2)
print(f'  Train RMSE={np.sqrt(mean_squared_error(y_tr, p_tr3)):.4f}, R2={r2_score(y_tr, p_tr3):.4f}')
print(f'  Test  RMSE={np.sqrt(mean_squared_error(y_te, p_te3)):.4f}, R2={r2_score(y_te, p_te3):.4f}')
print(f'  Gap R2={abs(r2_score(y_tr, p_tr3) - r2_score(y_te, p_te3)):.4f}')

# 4. TimeSeries CV on 26 features
print('\n4. TimeSeriesSplit CV (26 features)')
tscv = TimeSeriesSplit(n_splits=5)
cv_rmse, cv_r2 = [], []
for tr_idx, val_idx in tscv.split(X2):
    m_cv = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
    m_cv.fit(X2.iloc[tr_idx].values, y.iloc[tr_idx])
    yp = m_cv.predict(X2.iloc[val_idx].values)
    cv_rmse.append(np.sqrt(mean_squared_error(y.iloc[val_idx], yp)))
    cv_r2.append(r2_score(y.iloc[val_idx], yp))
print(f'  CV RMSE: {np.mean(cv_rmse):.4f} +/- {np.std(cv_rmse):.4f}')
print(f'  CV R2:   {np.mean(cv_r2):.4f} +/- {np.std(cv_r2):.4f}')

# Summary
print('\n' + '=' * 70)
print('SUMMARY')
print('=' * 70)
print(f'{"Config":<40} {"Test RMSE":<12} {"Test R2":<12} {"Gap R2":<12}')
print('-' * 70)
print(f'{"1. Baseline 27f NoScaler":<40} {np.sqrt(mean_squared_error(y_te, p_te)):<12.4f} {r2_score(y_te, p_te):<12.4f} {abs(r2_score(y_tr, p_tr)-r2_score(y_te, p_te)):<12.4f}')
print(f'{"2. Drop week 26f NoScaler":<40} {np.sqrt(mean_squared_error(y_te, p_te2)):<12.4f} {r2_score(y_te, p_te2):<12.4f} {abs(r2_score(y_tr, p_tr2)-r2_score(y_te, p_te2)):<12.4f}')
print(f'{"3. Drop week 26f StdScaler":<40} {np.sqrt(mean_squared_error(y_te, p_te3)):<12.4f} {r2_score(y_te, p_te3):<12.4f} {abs(r2_score(y_tr, p_tr3)-r2_score(y_te, p_te3)):<12.4f}')
