#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticity Curve Analysis for Optimus Price
Generates: Occupancy(price), Revenue(price), argmax Revenue
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os
import warnings
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

TARGET_PRICE = "avg_price_per_room"
TARGET_OCCUPANCY = "booking_status_Not_Canceled"


def load_data():
    path = DATA_DIR / "processed" / "hotel_reservations_real.csv"
    if not path.exists():
        path = DATA_DIR / "processed" / "hotel_reservations_clean.csv"
    df = pd.read_csv(path)
    leaked = [c for c in df.columns if "competitor" in c.lower()]
    if leaked:
        df = df.drop(columns=leaked)
    return df


def prepare_occupancy_features(df, price=None):
    """Prepare features for occupancy prediction."""
    features = pd.DataFrame()

    if price is not None:
        features["room_price"] = price
    elif TARGET_PRICE in df.columns:
        features["room_price"] = df[TARGET_PRICE]
    else:
        features["room_price"] = 100.0

    if TARGET_PRICE in df.columns:
        market_avg = df[TARGET_PRICE].rolling(window=30, min_periods=1).mean()
        features["price_vs_market"] = features["room_price"] / (market_avg + 1)
    else:
        features["price_vs_market"] = 1.0

    if "arrival_month" in df.columns:
        features["month"] = df["arrival_month"]
        season_factor = {
            1: 0.70, 2: 0.65, 3: 0.75, 4: 0.85,
            5: 0.90, 6: 1.25, 7: 1.40, 8: 1.35,
            9: 0.95, 10: 0.85, 11: 0.75, 12: 1.20,
        }
        features["season_factor"] = features["month"].map(season_factor).fillna(1.0)
    else:
        features["month"] = 6
        features["season_factor"] = 1.0

    if "arrival_day_of_week" in df.columns:
        features["is_weekend"] = (df["arrival_day_of_week"] >= 5).astype(int)
    else:
        features["is_weekend"] = 0

    if "lead_time" in df.columns:
        features["lead_time_days"] = df["lead_time"]
        features["is_last_minute"] = (df["lead_time"] < 7).astype(int)
        features["is_early_bird"] = (df["lead_time"] > 60).astype(int)
    else:
        features["lead_time_days"] = 30
        features["is_last_minute"] = 0
        features["is_early_bird"] = 0

    features["total_guests"] = df.get("total_guests", 2)
    features["total_nights"] = df.get("total_nights", 1)
    features["special_requests"] = df.get("no_of_special_requests", 0)
    features["is_repeated_guest"] = df.get("repeated_guest", 0)

    if "market_segment_type_Online" in df.columns:
        features["is_online_booking"] = df["market_segment_type_Online"].astype(int)
    else:
        features["is_online_booking"] = 1

    meal_cols = [c for c in df.columns if c.startswith("type_of_meal_plan_")]
    if meal_cols:
        features["has_meal_plan"] = (df[meal_cols].sum(axis=1) > 0).astype(int)
    else:
        features["has_meal_plan"] = 0

    room_cols = [c for c in df.columns if c.startswith("room_type_reserved_")]
    if room_cols:
        room_values = {col: i + 1 for i, col in enumerate(sorted(room_cols))}
        features["room_type_value"] = sum(
            df[col].astype(int) * val for col, val in room_values.items()
        )
    else:
        features["room_type_value"] = 1

    features["requires_parking"] = df.get("required_car_parking_space", 0)

    return features


def train_occupancy_model(df):
    """Train occupancy classifier."""
    X = prepare_occupancy_features(df)
    y = df[TARGET_OCCUPANCY].astype(int)

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", GradientBoostingClassifier(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            subsample=0.8, random_state=42
        )),
    ])
    model.fit(X_train, y_train)

    from sklearn.metrics import roc_auc_score
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    print(f"  Occupancy model AUC: {auc:.4f}")

    return model, X_test


def generate_occupancy_curve(model, X_base, price_range=(20, 300), n_points=50):
    """Generate occupancy vs price curve."""
    prices = np.linspace(price_range[0], price_range[1], n_points)
    occupancies = []

    for price in prices:
        X_price = X_base.copy()
        X_price["room_price"] = price
        # Update price_vs_market with new price
        if "price_vs_market" in X_price.columns:
            avg_price = X_base["room_price"].mean()
            X_price["price_vs_market"] = price / (avg_price + 1)

        occ_prob = model.predict_proba(X_price)[:, 1].mean()
        occupancies.append(occ_prob)

    return prices, np.array(occupancies)


def generate_revenue_curve(prices, occupancies, total_rooms=100):
    """Generate revenue vs price curve."""
    revenue = occupancies * prices * total_rooms
    return revenue


def find_optimal_price(prices, revenue):
    """Find price that maximizes revenue."""
    idx = np.argmax(revenue)
    return prices[idx], revenue[idx]


def compute_elasticity(prices, occupancies):
    """Compute point elasticity at each price point."""
    dQ = np.diff(occupancies)
    dP = np.diff(prices)
    P_mid = (prices[:-1] + prices[1:]) / 2
    Q_mid = (occupancies[:-1] + occupancies[1:]) / 2

    # Avoid division by zero
    Q_mid = np.where(Q_mid < 0.01, 0.01, Q_mid)

    elasticity = (dQ / dP) * (P_mid / Q_mid)
    return prices[:-1], elasticity


def plot_occupancy_curve(prices, occupancies, save_path=None):
    """Plot occupancy vs price curve."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(prices, occupancies, "b-", linewidth=2, label="Occupancy Probability")
    ax.fill_between(prices, occupancies, alpha=0.1, color="blue")
    ax.set_xlabel("Price (EUR)", fontsize=12)
    ax.set_ylabel("Occupancy Probability", fontsize=12)
    ax.set_title("Occupancy vs Price Curve (Demand Curve)", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Mark key points
    max_occ_idx = np.argmax(occupancies)
    min_occ_idx = np.argmin(occupancies)
    ax.annotate(f"Max: {occupancies[max_occ_idx]:.2%} at €{prices[max_occ_idx]:.0f}",
                xy=(prices[max_occ_idx], occupancies[max_occ_idx]),
                xytext=(prices[max_occ_idx] + 30, occupancies[max_occ_idx] + 0.05),
                arrowprops=dict(arrowstyle="->", color="green"), color="green")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_revenue_curve(prices, revenue, optimal_price, optimal_revenue, save_path=None):
    """Plot revenue vs price curve with optimal point."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(prices, revenue, "g-", linewidth=2, label="Revenue")
    ax.fill_between(prices, revenue, alpha=0.1, color="green")

    # Mark optimal
    ax.axvline(x=optimal_price, color="r", linestyle="--", alpha=0.7, label=f"Optimal: €{optimal_price:.2f}")
    ax.plot(optimal_price, optimal_revenue, "r*", markersize=15, zorder=5)
    ax.annotate(f"Optimal Revenue: €{optimal_revenue:,.0f}\nat €{optimal_price:.2f}/room",
                xy=(optimal_price, optimal_revenue),
                xytext=(optimal_price + 30, optimal_revenue * 0.95),
                arrowprops=dict(arrowstyle="->", color="red"),
                fontsize=11, color="red")

    ax.set_xlabel("Price (EUR)", fontsize=12)
    ax.set_ylabel("Revenue (EUR)", fontsize=12)
    ax.set_title("Revenue vs Price Curve", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_elasticity(prices_e, elasticity, save_path=None):
    """Plot elasticity curve."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Classify elasticity
    colors = []
    for e in elasticity:
        if e < -1.5:
            colors.append("#F44336")  # Very elastic (red)
        elif e < -0.5:
            colors.append("#FF9800")  # Elastic (orange)
        elif e < 0:
            colors.append("#4CAF50")  # Inelastic (green)
        else:
            colors.append("#9C27B0")  # Anomaly (purple)

    ax.bar(prices_e, elasticity, width=np.mean(np.diff(prices_e)) * 0.8, color=colors, alpha=0.7)
    ax.axhline(y=-1, color="red", linestyle="--", alpha=0.5, label="Unit Elastic (E=-1)")
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)
    ax.set_xlabel("Price (EUR)", fontsize=12)
    ax.set_ylabel("Price Elasticity of Demand", fontsize=12)
    ax.set_title("Price Elasticity Curve", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend()

    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#F44336", alpha=0.7, label="Very Elastic (E < -1.5)"),
        Patch(facecolor="#FF9800", alpha=0.7, label="Elastic (-1.5 < E < -0.5)"),
        Patch(facecolor="#4CAF50", alpha=0.7, label="Inelastic (-0.5 < E < 0)"),
        Patch(facecolor="#9C27B0", alpha=0.7, label="Anomaly (E > 0)"),
    ]
    ax.legend(handles=legend_elements + [plt.Line2D([0], [0], color="red", linestyle="--", label="Unit Elastic")],
              loc="upper right")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def plot_combined(prices, occupancies, revenue, optimal_price, optimal_revenue, save_path=None):
    """Plot combined dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Occupancy curve
    ax = axes[0, 0]
    ax.plot(prices, occupancies, "b-", linewidth=2)
    ax.fill_between(prices, occupancies, alpha=0.1, color="blue")
    ax.set_xlabel("Price (EUR)")
    ax.set_ylabel("Occupancy Probability")
    ax.set_title("Occupancy vs Price")
    ax.grid(True, alpha=0.3)

    # Revenue curve
    ax = axes[0, 1]
    ax.plot(prices, revenue, "g-", linewidth=2)
    ax.axvline(x=optimal_price, color="r", linestyle="--", alpha=0.7)
    ax.plot(optimal_price, optimal_revenue, "r*", markersize=15)
    ax.set_xlabel("Price (EUR)")
    ax.set_ylabel("Revenue (EUR)")
    ax.set_title(f"Revenue vs Price (Optimal: €{optimal_price:.0f})")
    ax.grid(True, alpha=0.3)

    # Elasticity
    ax = axes[1, 0]
    prices_e, elasticity = compute_elasticity(prices, occupancies)
    colors = ["#F44336" if e < -1.5 else "#FF9800" if e < -0.5 else "#4CAF50" if e < 0 else "#9C27B0" for e in elasticity]
    ax.bar(prices_e, elasticity, width=np.mean(np.diff(prices_e)) * 0.8, color=colors, alpha=0.7)
    ax.axhline(y=-1, color="red", linestyle="--", alpha=0.5)
    ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)
    ax.set_xlabel("Price (EUR)")
    ax.set_ylabel("Elasticity")
    ax.set_title("Price Elasticity")
    ax.grid(True, alpha=0.3, axis="y")

    # Price distribution
    ax = axes[1, 1]
    ax.hist(prices, bins=30, color="#2196F3", alpha=0.7, edgecolor="white")
    ax.axvline(x=optimal_price, color="r", linestyle="--", linewidth=2, label=f"Optimal: €{optimal_price:.0f}")
    ax.set_xlabel("Price (EUR)")
    ax.set_ylabel("Frequency")
    ax.set_title("Price Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.suptitle("Elasticity Analysis Dashboard", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig


def run_analysis():
    print("=" * 60)
    print("ELASTICITY CURVE ANALYSIS")
    print("=" * 60)

    df = load_data()
    print(f"Data: {len(df)} rows")

    # Train occupancy model
    print("\nTraining occupancy model...")
    model, X_test = train_occupancy_model(df)

    # Use test set as base (average profile)
    X_base = X_test.head(100).copy()  # Use 100 samples from test set

    # Generate curves
    print("\nGenerating occupancy curve...")
    prices, occupancies = generate_occupancy_curve(model, X_base, price_range=(20, 300), n_points=50)
    print(f"  Price range: €{prices[0]:.0f} - €{prices[-1]:.0f}")
    print(f"  Occupancy range: {occupancies.min():.2%} - {occupancies.max():.2%}")

    # Revenue curve
    print("Generating revenue curve...")
    total_rooms = 100
    revenue = generate_revenue_curve(prices, occupancies, total_rooms)
    optimal_price, optimal_revenue = find_optimal_price(prices, revenue)
    print(f"  Optimal price: €{optimal_price:.2f}")
    print(f"  Max revenue: €{optimal_revenue:,.0f}")

    # Current revenue (at average price)
    current_price = df[TARGET_PRICE].mean()
    current_idx = np.argmin(np.abs(prices - current_price))
    current_revenue = revenue[current_idx]
    print(f"  Current avg price: €{current_price:.2f}")
    print(f"  Current revenue: €{current_revenue:,.0f}")
    print(f"  Revenue gain from optimization: €{optimal_revenue - current_revenue:,.0f}")

    # Elasticity
    prices_e, elasticity = compute_elasticity(prices, occupancies)
    avg_elasticity = np.mean(elasticity)
    print(f"  Average elasticity: {avg_elasticity:.3f}")

    # Plots
    print("\nGenerating plots...")
    plot_occupancy_curve(prices, occupancies, save_path=str(REPORTS_DIR / "elasticity_occupancy.png"))
    plot_revenue_curve(prices, revenue, optimal_price, optimal_revenue, save_path=str(REPORTS_DIR / "elasticity_revenue.png"))
    plot_elasticity(prices_e, elasticity, save_path=str(REPORTS_DIR / "elasticity_curve.png"))
    plot_combined(prices, occupancies, revenue, optimal_price, optimal_revenue, save_path=str(REPORTS_DIR / "elasticity_dashboard.png"))

    # Sensitivity analysis
    print("\nSensitivity analysis...")
    sensitivity = []
    for pct_change in [-20, -10, -5, 0, 5, 10, 20]:
        test_price = current_price * (1 + pct_change / 100)
        idx = np.argmin(np.abs(prices - test_price))
        sens_occ = occupancies[idx]
        sens_rev = revenue[idx]
        sensitivity.append({
            "price_change_pct": pct_change,
            "price_eur": round(float(test_price), 2),
            "occupancy_pct": round(float(sens_occ * 100), 2),
            "revenue_eur": round(float(sens_rev), 2),
            "revenue_change_pct": round(float((sens_rev - current_revenue) / current_revenue * 100), 2) if current_revenue > 0 else 0,
        })

    for s in sensitivity:
        print(f"  {s['price_change_pct']:+3d}%: €{s['price_eur']:.0f} -> {s['occupancy_pct']:.1f}% occ, €{s['revenue_eur']:,.0f} rev ({s['revenue_change_pct']:+.1f}%)")

    # Save results
    results = {
        "optimal_price": round(float(optimal_price), 2),
        "optimal_revenue": round(float(optimal_revenue), 2),
        "current_price": round(float(current_price), 2),
        "current_revenue": round(float(current_revenue), 2),
        "revenue_gain": round(float(optimal_revenue - current_revenue), 2),
        "average_elasticity": round(float(avg_elasticity), 4),
        "sensitivity": sensitivity,
        "price_range": [float(prices[0]), float(prices[-1])],
        "occupancy_range": [float(occupancies.min()), float(occupancies.max())],
    }

    output_path = REPORTS_DIR / "elasticity_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")

    return results


if __name__ == "__main__":
    run_analysis()
