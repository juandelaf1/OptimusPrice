"""
Test: selected INE features + StandardScaler
Only use grado_ocupacion_plazas (most interpretable)
Compare with and without scaling
"""
import sys, pandas as pd, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "data" / "processed" / "hotel_reservations_real.csv")
ine_data = pd.read_csv(BASE_DIR / "data/v2_market/raw/ine/baleares_occupation_data.csv")
target = "avg_price_per_room"

print("=" * 70)
print("TEST: INE FEATURES SELECCIONADAS + SCALING")
print("=" * 70)

# Check correlation between INE features and arrival_month
print("\n[1] Correlación INE features vs arrival_month:")
df_merged = df.merge(ine_data, left_on=["arrival_year", "arrival_month"],
                     right_on=["year", "month"], how="left")
ine_cols = [c for c in ine_data.columns if c not in ["year", "month"]]
for c in ine_cols:
    corr = df_merged[c].corr(df_merged["arrival_month"])
    print(f"  {c}: r={corr:.4f} con arrival_month")

# Select only most impactful features
print("\n[2] Features INE seleccionadas:")
selected_ine = ["grado_ocupacion_plazas", "estancia_media"]
print(f"  {selected_ine}")

# Baseline
X = df.drop(columns=[target])
y = df[target]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
m = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
m.fit(X_tr.values, y_tr)
base_rmse = np.sqrt(mean_squared_error(y_te, m.predict(X_te.values)))
base_r2 = r2_score(y_te, m.predict(X_te.values))
print(f"\nBaseline (27f, NoScaler): RMSE={base_rmse:.4f}, R2={base_r2:.4f}")

# Test different configurations
configs = [
    {"name": "+1 INE (grado_ocup), NoScaler", "features": ["grado_ocupacion_plazas"], "scaler": False},
    {"name": "+1 INE (grado_ocup), StdScaler", "features": ["grado_ocupacion_plazas"], "scaler": True},
    {"name": "+2 INE, StdScaler", "features": selected_ine, "scaler": True},
    {"name": "+9 INE, StdScaler", "features": ine_cols, "scaler": True},
]

results = []
for cfg in configs:
    print(f"\n[3] {cfg['name']}")

    # Merge
    df_m = df.merge(ine_data[["year", "month"] + cfg["features"]],
                    left_on=["arrival_year", "arrival_month"],
                    right_on=["year", "month"], how="left")
    df_m = df_m.drop(columns=["year", "month"])

    X_m = df_m.drop(columns=[target])
    y_m = df_m[target]
    X_tr_m, X_te_m, y_tr_m, y_te_m = train_test_split(
        X_m, y_m, test_size=0.2, random_state=42, shuffle=False)

    if cfg["scaler"]:
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("model", ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42))
        ])
        pipe.fit(X_tr_m, y_tr_m)
        p_tr = pipe.predict(X_tr_m)
        p_te = pipe.predict(X_te_m)
    else:
        model = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
        model.fit(X_tr_m.values, y_tr_m)
        p_tr = model.predict(X_tr_m.values)
        p_te = model.predict(X_te_m.values)

    tr_rmse = np.sqrt(mean_squared_error(y_tr_m, p_tr))
    te_rmse = np.sqrt(mean_squared_error(y_te_m, p_te))
    tr_r2 = r2_score(y_tr_m, p_tr)
    te_r2 = r2_score(y_te_m, p_te)
    gap = abs(tr_r2 - te_r2)

    results.append({
        "config": cfg["name"],
        "train_rmse": tr_rmse,
        "test_rmse": te_rmse,
        "train_r2": tr_r2,
        "test_r2": te_r2,
        "gap_r2": gap,
    })
    print(f"  Train RMSE={tr_rmse:.4f}, R2={tr_r2:.4f}")
    print(f"  Test  RMSE={te_rmse:.4f}, R2={te_r2:.4f}")
    print(f"  Gap R2={gap:.4f}")

# Summary
print("\n" + "=" * 70)
print("COMPARACIÓN FINAL")
print("=" * 70)
print(f"{'Config':<45} {'Test RMSE':<12} {'Test R2':<12} {'Gap R2':<12}")
print("-" * 70)
print(f"{'Baseline (27f, NoScaler)':<45} {base_rmse:<12.4f} {base_r2:<12.4f} {'N/A':<12}")
for r in results:
    print(f"{r['config']:<45} {r['test_rmse']:<12.4f} {r['test_r2']:<12.4f} {r['gap_r2']:<12.4f}")

print("\n" + "=" * 70)
best = min(results, key=lambda x: x["test_rmse"])
if best["test_rmse"] < base_rmse:
    print(f"MEJOR: {best['config']} (RMSE {best['test_rmse']:.4f})")
else:
    print(f"Ninguna configuración INE supera la baseline.")
    print(f"Mejor INE: {best['config']} (RMSE {best['test_rmse']:.4f} vs baseline {base_rmse:.4f})")
