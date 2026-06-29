import sys
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")
from src.optimus_price.occupancy_model import OccupancyPredictor
from src.optimus_price.elasticity_engine import PriceElasticityEngine
from src.optimus_price.revenue_optimizer import RevenueOptimizer

print("Loading models...")
predictor = OccupancyPredictor()
predictor.load()

engine = PriceElasticityEngine(predictor)
optimizer = RevenueOptimizer(predictor, engine)

features = {"lead_time_days": 30, "total_guests": 2, "total_nights": 2}

print("\n--- Revenue Curve Analysis ---")
curve = engine.generate_revenue_curve(features, price_range=(50.0, 300.0), n_points=50, total_rooms=100)
print(f"Optimal Price: {curve.optimal_price:.2f}")
print(f"Optimal Revenue: {curve.optimal_revenue:.2f}/night")
print(f"Current Price: {curve.current_price:.2f}")
print(f"Current Revenue: {curve.current_revenue:.2f}/night")
print(f"Revenue Gain: {curve.revenue_gain_pct:+.1f}%")

print("\n--- Price Optimization ---")
rec = optimizer.optimize(features, current_price=120.0, total_rooms=100)
print(f"Current Price: {rec.current_price:.2f}")
print(f"Optimal Price: {rec.optimal_price:.2f}")
print(f"Elasticity: {rec.elasticity:.3f}")
print(f"Revenue Gain/Room: {rec.revenue_gain_per_room:.2f}")
total_gain = rec.revenue_gain_per_room * 100
annual_gain = total_gain * 365
print(f"Total Revenue Gain: {total_gain:.2f}/night")
print(f"Annual Gain: {annual_gain:,.0f}")
print(f"Confidence: {rec.confidence:.0%}")
print(f"Risk: {rec.risk_level}")
