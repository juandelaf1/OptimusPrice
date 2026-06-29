#!/usr/bin/env python3
"""
Generate realistic tourism data for Mallorca based on real patterns.
This creates CSV files that simulate INE and Google Trends data.
Use this until real data sources are connected.
"""

import csv
import random
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
INE_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "ine"
GTRENDS_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "google_trends"
AIRBNB_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "airbnb"

INE_DIR.mkdir(parents=True, exist_ok=True)
GTRENDS_DIR.mkdir(parents=True, exist_ok=True)
AIRBNB_DIR.mkdir(parents=True, exist_ok=True)


def generate_ine_occupancy():
    """Generate INE-style hotel occupancy data for Balearic Islands (2015-2025)."""
    filepath = INE_DIR / "ine_ocupacion_hoteleras_baleares.csv"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Período', 'Comunidad Autónoma', 'Tipo de alojamiento', 'Valor'])
        
        for year in range(2015, 2026):
            for month in range(1, 13):
                # Real occupancy pattern for Balearic Islands
                # Source: INE real patterns (2015-2023 average)
                base_occupancy = {
                    1: 28, 2: 25, 3: 38, 4: 52,
                    5: 68, 6: 82, 7: 92, 8: 93,
                    9: 80, 10: 62, 11: 35, 12: 30,
                }
                
                # COVID impact (2020-2021)
                covid_factor = 1.0
                if year == 2020:
                    if month in [3, 4, 5, 6]:
                        covid_factor = 0.3
                    elif month in [7, 8]:
                        covid_factor = 0.6
                    else:
                        covid_factor = 0.5
                elif year == 2021:
                    if month in [1, 2, 3]:
                        covid_factor = 0.5
                    elif month in [4, 5, 6]:
                        covid_factor = 0.7
                    else:
                        covid_factor = 0.85
                
                # Recovery trend (2022-2025)
                recovery = 1.0
                if year >= 2022:
                    recovery = 1.0 + (year - 2022) * 0.02
                
                # Natural variation
                noise = random.uniform(-3, 3)
                
                occupancy = min(98, max(15, base_occupancy[month] * covid_factor * recovery + noise))
                
                period = f"{year}Mes{month:02d}"
                writer.writerow([period, 'Illes Balears', 'Hoteleros', f"{occupancy:.1f}"])
    
    print(f"Generated: {filepath}")
    return filepath


def generate_ine_prices():
    """Generate INE-style average hotel price data for Balearic Islands (2015-2025)."""
    filepath = INE_DIR / "ine_precios_medios_baleares.csv"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Período', 'Comunidad Autónoma', 'Tipo de alojamiento', 'Valor'])
        
        for year in range(2015, 2026):
            for month in range(1, 13):
                # Real price pattern for Balearic Islands (EUR/night)
                # Source: INE real patterns (2015-2023 average)
                base_price = {
                    1: 75, 2: 70, 3: 85, 4: 105,
                    5: 130, 6: 155, 7: 180, 8: 185,
                    9: 150, 10: 115, 11: 80, 12: 72,
                }
                
                # Inflation adjustment (3% annual)
                inflation = 1.0 + (year - 2015) * 0.03
                
                # COVID impact on prices
                covid_factor = 1.0
                if year == 2020:
                    covid_factor = 0.7
                elif year == 2021:
                    covid_factor = 0.85
                
                noise = random.uniform(-5, 5)
                
                price = max(50, base_price[month] * inflation * covid_factor + noise)
                
                period = f"{year}Mes{month:02d}"
                writer.writerow([period, 'Illes Balears', 'Hoteleros', f"{price:.1f}"])
    
    print(f"Generated: {filepath}")
    return filepath


def generate_gtrends_data():
    """Generate Google Trends-style search volume data for Mallorca queries."""
    filepath = GTRENDS_DIR / "mallorca_tourism_trends.csv"
    
    queries = [
        'Mallorca hotels',
        'Mallorca apartments',
        'Mallorca tourism',
        'Mallorca weather',
        'Alcudia hotels',
        'Palma de Mallorca hotels',
        'Magaluf hotels',
        'Mallorca villa rental',
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Month'] + queries)
        
        for year in range(2020, 2026):
            for month in range(1, 13):
                # Seasonal search pattern
                seasonal = {
                    1: 25, 2: 20, 3: 35, 4: 55,
                    5: 75, 6: 90, 7: 100, 8: 95,
                    9: 70, 10: 50, 11: 30, 12: 25,
                }
                
                # Trend growth (5% annual)
                growth = 1.0 + (year - 2020) * 0.05
                
                row = [f"{year}-{month:02d}-01"]
                for query in queries:
                    # Different queries have different volumes
                    query_factor = {
                        'Mallorca hotels': 1.0,
                        'Mallorca apartments': 0.8,
                        'Mallorca tourism': 0.9,
                        'Mallorca weather': 0.6,
                        'Alcudia hotels': 0.4,
                        'Palma de Mallorca hotels': 0.5,
                        'Magaluf hotels': 0.3,
                        'Mallorca villa rental': 0.35,
                    }
                    
                    noise = random.uniform(-3, 3)
                    value = min(100, max(0, seasonal[month] * growth * query_factor[query] + noise))
                    row.append(f"{value:.0f}")
                
                writer.writerow(row)
    
    print(f"Generated: {filepath}")
    return filepath


def generate_airbnb_prices():
    """Generate Airbnb-style pricing data for Mallorca segments."""
    filepath = AIRBNB_DIR / "airbnb_mallorca_prices.csv"
    
    segments = {
        'palma_urbano': {'center_lat': 39.5696, 'center_lng': 2.6502, 'avg_price': 95},
        'playa_costa': {'center_lat': 39.5000, 'center_lng': 2.8000, 'avg_price': 120},
        'magaluf_party': {'center_lat': 39.5089, 'center_lng': 2.4447, 'avg_price': 75},
        'alcudia_family': {'center_lat': 39.8266, 'center_lng': 3.1215, 'avg_price': 110},
        'interior_rural': {'center_lat': 39.7000, 'center_lng': 2.9000, 'avg_price': 140},
        'luxury_villas': {'center_lat': 39.5500, 'center_lng': 2.4500, 'avg_price': 350},
    }
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'listing_id', 'segment', 'property_type', 'bedrooms',
            'price_per_night', 'min_nights', 'latitude', 'longitude',
            'review_scores_rating', 'number_of_reviews',
        ])
        
        listing_id = 1
        for segment, info in segments.items():
            # Generate 30 listings per segment
            for i in range(30):
                # Seasonal price variation
                month = random.randint(1, 12)
                seasonal = {
                    1: 0.7, 2: 0.65, 3: 0.8, 4: 0.95,
                    5: 1.1, 6: 1.25, 7: 1.4, 8: 1.4,
                    9: 1.15, 10: 0.9, 11: 0.75, 12: 0.7,
                }
                
                bedrooms = random.choice([1, 1, 2, 2, 2, 3, 3, 4])
                bedroom_factor = 1.0 + (bedrooms - 1) * 0.3
                
                price = info['avg_price'] * seasonal[month] * bedroom_factor * random.uniform(0.8, 1.2)
                
                lat = info['center_lat'] + random.uniform(-0.02, 0.02)
                lng = info['center_lng'] + random.uniform(-0.02, 0.02)
                
                prop_type = 'apartment' if segment in ['palma_urbano', 'magaluf_party'] else \
                           'villa' if segment == 'luxury_villas' else \
                           'house' if segment == 'interior_rural' else 'apartment'
                
                writer.writerow([
                    f'abnb_{listing_id:04d}',
                    segment,
                    prop_type,
                    bedrooms,
                    f"{price:.0f}",
                    2 if segment == 'luxury_villas' else 1,
                    f"{lat:.4f}",
                    f"{lng:.4f}",
                    f"{random.uniform(3.5, 5.0):.1f}",
                    random.randint(5, 200),
                ])
                listing_id += 1
    
    print(f"Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=== Generating Realistic Tourism Data for Mallorca ===\n")
    
    generate_ine_occupancy()
    generate_ine_prices()
    generate_gtrends_data()
    generate_airbnb_prices()
    
    print("\n=== Data Generation Complete ===")
    print(f"Files created in: {BASE_DIR / 'data' / 'v2_market' / 'raw'}")
