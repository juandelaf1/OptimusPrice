import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv('data/processed/hotel_reservations_real.csv')
X = df.drop(columns=['avg_price_per_room'])
y = df['avg_price_per_room']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

mse = mean_squared_error
rmse = lambda yt, yp: np.sqrt(mse(yt, yp))

scalers = {
    'StandardScaler': StandardScaler(),
    'RobustScaler': RobustScaler(),
    'MinMaxScaler': MinMaxScaler(),
    'NoScaler': None,
}

results = []
for name, scaler in scalers.items():
    if scaler is not None:
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
    else:
        X_train_s = X_train.values
        X_test_s = X_test.values

    model = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
    model.fit(X_train_s, y_train)

    pred_train = model.predict(X_train_s)
    pred_test = model.predict(X_test_s)

    results.append({
        'scaler': name,
        'train_rmse': round(rmse(y_train, pred_train), 4),
        'test_rmse': round(rmse(y_test, pred_test), 4),
        'train_r2': round(r2_score(y_train, pred_train), 4),
        'test_r2': round(r2_score(y_test, pred_test), 4),
        'gap_rmse': round(abs(rmse(y_train, pred_train) - rmse(y_test, pred_test)), 4),
        'gap_r2': round(abs(r2_score(y_train, pred_train) - r2_score(y_test, pred_test)), 4),
        'zeros_coef': int(np.sum(model.coef_ == 0)),
        'coef_sparsity': round(np.sum(model.coef_ == 0) / len(model.coef_) * 100, 1),
    })

res_df = pd.DataFrame(results)
print('=== ElasticNet Scaling Comparison ===')
print(res_df.to_string(index=False))
print()

# GradientBoosting with RobustScaler
from sklearn.ensemble import GradientBoostingRegressor

scaler = RobustScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

gb = GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.08,
                                subsample=0.8, random_state=42)
gb.fit(X_train_s, y_train)

pred_train = gb.predict(X_train_s)
pred_test = gb.predict(X_test_s)

print('=== GradientBoosting with RobustScaler ===')
print(f'Train RMSE: {rmse(y_train, pred_train):.4f}')
print(f'Test RMSE:  {rmse(y_test, pred_test):.4f}')
print(f'Train R2:   {r2_score(y_train, pred_train):.4f}')
print(f'Test R2:    {r2_score(y_test, pred_test):.4f}')
print(f'Gap R2:     {abs(r2_score(y_train, pred_train) - r2_score(y_test, pred_test)):.4f}')

# Show overfitting analysis
print()
print('=== Overfitting Analysis ===')
en = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
scaler = RobustScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)
en.fit(X_train_s, y_train)

train_mse = mse(y_train, en.predict(X_train_s))
test_mse = mse(y_test, en.predict(X_test_s))
print(f'ElasticNet - Train MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}')
print(f'Variance ratio (train/test): {train_mse/test_mse:.4f}')
print(f'Coef non-zero: {np.sum(en.coef_ != 0)}/{len(en.coef_)}')

gb2 = GradientBoostingRegressor(n_estimators=200, max_depth=6, learning_rate=0.08,
                                 subsample=0.8, random_state=42)
gb2.fit(X_train_s, y_train)
gb_train_mse = mse(y_train, gb2.predict(X_train_s))
gb_test_mse = mse(y_test, gb2.predict(X_test_s))
print(f'GradientBoosting - Train MSE: {gb_train_mse:.4f}, Test MSE: {gb_test_mse:.4f}')
print(f'Variance ratio (train/test): {gb_train_mse/gb_test_mse:.4f}')
