#!/usr/bin/env python3
"""
V2 Pipeline — INE Data Ingester
Parses and ingests data from Spain's Instituto Nacional de Estadística (INE).
INE provides free CSV data about tourism: occupancy, prices, demand.
"""

import csv
import re
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

from .market_db import MarketIntelligenceDB


BASE_DIR = Path(__file__).resolve().parent.parent.parent
INE_DATA_DIR = BASE_DIR / "data" / "v2_market" / "raw" / "ine"

# INE column name mappings (Spanish → English)
INE_COLUMN_MAP = {
    'Período': 'period',
    'Tipo de alojamiento': 'accommodation_type',
    'Comunidad Autónoma': 'region',
    'Provincia': 'province',
    'Mes': 'month',
    'Año': 'year',
    'Valor': 'value',
    'Total': 'total',
    'Nacional': 'national',
    'Baleares': 'baleares',
    'Illes Balears': 'baleares',
    'Palma': 'palma',
    'Mallorca': 'mallorca',
    'Menorca': 'menorca',
    'Ibiza': 'ibiza',
}

# INE dataset identifiers for tourism
INE_DATASETS = {
    'occupancy': {
        'description': 'Hotel occupancy rates by region',
        'expected_columns': ['Período', 'Comunidad Autónoma', 'Tipo de alojamiento', 'Valor'],
    },
    'prices': {
        'description': 'Average hotel prices by region',
        'expected_columns': ['Período', 'Comunidad Autónoma', 'Tipo de alojamiento', 'Valor'],
    },
    'demand': {
        'description': 'Tourist demand indicators',
        'expected_columns': ['Período', 'Comunidad Autónoma', 'Valor'],
    },
}


class INEDataIngester:
    """Parses and ingests INE tourism data."""

    def __init__(self, db: Optional[MarketIntelligenceDB] = None):
        self.db = db or MarketIntelligenceDB()
        INE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def parse_ine_csv(self, filepath: Path) -> List[Dict]:
        """Parse an INE CSV file and return normalized records."""
        records = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Handle INE's semi-colon separated format
        lines = content.strip().split('\n')
        if not lines:
            return records

        # Detect delimiter
        if ';' in lines[0]:
            delimiter = ';'
        elif ',' in lines[0]:
            delimiter = ','
        else:
            delimiter = '\t'

        # Parse header
        header_line = lines[0]
        # Remove footnote markers like "[1]", "[2]" from headers
        header_line = re.sub(r'\[\d+\]', '', header_line)
        headers = [h.strip() for h in header_line.split(delimiter)]

        # Parse data rows
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip() or line.startswith('Fuente') or line.startswith('Nota'):
                continue
            # Remove footnote markers
            line = re.sub(r'\[\d+\]', '', line)
            values = [v.strip() for v in line.split(delimiter)]
            if len(values) != len(headers):
                continue

            row = dict(zip(headers, values))
            record = self._normalize_row(row, filepath.stem)
            if record:
                records.append(record)

        return records

    def _normalize_row(self, row: Dict, source_file: str) -> Optional[Dict]:
        """Normalize an INE row to our schema."""
        # Extract period (year-month)
        period_str = row.get('Período', row.get('period', ''))
        year, month = self._parse_period(period_str)
        if not year or not month:
            return None

        # Extract value
        value_str = row.get('Valor', row.get('Total', row.get('value', '')))
        value = self._parse_number(value_str)
        if value is None:
            return None

        # Extract region
        region_raw = row.get('Comunidad Autónoma', row.get('region', ''))
        region, subregion = self._parse_region(region_raw)

        # Extract accommodation type
        accom_raw = row.get('Tipo de alojamiento', row.get('accommodation_type', ''))
        accommodation_type = self._parse_accommodation(accom_raw)

        # Detect data type from filename or content
        data_type = self._detect_data_type(source_file, row)

        return {
            'year': year,
            'month': month,
            'region': region,
            'subregion': subregion,
            'accommodation_type': accommodation_type,
            'value': value,
            'data_type': data_type,
            'source_file': source_file,
        }

    def _parse_period(self, period_str: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse period string to year and month."""
        period_str = str(period_str).strip()
        
        # Format: "2024Mes01" (INE standard)
        match = re.match(r'(\d{4})[Mm]es(\d{1,2})', period_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            if 1 <= month <= 12:
                return year, month
        
        # Format: "2024-M01" or "2024-M1"
        match = re.match(r'(\d{4})-?[Mm](\d{1,2})', period_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            if 1 <= month <= 12:
                return year, month
        
        # Format: "202401" (YYYYMM)
        match = re.match(r'(\d{4})(\d{2})', period_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            if 1 <= month <= 12:
                return year, month
        
        # Fallback: extract year and month separately
        year_match = re.search(r'(\d{4})', period_str)
        month_match = re.search(r'(\d{1,2})', period_str.replace(str(year_match.group(1)) if year_match else '', ''))
        
        if year_match:
            year = int(year_match.group(1))
            month = int(month_match.group(1)) if month_match else 1
            if 1 <= month <= 12:
                return year, month
        
        return None, None

    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse INE number format."""
        if not value_str or value_str.strip() in ('', '-', '...', 'N/A', 'null'):
            return None
        value_str = str(value_str).strip()
        
        # Check if it's a decimal number with comma (Spanish format: 28,8)
        if ',' in value_str and '.' not in value_str:
            # Spanish format: comma is decimal separator
            value_str = value_str.replace(',', '.')
        elif '.' in value_str and ',' in value_str:
            # Could be: 1.234,56 (Spanish) or 1,234.56 (English)
            # If comma comes after dot, it's Spanish: 1.234,56
            if value_str.rindex(',') > value_str.rindex('.'):
                value_str = value_str.replace('.', '').replace(',', '.')
            else:
                # English format: 1,234.56
                value_str = value_str.replace(',', '')
        
        try:
            return float(value_str)
        except ValueError:
            return None

    def _parse_region(self, region_raw: str) -> Tuple[str, Optional[str]]:
        """Parse INE region to our region/subregion format."""
        region_raw = str(region_raw).strip()
        region_lower = region_raw.lower()
        
        # Handle Spanish/Valencian names for Balearic Islands
        if 'baleares' in region_lower or 'illes balears' in region_lower:
            return 'baleares', None
        if 'palma' in region_lower:
            return 'mallorca', 'palma'
        if 'mallorca' in region_lower:
            return 'mallorca', None
        if 'menorca' in region_lower:
            return 'mallorca', 'menorca'
        if 'ibiza' in region_lower:
            return 'mallorca', 'ibiza'
        if 'formentera' in region_lower:
            return 'mallorca', 'formentera'
        return 'mallorca', None

    def _parse_accommodation(self, accom_raw: str) -> Optional[str]:
        """Parse INE accommodation type to our format."""
        accom_raw = str(accom_raw).strip().lower()
        if 'hotel' in accom_raw:
            return 'hotel'
        if 'apartamento' in accom_raw or 'apart' in accom_raw:
            return 'apartment'
        if 'villa' in accom_raw or 'casa' in accom_raw:
            return 'villa'
        if 'rural' in accom_raw or 'agroturismo' in accom_raw:
            return 'rural_house'
        return None

    def _detect_data_type(self, source_file: str, row: Dict) -> str:
        """Detect if this is occupancy, price, or demand data."""
        source_lower = source_file.lower()
        if 'ocupacion' in source_lower or 'occupancy' in source_lower:
            return 'occupancy'
        if 'precio' in source_lower or 'price' in source_lower or 'precios' in source_lower:
            return 'price'
        if 'demanda' in source_lower or 'demand' in source_lower:
            return 'demand'
        # Check row content
        accom_raw = row.get('Tipo de alojamiento', row.get('accommodation_type', '')).lower()
        if 'hotel' in accom_raw:
            return 'occupancy'
        return 'unknown'

    def ingest_csv(self, filepath: Path) -> dict:
        """Parse an INE CSV and insert into database."""
        records = self.parse_ine_csv(filepath)
        if not records:
            return {'inserted': 0, 'message': 'No valid records found'}

        inserted = 0
        for record in records:
            try:
                if record['data_type'] == 'occupancy':
                    # Convert percentage (0-100) to decimal (0-1)
                    occ_value = record['value']
                    if occ_value > 1.0:  # Assuming percentage format
                        occ_value = occ_value / 100.0
                    self.db.insert_demand_signal({
                        'signal_date': date(record['year'], record['month'], 1),
                        'region': record['region'],
                        'subregion': record['subregion'],
                        'occupancy_estimate': min(1.0, max(0.0, occ_value)),
                        'source': 'ine',
                        'source_metric': f"occupancy_{record.get('accommodation_type', 'all')}",
                    })
                elif record['data_type'] == 'price':
                    # Calculate price index relative to 2015 baseline (avg ~100 EUR)
                    baseline_price = 100.0
                    price_index = 100.0 * (record['value'] / baseline_price)
                    self.db.insert_market_index({
                        'index_date': date(record['year'], record['month'], 1),
                        'period': 'monthly',
                        'region': record['region'],
                        'subregion': record['subregion'],
                        'segment': 'playa_costa',
                        'accommodation_type': record.get('accommodation_type'),
                        'price_index': round(price_index, 1),
                        'avg_price': round(record['value'], 2),
                        'sample_size': 1,
                        'confidence_level': 'high',
                        'source': 'ine',
                    })
                inserted += 1
            except Exception as e:
                pass
        return {'inserted': inserted, 'total_parsed': len(records)}

    def ingest_directory(self) -> dict:
        """Ingest all CSV files in the INE data directory."""
        results = []
        for csv_file in INE_DATA_DIR.glob('*.csv'):
            result = self.ingest_csv(csv_file)
            results.append({'file': csv_file.name, **result})
        
        # Create seasonality index from occupancy data
        self._create_seasonality_from_occupancy()
        
        return {'files_processed': len(results), 'results': results}
    
    def _create_seasonality_from_occupancy(self):
        """Create seasonality index from aggregated occupancy data."""
        # Aggregate occupancy by month across all years
        monthly_occupancy = {}
        with self.db._conn() as conn:
            rows = conn.execute("""
                SELECT signal_date, occupancy_estimate 
                FROM demand_signals 
                WHERE source = 'ine' AND source_metric LIKE 'occupancy_%'
            """).fetchall()
            
            for row in rows:
                signal_date = row['signal_date']
                if isinstance(signal_date, str):
                    from datetime import datetime
                    signal_date = datetime.strptime(signal_date, '%Y-%m-%d').date()
                month = signal_date.month
                if month not in monthly_occupancy:
                    monthly_occupancy[month] = []
                monthly_occupancy[month].append(row['occupancy_estimate'])
        
        # Calculate average occupancy per month and create seasonality index
        if monthly_occupancy:
            # Calculate overall average occupancy (should be 0-1)
            all_values = [v for values in monthly_occupancy.values() for v in values]
            avg_occupancy_all = sum(all_values) / len(all_values) if all_values else 0.5
            
            for month in range(1, 13):
                if month in monthly_occupancy and monthly_occupancy[month]:
                    avg_occ = sum(monthly_occupancy[month]) / len(monthly_occupancy[month])
                    # Seasonality factor: 1.0 = average, >1 = peak, <1 = low
                    factor = avg_occ / avg_occupancy_all if avg_occupancy_all > 0 else 1.0
                    
                    self.db.insert_seasonality({
                        'month': month,
                        'day_of_week': None,
                        'region': 'mallorca',
                        'segment': 'playa_costa',
                        'seasonality_factor': round(factor, 3),
                        'avg_occupancy': round(avg_occ, 3),
                        'years_of_data': len(monthly_occupancy[month]),
                        'data_sources': 'ine_occupancy',
                    })

    def create_sample_data(self):
        """Create sample INE-like data for testing."""
        sample_records = []
        # Simulate 24 months of hotel occupancy data for Mallorca
        for year in range(2020, 2025):
            for month in range(1, 13):
                # Seasonal pattern: peak in summer
                base_occupancy = 65
                seasonal = 25 * (1 if month in [7, 8] else 0.6 if month in [6, 9] else 0.3 if month in [5, 10] else 0)
                trend = (year - 2020) * 2
                occupancy = min(95, max(20, base_occupancy + seasonal + trend))

                sample_records.append({
                    'signal_date': date(year, month, 1),
                    'region': 'mallorca',
                    'subregion': None,
                    'occupancy_estimate': occupancy / 100.0,
                    'source': 'ine',
                    'source_metric': 'occupancy_hotel',
                })

        for record in sample_records:
            self.db.insert_demand_signal(record)

        # Create seasonality index
        monthly_seasonality = {
            1: 0.45, 2: 0.40, 3: 0.55, 4: 0.70,
            5: 0.85, 6: 0.95, 7: 1.00, 8: 1.00,
            9: 0.90, 10: 0.75, 11: 0.55, 12: 0.50,
        }
        for month, factor in monthly_seasonality.items():
            self.db.insert_seasonality({
                'month': month,
                'day_of_week': None,
                'region': 'mallorca',
                'segment': 'playa_costa',
                'seasonality_factor': factor,
                'avg_occupancy': 0.65 + (factor - 0.5) * 0.3,
                'years_of_data': 5,
                'data_sources': 'ine_simulated',
            })

        return {'records_created': len(sample_records) + len(monthly_seasonality)}


if __name__ == "__main__":
    ingester = INEDataIngester()
    result = ingester.create_sample_data()
    print(f"Sample data created: {result}")
    stats = ingester.db.get_stats()
    print(f"Database stats: {stats}")
