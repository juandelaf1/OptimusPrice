#!/usr/bin/env python3
"""
V2 Pipeline — Data Validator
Validates scraped market data against quality rules.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
import re


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float


class MarketDataValidator:
    """Validates market price data for V2 pipeline."""

    def __init__(self, min_price: float = 10.0, max_price: float = 1000.0):
        self.min_price = min_price
        self.max_price = max_price

    def validate(self, data: dict) -> ValidationResult:
        """
        Validate a single market price record.
        
        Args:
            data: Dictionary with market price fields
            
        Returns:
            ValidationResult with is_valid, errors, warnings, quality_score
        """
        errors = []
        warnings = []
        score = 1.0

        # Required fields
        required = ['snapshot_date', 'target_date', 'source', 'price_per_night']
        for field in required:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
                score -= 0.3

        if errors:
            return ValidationResult(False, errors, warnings, max(0.0, score))

        # Price validation
        price = data.get('price_per_night')
        if not isinstance(price, (int, float)):
            errors.append(f"Invalid price type: {type(price)}")
            score -= 0.3
        elif price < self.min_price or price > self.max_price:
            errors.append(f"Price {price} outside range [{self.min_price}, {self.max_price}]")
            score -= 0.3

        # Date validation
        try:
            snapshot = data['snapshot_date']
            target = data['target_date']
            
            if isinstance(snapshot, str):
                snapshot = datetime.strptime(snapshot, '%Y-%m-%d').date()
            if isinstance(target, str):
                target = datetime.strptime(target, '%Y-%m-%d').date()
            
            if target <= snapshot:
                errors.append("target_date must be after snapshot_date")
                score -= 0.2
            
            days_ahead = (target - snapshot).days
            if days_ahead < 0 or days_ahead > 365:
                errors.append(f"days_ahead {days_ahead} outside range [0, 365]")
                score -= 0.1
                
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid date format: {e}")
            score -= 0.2

        # Location validation
        location = data.get('location', '')
        if location and 'mallorca' not in location.lower():
            warnings.append(f"Location '{location}' not in Mallorca")

        # Source validation
        valid_sources = ['booking.com', 'airbnb', 'expedia', 'manual']
        source = data.get('source', '')
        if source and source.lower() not in valid_sources:
            warnings.append(f"Unknown source: {source}")

        # Missing optional fields
        optional_fields = ['sublocation', 'property_type', 'star_rating', 'bedrooms']
        for field in optional_fields:
            if field not in data or data[field] is None:
                score -= 0.05
                warnings.append(f"Missing optional field: {field}")

        # Quality indicators
        if data.get('data_quality_score', 1.0) < 0.5:
            warnings.append("Low quality score from scraper")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=max(0.0, score)
        )

    def validate_batch(self, records: List[dict]) -> dict:
        """
        Validate a batch of records.
        
        Returns:
            Summary with total, valid, invalid, avg_quality
        """
        results = [self.validate(r) for r in records]
        
        valid = [r for r in results if r.is_valid]
        invalid = [r for r in results if not r.is_valid]
        avg_quality = sum(r.quality_score for r in results) / len(results) if results else 0
        
        return {
            'total': len(records),
            'valid': len(valid),
            'invalid': len(invalid),
            'avg_quality_score': round(avg_quality, 3),
            'error_summary': self._summarize_errors(invalid),
        }

    def _summarize_errors(self, results: List[ValidationResult]) -> dict:
        """Summarize validation errors."""
        error_counts = {}
        for r in results:
            for e in r.errors:
                error_counts[e] = error_counts.get(e, 0) + 1
        return error_counts
