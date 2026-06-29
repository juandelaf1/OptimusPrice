import pandas as pd, numpy as np
df = pd.read_csv('data/processed/hotel_reservations_real.csv')
X = df.drop(columns=['avg_price_per_room'])

# Check correlations
cols = ['arrival_month','arrival_week_number','arrival_year','arrival_day_of_week',
        'lead_time','total_nights','total_guests','room_type_value','market_segment_value']
corr = X[cols].corr()
print('=== Correlation matrix ===')
print(corr.round(3))
print()

# Check feature builder features
print('Feature builder features in dataset:')
fb_cols = ['month_sin','month_cos','week_sin','week_cos','quarter','season',
           'is_high_season','is_weekend_arrival','lag_7','lag_30','rolling_mean_7',
           'lead_time_bin','short_stay','medium_stay','long_stay','stay_bucket',
           'booking_window','guest_density','room_intensity']
for c in fb_cols:
    present = c in X.columns
    status = 'PRESENT' if present else 'MISSING'
    print(f'  {c}: {status}')

# VIF approximation for temporal features
print()
print('=== VIF analysis (pairwise R2 approach) ===')
from sklearn.linear_model import LinearRegression
for target_feat in ['arrival_month', 'arrival_week_number', 'arrival_year', 'arrival_day_of_week']:
    other_features = [c for c in cols if c != target_feat]
    reg = LinearRegression().fit(X[other_features], X[target_feat])
    r2 = reg.score(X[other_features], X[target_feat])
    vif = 1 / (1 - r2) if r2 < 1 else float('inf')
    print(f'  {target_feat}: R2={r2:.4f}, VIF={vif:.2f}')

print()
print('=== Temporal features redundancy ===')
from itertools import combinations
for a, b in combinations(['arrival_month', 'arrival_week_number', 'arrival_year', 'arrival_day_of_week', 'arrival_date'], 2):
    if a in X.columns and b in X.columns:
        r = X[a].corr(X[b])
        if abs(r) > 0.3:
            print(f'  {a} vs {b}: r={r:.4f}')
