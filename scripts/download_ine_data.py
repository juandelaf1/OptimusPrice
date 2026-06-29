#!/usr/bin/env python3
"""
Download Real INE Tourism Data
Guide and script for downloading real data from Spain's INE statistics institute.

INE provides free CSV data about tourism in Spain.
Website: https://www.ine.es
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

INE_DATA_DIR = Path("data/v2_market/raw/ine")

# INE dataset URLs and descriptions
INE_DATASETS = {
    "ocupacion_hotelera": {
        "description": "Encuesta de Ocupación Hotelera (Hotel Occupancy Survey)",
        "url": "https://www.ine.es/jaxiT3/Tabla.htm?t=3996",
        "filename": "ine_ocupacion_hoteleras_baleares.csv",
        "instructions": """
Para descargar estos datos:
1. Ve a https://www.ine.es/jaxiT3/Tabla.htm?t=3996
2. Selecciona 'Islas Baleares' en Comunidad Autónoma
3. Selecciona 'Hoteleros' en Tipo de alojamiento
4. Haz clic en 'Descargar' > 'CSV'
5. Guarda el archivo como: data/v2_market/raw/ine/ine_ocupacion_hoteleras_baleares.csv
""",
    },
    "precios_medios": {
        "description": "Encuesta de Ocupación Hotelera - Precios medios (Average Prices)",
        "url": "https://www.ine.es/jaxiT3/Tabla.htm?t=3997",
        "filename": "ine_precios_medios_baleares.csv",
        "instructions": """
Para descargar estos datos:
1. Ve a https://www.ine.es/jaxiT3/Tabla.htm?t=3997
2. Selecciona 'Islas Baleares' en Comunidad Autónoma
3. Selecciona 'Hoteleros' en Tipo de alojamiento
4. Haz clic en 'Descargar' > 'CSV'
5. Guarda el archivo como: data/v2_market/raw/ine/ine_precios_medios_baleares.csv
""",
    },
}


def check_data_status():
    """Check status of INE data files."""
    print("=== Estado de Datos INE ===\n")
    
    for key, dataset in INE_DATASETS.items():
        filepath = INE_DATA_DIR / dataset['filename']
        exists = filepath.exists()
        size = filepath.stat().st_size if exists else 0
        
        status = "EXISTS" if exists else "MISSING"
        print(f"[{status}] {dataset['filename']}")
        print(f"    {dataset['description']}")
        if exists:
            print(f"    Size: {size:,} bytes")
        print(f"    URL: {dataset['url']}")
        print()
    
    return all((INE_DATA_DIR / d['filename']).exists() for d in INE_DATASETS.values())


def print_download_guide():
    """Print guide for downloading INE data."""
    print("\n=== Guía de Descarga de Datos INE ===\n")
    
    for key, dataset in INE_DATASETS.items():
        print(f"--- {dataset['description']} ---")
        print(dataset['instructions'])
        print()


def download_with_requests():
    """Try to download data using requests (if available)."""
    try:
        import requests
    except ImportError:
        print("requests no instalado. Instala con: pip install requests")
        return False
    
    print("Intentando descargar datos INE...")
    print("NOTA: INE puede requerir interacción manual para algunos datasets.")
    print()
    
    # Note: INE's API requires specific parameters
    # This is a simplified version
    print("Para datos completos, usa la guía manual:")
    print_download_guide()
    
    return False


if __name__ == "__main__":
    print("=== INE Tourism Data Downloader ===\n")
    
    # Check current status
    all_complete = check_data_status()
    
    if all_complete:
        print("Todos los archivos de datos INE están presentes.")
        print("Puedes proceder a ingestar los datos con:")
        print("  python -m src.v2_pipeline.ine_ingester")
    else:
        print("Faltan archivos de datos INE.")
        print()
        print_download_guide()
        
        print("\n¿Deseas intentar descarga automática? (s/n): ", end="")
        response = input().strip().lower()
        
        if response == 's':
            download_with_requests()
