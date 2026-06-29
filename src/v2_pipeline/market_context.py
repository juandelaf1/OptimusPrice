#!/usr/bin/env python3
"""
V2 Market Context Provider
Provides market context for V1 predictions using V2 market intelligence data.
"""

import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.v2_pipeline.market_db import MarketIntelligenceDB


class MarketContextProvider:
    """Provides market context for pricing predictions."""
    
    def __init__(self, db: Optional[MarketIntelligenceDB] = None):
        self.db = db or MarketIntelligenceDB()
    
    def get_market_context(
        self,
        region: str = 'mallorca',
        segment: str = 'playa_costa',
        target_date: Optional[date] = None,
    ) -> Dict:
        """
        Get market context for a specific region, segment, and date.
        
        Returns:
            Dictionary with market context information
        """
        if target_date is None:
            target_date = date.today()
        
        context = {
            'region': region,
            'segment': segment,
            'target_date': target_date.isoformat(),
            'market_index': None,
            'seasonality': None,
            'demand_signals': None,
            'recommendations': [],
        }
        
        # Get market index
        index_data = self.db.query_market_index(
            region=region,
            segment=segment,
            limit=1,
        )
        if index_data:
            latest = index_data[0]
            context['market_index'] = {
                'price_index': latest['price_index'],
                'avg_price': latest['avg_price'],
                'price_change_pct': latest['price_change_pct'],
            }
        
        # Get seasonality
        seasonality = self.db.query_seasonality(
            region=region,
            segment=segment,
        )
        if seasonality:
            month = target_date.month
            for s in seasonality:
                if s['month'] == month:
                    context['seasonality'] = {
                        'factor': s['seasonality_factor'],
                        'avg_occupancy': s['avg_occupancy'],
                        'is_peak': s['seasonality_factor'] > 1.2,
                        'is_low': s['seasonality_factor'] < 0.8,
                    }
                    break
        
        # Get demand signals
        with self.db._conn() as conn:
            demand = conn.execute("""
                SELECT AVG(search_volume_index) as avg_search,
                       AVG(occupancy_estimate) as avg_occupancy
                FROM demand_signals
                WHERE region = ? AND signal_date >= date(?, '-30 days')
            """, (region, target_date.isoformat())).fetchone()
            
            if demand and demand['avg_search']:
                context['demand_signals'] = {
                    'search_volume_index': demand['avg_search'],
                    'occupancy_estimate': demand['avg_occupancy'],
                }
        
        # Generate recommendations
        context['recommendations'] = self._generate_recommendations(context)
        
        return context
    
    def _generate_recommendations(self, context: Dict) -> list:
        """Generate pricing recommendations based on market context."""
        recommendations = []
        
        # Seasonality recommendations
        seasonality = context.get('seasonality')
        if seasonality:
            if seasonality['is_peak']:
                recommendations.append({
                    'type': 'pricing',
                    'message': 'Temporada alta — considerar incremento de precios del 15-25%',
                    'priority': 'high',
                })
            elif seasonality['is_low']:
                recommendations.append({
                    'type': 'pricing',
                    'message': 'Temporada baja — considerar descuentos o paquetes especiales',
                    'priority': 'medium',
                })
        
        # Market index recommendations
        market_index = context.get('market_index')
        if market_index and market_index.get('price_change_pct'):
            change = market_index['price_change_pct']
            if change > 10:
                recommendations.append({
                    'type': 'market',
                    'message': f'Mercado en alza (+{change:.1f}%) — evaluar ajuste de precios',
                    'priority': 'medium',
                })
            elif change < -10:
                recommendations.append({
                    'type': 'market',
                    'message': f'Mercado en bajada ({change:.1f}%) — revisar estrategia de precios',
                    'priority': 'high',
                })
        
        # Demand recommendations
        demand = context.get('demand_signals')
        if demand:
            occ = demand.get('occupancy_estimate')
            if occ is not None:
                if occ > 0.8:
                    recommendations.append({
                        'type': 'demand',
                        'message': 'Alta ocupación estimada — posible oportunidad de incremento de precios',
                        'priority': 'medium',
                    })
                elif occ < 0.4:
                    recommendations.append({
                        'type': 'demand',
                        'message': 'Baja ocupación estimada — considerar promociones',
                        'priority': 'high',
                    })
        
        return recommendations
    
    def adjust_prediction(
        self,
        base_price: float,
        region: str = 'mallorca',
        segment: str = 'playa_costa',
        target_date: Optional[date] = None,
    ) -> Dict:
        """
        Adjust a V1 prediction using V2 market context.
        
        Args:
            base_price: Price predicted by V1 model
            region: Market region
            segment: Market segment
            target_date: Target date for pricing
            
        Returns:
            Dictionary with adjusted price and context
        """
        context = self.get_market_context(region, segment, target_date)
        
        adjustment_factor = 1.0
        adjustments = []
        
        # Apply seasonality adjustment
        if context.get('seasonality'):
            factor = context['seasonality']['factor']
            if factor != 1.0:
                adjustment_factor *= factor
                adjustments.append(f"Estacionalidad: x{factor:.2f}")
        
        # Apply market index adjustment
        if context.get('market_index') and context['market_index'].get('price_change_pct'):
            change = context['market_index']['price_change_pct']
            if abs(change) > 5:  # Only apply if change > 5%
                market_adj = 1.0 + (change / 100 * 0.3)  # Dampened adjustment
                adjustment_factor *= market_adj
                adjustments.append(f"Mercado: x{market_adj:.2f}")
        
        adjusted_price = base_price * adjustment_factor
        
        return {
            'base_price': base_price,
            'adjusted_price': adjusted_price,
            'adjustment_factor': adjustment_factor,
            'adjustments': adjustments,
            'context': context,
        }


if __name__ == "__main__":
    # Demo
    provider = MarketContextProvider()
    
    print("=== Market Context Demo ===")
    context = provider.get_market_context(
        region='mallorca',
        segment='playa_costa',
        target_date=date(2025, 7, 15),
    )
    
    print(f"\nRegion: {context['region']}")
    print(f"Segment: {context['segment']}")
    print(f"Date: {context['target_date']}")
    
    if context['market_index']:
        print(f"\nMarket Index:")
        print(f"  Price Index: {context['market_index']['price_index']:.1f}")
        print(f"  Avg Price: €{context['market_index']['avg_price']:.0f}")
    
    if context['seasonality']:
        print(f"\nSeasonality:")
        print(f"  Factor: {context['seasonality']['factor']:.3f}")
        print(f"  Occupancy: {context['seasonality']['avg_occupancy']*100:.0f}%")
        print(f"  Is Peak: {context['seasonality']['is_peak']}")
    
    print(f"\nRecommendations:")
    for rec in context['recommendations']:
        print(f"  [{rec['priority']}] {rec['message']}")
    
    print("\n=== Price Adjustment Demo ===")
    base_price = 120.0
    result = provider.adjust_prediction(
        base_price=base_price,
        region='mallorca',
        segment='playa_costa',
        target_date=date(2025, 7, 15),
    )
    
    print(f"\nBase Price (V1): €{result['base_price']:.0f}")
    print(f"Adjusted Price (V2): €{result['adjusted_price']:.0f}")
    print(f"Adjustment Factor: x{result['adjustment_factor']:.3f}")
    print(f"Adjustments: {', '.join(result['adjustments'])}")
