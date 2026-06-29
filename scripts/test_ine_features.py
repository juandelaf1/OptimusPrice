"""
Extract INE Baleares occupancy data and merge with training dataset
Test if external tourism data improves predictions
"""
import sys, csv, json
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
TRAIN_PATH = DATA_DIR / "hotel_reservations_real.csv"
OUTPUT_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "ine"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2066"

# Baleares series codes and names
BALEARES_SERIES = {
    "EOT147": "grado_ocupacion_plazas",
    "EOT149": "grado_ocupacion_habitaciones",
    "EOT146": "plazas_estimadas",
    "EOT145": "establecimientos_abiertos",
    "EOT148": "grado_ocupacion_plazas_finde",
    "EOT150": "personal_empleado",
    "EOT151": "viajeros_entrados",
    "EOT152": "pernoctaciones",
    "EOT153": "estancia_media",
}

def timestamp_to_year_month(ts_ms):
    """Convert INE timestamp (ms) to (year, month) tuple."""
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.year, dt.month

def download_and_extract():
    """Download INE data and extract Baleares series."""
    print("Descargando datos INE...")
    r = requests.get(API_URL, timeout=120)
    data = r.json()
    print(f"  Total series: {len(data)}")

    # Find Baleares series
    extracted = {}
    for item in data:
        cod = item.get("COD", "")
        if cod in BALEARES_SERIES:
            name = BALEARES_SERIES[cod]
            records = []
            for obs in item.get("Data", []):
                year, month = timestamp_to_year_month(obs.get("Fecha", 0))
                valor = obs.get("Valor")
                records.append({
                    "year": year,
                    "month": month,
                    f"{name}": valor,
                })
            extracted[name] = records
            print(f"  {cod}: {name} ({len(records)} obs)")

    # Merge into single dataframe
    all_dfs = []
    for name, records in extracted.items():
        df = pd.DataFrame(records)
        all_dfs.append(df.set_index(["year", "month"]))

    merged = pd.concat(all_dfs, axis=1).reset_index()
    merged = merged.sort_values(["year", "month"]).dropna(how="all")
    print(f"\n  Total registros combinados: {len(merged)}")
    print(f"  Periodo: {merged['year'].min()}-{merged['month'].min()} a "
          f"{merged['year'].max()}-{merged['month'].max()}")
    print(f"  Columnas: {list(merged.columns)}")

    return merged

def load_ine_csv():
    """Fallback: load existing INE CSV files if download fails."""
    files = list(OUTPUT_DIR.glob("*.csv"))
    if not files:
        return None
    dfs = []
    for f in files:
        df = pd.read_csv(f, delimiter=";", encoding="utf-8")
        df["year"] = df["Período"].str[:4].astype(int)
        df["month"] = df["Período"].str.extract(r"Mes(\d+)").astype(int)
        df = df.rename(columns={"Valor": f.name.replace(".csv", "")})
        dfs.append(df[["year", "month", f.name.replace(".csv", "")]])
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on=["year", "month"], how="outer")
    return merged.sort_values(["year", "month"])

if __name__ == "__main__":
    print("=" * 70)
    print("INE DATA EXTRACTION + MODEL TEST")
    print("=" * 70)

    # 1. Extract INE data
    print("\n[1] Extrayendo datos INE Baleares...")
    ine_data = download_and_extract()

    # Save extracted data
    out_path = OUTPUT_DIR / "baleares_occupation_data.csv"
    ine_data.to_csv(out_path, index=False)
    print(f"  Guardado: {out_path}")

    # 2. Load training data
    print("\n[2] Cargando dataset de entrenamiento...")
    df_train = pd.read_csv(TRAIN_PATH)
    target = "avg_price_per_room"
    print(f"  Shape: {df_train.shape}")
    print(f"  Periodo: {df_train['arrival_year'].min()}-{df_train['arrival_month'].min()} a "
          f"{df_train['arrival_year'].max()}-{df_train['arrival_month'].max()}")

    # 3. Merge INE data with training data
    print("\n[3] Fusionando datos INE con training...")
    df_merged = df_train.merge(
        ine_data,
        left_on=["arrival_year", "arrival_month"],
        right_on=["year", "month"],
        how="left",
    )
    pre_rows = len(df_merged)
    df_merged = df_merged.dropna(subset=[c for c in ine_data.columns if c not in ["year", "month"]])
    post_rows = len(df_merged)
    print(f"  Filas antes de merge: {pre_rows}")
    print(f"  Filas después de merge (sin NaN): {post_rows}")
    print(f"  Filas perdidas por falta de datos INE: {pre_rows - post_rows}")

    # 4. Train baseline (27 features, NoScaler)
    print("\n[4] Entrenando BASELINE (27f, NoScaler)...")
    X = df_train.drop(columns=[target])
    y = df_train[target]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    m_base = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
    m_base.fit(X_tr.values, y_tr)
    p_te_base = m_base.predict(X_te.values)
    baseline_rmse = np.sqrt(mean_squared_error(y_te, p_te_base))
    baseline_r2 = r2_score(y_te, p_te_base)
    print(f"  RMSE={baseline_rmse:.4f}, R2={baseline_r2:.4f}")

    # 5. Train with INE features
    print("\n[5] Entrenando con INE features (NoScaler)...")
    ine_features = [c for c in ine_data.columns if c not in ["year", "month"]]
    print(f"  Features INE a añadir: {ine_features}")
    
    X_ine = df_merged.drop(columns=[target] + ine_features)
    y_ine = df_merged[target]
    X_ine_fe = df_merged[ine_features]
    
    # Check coverage
    print(f"  Coverage stats:")
    for col in ine_features:
        non_null = df_merged[col].notna().sum()
        print(f"    {col}: {non_null}/{len(df_merged)} ({non_null/len(df_merged)*100:.1f}%)")
    
    # Merge original features with INE features
    X_combined = pd.concat([X_ine, X_ine_fe], axis=1)
    print(f"  Features totales: {X_combined.shape[1]} (originales {X_ine.shape[1]} + INE {len(ine_features)})")
    
    # Split
    X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
        X_combined, y_ine, test_size=0.2, random_state=42, shuffle=False
    )
    
    m_ine = ElasticNet(alpha=0.024, l1_ratio=0.725, max_iter=10000, random_state=42)
    m_ine.fit(X_tr_c.values, y_tr_c)
    p_tr_ine = m_ine.predict(X_tr_c.values)
    p_te_ine = m_ine.predict(X_te_c.values)
    
    ine_rmse = np.sqrt(mean_squared_error(y_te_c, p_te_ine))
    ine_r2 = r2_score(y_te_c, p_te_ine)
    ine_gap = abs(r2_score(y_tr_c, p_tr_ine) - r2_score(y_te_c, p_te_ine))
    
    print(f"  Train RMSE={np.sqrt(mean_squared_error(y_tr_c, p_tr_ine)):.4f}, R2={r2_score(y_tr_c, p_tr_ine):.4f}")
    print(f"  Test  RMSE={ine_rmse:.4f}, R2={ine_r2:.4f}")
    print(f"  Gap R2={ine_gap:.4f}")
    
    # Feature importance of INE features
    print("\n[6] Coeficientes de features INE:")
    coefs = pd.DataFrame({
        'feature': X_combined.columns,
        'coef': m_ine.coef_,
    })
    ine_coefs = coefs[coefs['feature'].isin(ine_features)]
    print(ine_coefs.to_string(index=False))

    # 7. Comparison
    print("\n" + "=" * 70)
    print("COMPARACIÓN FINAL")
    print("=" * 70)
    print(f"{'Config':<50} {'Test RMSE':<12} {'Test R2':<12} {'Gap R2':<12}")
    print("-" * 70)
    print(f"{'Baseline (27f, NoScaler)':<50} {baseline_rmse:<12.4f} {baseline_r2:<12.4f} {'N/A':<12}")
    print(f"{'+ INE occupation features':<50} {ine_rmse:<12.4f} {ine_r2:<12.4f} {ine_gap:<12.4f}")
    delta_rmse = ((baseline_rmse - ine_rmse) / baseline_rmse) * 100
    delta_r2 = ine_r2 - baseline_r2
    print(f"{'Delta (%)':<50} {delta_rmse:<+12.2f}% {delta_r2:<+12.4f} {'':<12}")
    
    print("\n" + "=" * 70)
    if ine_rmse < baseline_rmse:
        print(f"✅ INE features MEJORAN el modelo: RMSE {baseline_rmse:.2f} → {ine_rmse:.2f}")
    else:
        print(f"❌ INE features NO mejoran el modelo: RMSE {baseline_rmse:.2f} → {ine_rmse:.2f}")
