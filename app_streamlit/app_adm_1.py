# -*- coding: utf-8 -*-
"""
Optimus Price — Admin Dashboard
Connected platform: DB-backed, shows customer activity + competitor intel
"""

import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os, sys, json
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
BASE_DIR = os.path.dirname(__file__)
PIPELINE_FILE = os.path.join(BASE_DIR, "..", "models", "pipeline_trained_model.pkl")

from optimus_db import db
from shared_utils import build_input_data, build_input_mod
from monitoring_service import MonitoringService, ALERTS_DIR

st.set_page_config(page_title="Optimus Price — Admin", layout="wide", page_icon="▌")

DARK_BG = "#0F1720"
SAGE = "#A3B18A"
TEXT_SEC = "#B0B8C5"
TEXT_MUTED = "#7C8595"
BORDER = "#242D3D"

page_style = f"""
<style>
    .stApp {{ background: {DARK_BG}; }}
    .block-container {{ padding: 2rem 3rem; max-width: 1400px; }}
    h1,h2,h3,h4,h5,h6,p,li,span {{ font-family: -apple-system, 'Inter', 'SF Pro', sans-serif; }}
    h1 {{ color: white; font-size: 1.75rem; font-weight: 600; letter-spacing: -0.02em; }}
    h2 {{ color: white; font-size: 1.25rem; font-weight: 500; }}
    p {{ color: {TEXT_SEC}; font-size: 0.9rem; }}
    div[data-testid="stMetricValue"] {{ font-size: 2rem !important; font-weight: 600 !important; color: white !important; }}
    div[data-testid="metric-container"] {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; padding: 1.25rem; }}
    .stButton button {{ background: white; color: {DARK_BG}; border-radius: 12px; font-weight: 500; border: none; }}
    .stButton button:hover {{ background: {SAGE}; color: {DARK_BG}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 2rem; border-bottom: 1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{ color: {TEXT_MUTED}; }}
    .stTabs [aria-selected="true"] {{ color: {SAGE} !important; }}
    hr {{ border-color: {BORDER}; margin: 1.5rem 0; }}
    .card {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; }}
    .badge-green {{ background: {SAGE}22; color: {SAGE}; }}
    .badge-gray {{ background: {BORDER}; color: {TEXT_MUTED}; }}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

try:
    pipeline = joblib.load(PIPELINE_FILE)
except FileNotFoundError:
    st.error(f"Model not found: {PIPELINE_FILE}")
    st.stop()

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# ---- Auth ----
st.sidebar.markdown("""<div style="font-size:1.5rem;font-weight:700;color:white;">▌ Optimus Price</div>""", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.8rem'>Admin Dashboard</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

role = st.sidebar.selectbox("Role", ["Administrador", "Cliente"])
show_admin = False
if role == "Administrador":
    pwd = st.sidebar.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        show_admin = True
        st.sidebar.markdown(f"<span class='badge badge-green'>Access Granted</span>", unsafe_allow_html=True)
    elif pwd:
        st.sidebar.error("Incorrect password")

page = st.sidebar.selectbox("Module", ["Dashboard", "Reservations", "Simulator", "Market Monitor"])

if show_admin:
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color:" + TEXT_MUTED + ";font-size:0.8rem'>Admin Tools</p>", unsafe_allow_html=True)
    override_val = st.sidebar.slider("Price Override (%)", -20, 30, 0, step=1)
    if st.sidebar.button("Save Override"):
        db.save_override(override_val, "Manual override from dashboard")
        st.sidebar.success(f"Override set to {override_val}%")

st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center">
    <h1>Optimus Price</h1>
    <p style="color:{TEXT_MUTED};font-size:0.8rem">{datetime.now():%Y-%m-%d %H:%M}</p>
</div>""", unsafe_allow_html=True)

if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    rstats = db.get_reservation_stats()
    qstats = db.get_query_stats()

    with col1:
        st.markdown(f"""<div class="card" style="text-align:center"><p style="color:{TEXT_MUTED};font-size:0.8rem">Total Reservations</p><p style="color:white;font-size:2rem;font-weight:700">{rstats['total_reservations']}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card" style="text-align:center"><p style="color:{TEXT_MUTED};font-size:0.8rem">Revenue</p><p style="color:{SAGE};font-size:2rem;font-weight:700">€{rstats['total_revenue']:,.0f}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card" style="text-align:center"><p style="color:{TEXT_MUTED};font-size:0.8rem">Queries Today</p><p style="color:white;font-size:2rem;font-weight:700">{qstats['queries_today']}</p></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="card" style="text-align:center"><p style="color:{TEXT_MUTED};font-size:0.8rem">Avg Price/Night</p><p style="color:white;font-size:2rem;font-weight:700">€{rstats['avg_price_per_night']:.0f}</p></div>""", unsafe_allow_html=True)

    st.markdown("<h2>Recent Customer Activity</h2>", unsafe_allow_html=True)
    queries = db.get_queries(limit=10)
    if queries:
        for q in queries:
            st.markdown(f"""<div class="card" style="padding:0.75rem 1rem;display:flex;justify-content:space-between">
                <div><span style="color:white">{q.get('source','portal')}</span>
                <span style="color:{TEXT_MUTED};margin-left:0.5rem">{q.get('total_guests','?')} guests · {q.get('total_nights','?')} nights</span></div>
                <div><span style="color:{SAGE};font-weight:600">€{q.get('final_price',0):.0f}</span>
                <span style="color:{TEXT_MUTED};margin-left:0.5rem;font-size:0.8rem">{q.get('created_at','')[:19]}</span></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED}'>No queries yet. Customer portal will feed data here.</p>", unsafe_allow_html=True)

    if show_admin:
        st.markdown("<h2>Active Override</h2>", unsafe_allow_html=True)
        override = db.get_active_override()
        if override:
            st.markdown(f"""<div class="card"><p>{override['admin_user']} set <b>{override['modifier_percent']:+.0f}%</b> on {override['created_at'][:19]}</p></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{TEXT_MUTED}'>No active override</p>", unsafe_allow_html=True)

elif page == "Reservations":
    st.markdown("<h2>Reservations</h2>", unsafe_allow_html=True)
    reservations = db.get_reservations(limit=50)
    if reservations:
        df = pd.DataFrame(reservations)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", csv, "reservations.csv", "text/csv")
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED}'>No reservations yet</p>", unsafe_allow_html=True)

elif page == "Simulator":
    st.markdown("<h2>Price Simulator</h2>", unsafe_allow_html=True)
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        lead_time = st.number_input("Lead Time (days)", 0, 365, 30)
        arrival = st.date_input("Arrival Date", today)
        nights = st.number_input("Nights", 1, 30, 3)
        guests = st.number_input("Guests", 1, 10, 2)
        meal = st.selectbox("Meal Plan", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
    with col2:
        room = st.selectbox("Room Type", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
        parking = st.checkbox("Parking Required")
        special = st.number_input("Special Requests", 0, 10, 0)

    input_data = build_input_data(parking, lead_time, arrival, 0, special, meal, room, guests, nights)
    try:
        pred = pipeline.predict(input_data)[0]
        override = db.get_active_override()
        override_pct = override["modifier_percent"] if override else 0
        final_price = pred * (1 + override_pct / 100)

        st.markdown(f"""<div style="display:flex;gap:2rem;margin:1rem 0">
            <div class="card" style="flex:1;text-align:center">
                <p style="color:{TEXT_MUTED};font-size:0.8rem">Base Price</p>
                <p style="color:white;font-size:1.5rem;font-weight:700">€{pred:.2f}</p>
            </div>
            <div class="card" style="flex:1;text-align:center;border-color:{SAGE}">
                <p style="color:{TEXT_MUTED};font-size:0.8rem">Final Price</p>
                <p style="color:{SAGE};font-size:1.5rem;font-weight:700">€{final_price:.2f}</p>
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("Save to DB"):
            qid = db.save_query({
                "session_id": "admin-sim",
                "total_guests": guests, "total_nights": nights,
                "lead_time": lead_time, "arrival_month": arrival.month,
                "room_type": room, "meal_plan": meal,
                "predicted_price": float(pred), "market_adjustment": override_pct,
                "final_price": float(final_price),
                "source": "admin_simulator"
            })
            st.success(f"Query saved (id={qid})")
    except Exception as e:
        st.error(f"Prediction error: {e}")

elif page == "Market Monitor":
    st.markdown("<h2>Market Monitor</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.8rem'>Competitor price intelligence via raspal_scrapper</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    hotel_id = "sample-hotel-001"
    with col1:
        if st.button("Run Price Check", use_container_width=True):
            svc = MonitoringService()
            svc.system.load_model()
            svc.add_hotel(hotel_id)
            results = svc.run_once()
            st.success(f"Checked {len(results)} hotels")

            for h, r in results.items():
                if "competitor_prices" in r:
                    for ota, price in r["competitor_prices"].items():
                        db.save_competitor_price(h, ota, price)
            st.rerun()

    competitor_data = db.get_latest_competitor_prices(hotel_id)
    if competitor_data:
        rows = ""
        for cd in competitor_data:
            rows += f"""<div class="card" style="padding:0.75rem 1rem;display:flex;justify-content:space-between">
                <span style="color:white">{cd['ota']}</span>
                <span style="color:{SAGE};font-weight:600">€{cd['price']:.0f}</span>
            </div>"""
        st.markdown(f"<h3>Latest OTA Prices</h3>{rows}", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED}'>Run a price check to see competitor data</p>", unsafe_allow_html=True)

    alerts_path = os.path.join(ALERTS_DIR, f"alerts_{datetime.now():%Y%m%d}.jsonl")
    if os.path.exists(alerts_path):
        st.markdown("<h3>Recent Alerts</h3>", unsafe_allow_html=True)
        with open(alerts_path) as f:
            for line in f.readlines()[-5:]:
                if line.strip():
                    a = json.loads(line)
                    st.markdown(f"""<div class="card" style="padding:0.5rem 1rem">{a['ota']} — €{a['ota_price']:.0f} vs €{a['internal_price']:.0f} (+{a['gap_percent']:.1f}%)</div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""<div style="text-align:center;color:{TEXT_MUTED};font-size:0.75rem;padding:1rem 0">
    Optimus Price v2.0 · Python · Pandas · Scikit-Learn · Streamlit · raspal_scrapper
</div>""", unsafe_allow_html=True)
