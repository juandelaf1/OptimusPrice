"""
Download INE Hotel Occupancy Data for Baleares
Uses requests to fetch JSON from INE API and filter for Illes Balears
INE Table 2066: Encuesta de Ocupación Hotelera
"""
import sys, os, json, csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import requests
except ImportError:
    print("ERROR: requests no instalado. pip install requests")
    sys.exit(1)

OUTPUT_DIR = Path("data/v2_market/raw/ine")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# INE API endpoint for table 2066 (Hotel Occupancy)
# This returns all data in JSON-stat format
API_URL = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2066"

def download_data():
    print(f"Descargando datos INE desde {API_URL}...")
    try:
        r = requests.get(API_URL, timeout=120, stream=True)
        r.raise_for_status()
        data = r.json()
        print(f"  Descargados {len(json.dumps(data))} bytes")
        return data
    except Exception as e:
        print(f"  Error descargando: {e}")
        return None

def parse_ine_data(data):
    """Parse INE JSON and extract Baleares data."""
    if not data:
        return None, None

    # INE returns data in a structure with metadata
    # Try to find the relevant data structure
    occupancy_rows = []
    price_rows = []

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "Data" in data:
        items = data["Data"]
    else:
        print(f"  Estructura inesperada: tipo={type(data)}")
        # Try to explore
        if isinstance(data, dict):
            print(f"  Keys: {list(data.keys())[:10]}")
        items = []

    # Parse each entry
    for item in items:
        if not isinstance(item, dict):
            continue
        # Try common INE formats
        periodo = item.get("Periodo") or item.get("periodo") or item.get("PK", {}).get("Periodo", "")
        valor = item.get("Valor") or item.get("valor")
        ccaa = item.get("ComunidadAutonoma") or item.get("CCAA") or item.get("PK", {}).get("ComunidadAutonoma", "")
        tipo = item.get("TipoAlojamiento") or item.get("Tipo") or item.get("PK", {}).get("TipoAlojamiento", "")

        if not periodo or valor is None:
            continue

        # Filter for Baleares
        if "Baleares" not in str(ccaa) and "balear" not in str(ccaa).lower():
            continue

        # Check if it's occupancy or price based on column names
        # If we don't know, store as occupancy (most common)
        row = {"Periodo": periodo, "CCAA": ccaa, "Tipo": tipo, "Valor": valor}
        occupancy_rows.append(row)

    return occupancy_rows, None

def parse_json_stat(data):
    """Parse JSON-stat format (common in INE API)."""
    if not data or "value" not in data:
        return None

    # JSON-stat format
    values = data.get("value", {})
    dimensions = data.get("dimension", {})
    status_dim = data.get("status", {}).get("dimension", {})

    # Try to extract dimension labels
    periodo_labels = {}
    ccaa_labels = {}
    tipo_labels = {}

    for dim_name, dim_obj in dimensions.items():
        labels = dim_obj.get("category", {}).get("label", {})
        if "periodo" in dim_name.lower() or "tiempo" in dim_name.lower():
            periodo_labels = labels
        elif "ccaa" in dim_name.lower() or "comunidad" in dim_name.lower():
            ccaa_labels = labels
        elif "tipo" in dim_name.lower() or "alojamiento" in dim_name.lower():
            tipo_labels = labels

    # Find the index for Baleares
    balears_id = None
    for k, v in ccaa_labels.items():
        if "balears" in v.lower() or "baleares" in v.lower():
            balears_id = k
            break

    if balears_id is None:
        print("  No se encontraron datos para Illes Balears")
        return None

    print(f"  ID para Illes Balears: {balears_id}")
    print(f"  Total periodos: {len(periodo_labels)}")
    print(f"  Total tipos: {len(tipo_labels)}")

    return values

def save_csv(rows, filename):
    if not rows:
        print(f"  No hay datos para {filename}")
        return False
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
    print(f"  Guardado: {filepath} ({len(rows)} filas)")
    return True

def verify_extracted_data(rows):
    """Verify and summarize the extracted data."""
    if not rows:
        return
    print(f"\n  Registros: {len(rows)}")
    periodos = set(r["Periodo"] for r in rows)
    tipos = set(r["Tipo"] for r in rows)
    print(f"  Periodos: {min(periodos)[:7]}...{max(periodos)[:7]} ({len(periodos)} meses)")
    print(f"  Tipos de alojamiento: {tipos}")
    valores = [float(r["Valor"]) for r in rows if r["Valor"]]
    if valores:
        print(f"  Valor min: {min(valores):.1f}, max: {max(valores):.1f}, mean: {sum(valores)/len(valores):.1f}")

if __name__ == "__main__":
    print("=" * 60)
    print("DESCARGA DATOS INE - OCUPACIÓN HOTELERA BALEARES")
    print("=" * 60)

    # Method 1: Try direct JSON endpoint
    print("\n[Método 1] API estándar INE...")
    data = download_data()
    if data:
        print(f"  Tipo de datos: {type(data).__name__}")
        if isinstance(data, list):
            print(f"  Tamaño de lista: {len(data)}")
            if len(data) > 0:
                print(f"  Primer item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'no dict'}")
        elif isinstance(data, dict):
            print(f"  Keys: {list(data.keys())[:15]}")
            if "value" in data:
                print(f"  JSON-stat format detected ({len(data['value'])} values)")
                vals = data["value"]
                # Try to find Baleares data by looking at values
                dims = data.get("dimension", {})
                for dk, dv in dims.items():
                    cats = dv.get("category", {})
                    labels = cats.get("label", {})
                    print(f"  Dimensión '{dk}': {len(labels)} categorías")
                    for lid, lname in list(labels.items())[:5]:
                        print(f"    {lid}: {lname}")

    # The data files already exist, let's check them
    print(f"\n[Método 2] Verificar datos locales...")
    files = list(OUTPUT_DIR.glob("*.csv"))
    if files:
        for f in files:
            size = f.stat().st_size
            print(f"  {f.name}: {size:,} bytes")
    else:
        print("  No hay archivos CSV locales")

    # Check if we have any results to save
    # Save a sample of what we'd extract
    print("\n" + "=" * 60)
    print("Los datos INE existentes son:")
    for f in sorted(OUTPUT_DIR.glob("*.csv")):
        with open(f, encoding="utf-8") as fh:
            lines = fh.readlines()
            print(f"  {f.name}: {len(lines)} líneas")
            if len(lines) > 1:
                print(f"    Encabezados: {lines[0].strip()}")
                print(f"    Primeras filas:")
                for line in lines[1:4]:
                    print(f"      {line.strip()}")
