"""
Parse INE API response and extract Baleares hotel data
"""
import sys, json, csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

API_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2066"
OUTPUT_DIR = Path("data/v2_market/raw/ine")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Descargando datos INE...")
r = requests.get(API_URL, timeout=120)
data = r.json()
print(f"Total series en tabla 2066: {len(data)}")

# Analyze structure
print("\n=== ESTRUCTURA DE DATOS ===")
for i, item in enumerate(data[:5]):
    print(f"\nSerie {i}:")
    for k, v in item.items():
        if k == "Data":
            print(f"  Data: {len(v)} observaciones")
            if v:
                print(f"    Primeros 3: {v[:3]}")
        else:
            print(f"  {k}: {v}")

# Find Baleares-related series
print("\n=== SERIES RELACIONADAS CON BALEARES ===")
for i, item in enumerate(data):
    nombre = item.get("Nombre", "")
    cod = item.get("COD", "")
    if "balear" in nombre.lower() or "baleares" in nombre.lower():
        print(f"\nSerie {i}: COD={cod}, Nombre={nombre}")
        data_pts = item.get("Data", [])
        print(f"  Observaciones: {len(data_pts)}")
        if data_pts:
            print(f"  Primeras 5:")
            for d in data_pts[:5]:
                print(f"    {d}")

# Find occupancy-related series
print("\n=== SERIES DE OCUPACIÓN ===")
for i, item in enumerate(data):
    nombre = item.get("Nombre", "")
    if "ocupación" in nombre.lower() or "grado" in nombre.lower() or "ocupacion" in nombre.lower():
        if "balear" in nombre.lower() or "nacional" in nombre.lower():
            print(f"Serie {i}: {nombre}")
            data_pts = item.get("Data", [])
            print(f"  Observaciones: {len(data_pts)}")
            if data_pts:
                print(f"  Primeros 3: {data_pts[:3]}")

# Find price-related series  
print("\n=== SERIES DE PRECIOS ===")
for i, item in enumerate(data):
    nombre = item.get("Nombre", "")
    if "precio" in nombre.lower() or "adr" in nombre.lower() or "ingreso" in nombre.lower() or "tarifa" in nombre.lower():
        if "balear" in nombre.lower() or "hotel" in nombre.lower():
            print(f"Serie {i}: {nombre}")
            data_pts = item.get("Data", [])
            print(f"  Observaciones: {len(data_pts)}")
            if data_pts:
                print(f"  Primeros 3: {data_pts[:3]}")
