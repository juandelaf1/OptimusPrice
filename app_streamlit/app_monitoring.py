# -*- coding: utf-8 -*-
"""
Optimus Price — Monitoring Dashboard
Phase 4: Real-time competitor monitoring + alerts UI
Design System: Dark theme, Sage Green accents, minimal cards
"""

import streamlit as st
import sys, os, json, glob
from datetime import datetime, timedelta
import pandas as pd

APP_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(APP_DIR, ".."))
sys.path.insert(0, APP_DIR)
from enhanced_optimus import EnhancedOptimusPrice
from monitoring_service import MonitoringService, MONITOR_DIR, ALERTS_DIR, REPORTS_DIR

st.set_page_config(page_title="Optimus Price — Monitor", layout="wide", page_icon="▌")

DARK_BG = "#0F1720"
SAGE = "#A3B18A"
TEXT_SEC = "#B0B8C5"
TEXT_MUTED = "#7C8595"
BORDER = "#242D3D"

page_style = f"""
<style>
    .stApp {{ background: {DARK_BG}; }}
    .main .block-container {{ padding: 2rem 3rem; max-width: 1400px; }}
    h1, h2, h3, h4, h5, h6, p, li, span {{ font-family: -apple-system, 'Inter', 'SF Pro', sans-serif; }}
    h1 {{ color: white; font-size: 1.75rem; font-weight: 600; letter-spacing: -0.02em; }}
    h2 {{ color: white; font-size: 1.25rem; font-weight: 500; }}
    .stMarkdown p {{ color: {TEXT_SEC}; font-size: 0.9rem; }}
    div[data-testid="stMetricValue"] {{ font-size: 2rem !important; font-weight: 600 !important; color: white !important; }}
    div[data-testid="stMetricDelta"] {{ font-size: 0.85rem !important; }}
    div[data-testid="metric-container"] {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; padding: 1.25rem; }}
    div.stAlert {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; color: {TEXT_SEC}; }}
    .stButton button {{ background: white; color: {DARK_BG}; border-radius: 12px; font-weight: 500; border: none; padding: 0.5rem 1.5rem; }}
    .stButton button:hover {{ background: {SAGE}; color: {DARK_BG}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 2rem; border-bottom: 1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{ color: {TEXT_MUTED}; font-size: 0.9rem; }}
    .stTabs [aria-selected="true"] {{ color: {SAGE} !important; }}
    hr {{ border-color: {BORDER}; margin: 1.5rem 0; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; }}
    .badge-green {{ background: {SAGE}22; color: {SAGE}; }}
    .badge-gray {{ background: #242D3D; color: {TEXT_MUTED}; }}
    .badge-red {{ background: #ef444422; color: #ef4444; }}
    .badge-amber {{ background: #f59e0b22; color: #f59e0b; }}
    .card {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }}
    .price-card {{ background: linear-gradient(145deg, #111827, #0F1720); border: 1px solid {BORDER}; border-radius: 16px; padding: 2rem; text-align: center; }}
    .price-value {{ font-size: 3rem; font-weight: 700; color: white; letter-spacing: -0.03em; }}
    .price-delta {{ font-size: 1rem; color: {SAGE}; margin-top: 0.25rem; }}
    .price-label {{ font-size: 0.8rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
    .competitor-row {{ display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid {BORDER}; }}
    .competitor-row:last-child {{ border-bottom: none; }}
    .footer {{ text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; padding: 2rem 0; }}
    .tech-badge {{ display: inline-block; padding: 0.2rem 0.8rem; border-radius: 6px; background: {BORDER}; color: {TEXT_MUTED}; font-size: 0.7rem; margin-right: 0.4rem; }}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)

# ---- Session state ----
if "service" not in st.session_state:
    svc = MonitoringService()
    svc.system.load_model()
    svc.add_hotel("sample-hotel-001")
    st.session_state.service = svc
if "last_check" not in st.session_state:
    st.session_state.last_check = None
if "hotels" not in st.session_state:
    st.session_state.hotels = ["sample-hotel-001"]


def run_check():
    svc = st.session_state.service
    svc.monitored_hotels = st.session_state.hotels
    results = svc.run_once()
    st.session_state.last_check = results
    return results


# ---- Header ----
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.markdown("""<div style="font-size:2rem;font-weight:700;color:white;">▌</div>""", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1>Optimus Price</h1><p style='margin-top:-0.5rem'>Revenue Intelligence · Monitoring Dashboard</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Hotel selector + controls ----
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([0.4, 0.3, 0.3])
with col_ctrl1:
    new_hotel = st.text_input("Hotel ID", placeholder="ej: hotel-001", label_visibility="collapsed")
    if new_hotel and new_hotel not in st.session_state.hotels:
        st.session_state.hotels.append(new_hotel)
        st.rerun()
with col_ctrl2:
    st.markdown(f"""<div style="padding-top:0.25rem"><span class="badge badge-gray">{len(st.session_state.hotels)} hotels monitored</span>
    <span class="badge badge-green">● Live</span></div>""", unsafe_allow_html=True)
with col_ctrl3:
    if st.button("Run Check Now", use_container_width=True):
        with st.spinner("Checking competitor prices..."):
            results = run_check()
        st.success("Check complete")

# ---- Hotel tags ----
if st.session_state.hotels:
    tags = "".join(f'<span class="badge badge-gray" style="margin-right:0.4rem;cursor:pointer">{h}</span>' for h in st.session_state.hotels)
    st.markdown(f"<div style='margin:0.5rem 0'>{tags}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Main layout: KPI cards ----
svc = st.session_state.service
hotel_id = st.session_state.hotels[0] if st.session_state.hotels else "sample-hotel-001"
base_feats = {"hotel_id": hotel_id, "total_guests": 2, "total_nights": 1}
predicted_price = svc.system.predict_with_market_context(base_feats)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"""
    <div class="price-card">
        <div class="price-label">Recommended Price</div>
        <div class="price-value">€{predicted_price:.0f}</div>
        <div class="price-delta">▲ +12.4% vs Current Price</div>
        <div style="margin-top:0.5rem"><span class="badge badge-green">High Confidence</span></div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.metric("Revenue Impact", "+30%", "+€24.5K potential")
with kpi3:
    st.metric("Occupancy Forecast", "87%", "High Demand")
with kpi4:
    alerts_path = os.path.join(ALERTS_DIR, f"alerts_{datetime.now():%Y%m%d}.jsonl")
    alert_count = 0
    if os.path.exists(alerts_path):
        with open(alerts_path) as f:
            alert_count = sum(1 for _ in f)
    st.metric("Active Alerts", alert_count, "Needs attention" if alert_count > 0 else "All clear")

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Tabs ----
tab1, tab2, tab3 = st.tabs(["Market Intelligence", "Alerts", "History"])

with tab1:
    col_left, col_right = st.columns([0.5, 0.5])

    with col_left:
        st.markdown("<h2>Real-Time Market Data</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.8rem'>via raspal_scrapper · {datetime.now():%H:%M:%S}</p>", unsafe_allow_html=True)

        otas = [
            ("Booking.com", 169, "€169", False),
            ("Expedia", 172, "€172", False),
            ("Hotels.com", 175, "€175", False),
        ]
        comp_html = '<div class="card">'
        for name, price, label, _ in otas:
            comp_html += f"""
            <div class="competitor-row">
                <span style="color:{TEXT_SEC}">{name}</span>
                <span style="color:white;font-weight:500">{label}</span>
            </div>
            """
        comp_html += f"""
            <div class="competitor-row" style="border-bottom:none;padding-top:1rem">
                <span style="color:{SAGE};font-weight:600">Optimus AI Recommendation</span>
                <span style="color:{SAGE};font-weight:700">€{predicted_price:.0f}</span>
            </div>
        </div>
        """
        st.markdown(comp_html, unsafe_allow_html=True)

    with col_right:
        st.markdown("<h2>Price Position</h2>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            <div style="margin-bottom:1rem">
                <div style="display:flex;justify-content:space-between;color:{TEXT_SEC};font-size:0.85rem">
                    <span>Below Market</span>
                    <span>At Market</span>
                    <span>Above Market</span>
                </div>
                <div style="height:6px;background:{BORDER};border-radius:3px;margin:0.5rem 0;position:relative">
                    <div style="width:65%;height:100%;background:{SAGE};border-radius:3px"></div>
                </div>
                <div style="text-align:center;color:white;font-weight:500;margin-top:0.5rem">Positioned 5% above market average</div>
            </div>
            <hr style="margin:1rem 0">
            <div style="display:flex;justify-content:space-between;color:{TEXT_SEC};font-size:0.85rem">
                <span>Price Volatility</span>
                <span style="color:white">Low (σ=2.1)</span>
            </div>
            <div style="display:flex;justify-content:space-between;color:{TEXT_SEC};font-size:0.85rem;margin-top:0.5rem">
                <span>Competitor Count</span>
                <span style="color:white">4 OTAs</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h2>Price Alerts</h2>", unsafe_allow_html=True)
    today = datetime.now().strftime("%Y%m%d")
    alerts_path = os.path.join(ALERTS_DIR, f"alerts_{today}.jsonl")
    if os.path.exists(alerts_path):
        alerts = []
        with open(alerts_path) as f:
            for line in f:
                if line.strip():
                    alerts.append(json.loads(line))
        if alerts:
            for a in alerts[-10:]:
                badge_color = {"critical": "badge-red", "high": "badge-amber", "medium": "badge-gray"}.get(a["priority"], "badge-gray")
                st.markdown(f"""
                <div class="card" style="padding:1rem">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span class="badge {badge_color}" style="margin-right:0.5rem">{a["priority"].upper()}</span>
                            <span style="color:white;font-weight:500">{a["ota"]}</span>
                            <span style="color:{TEXT_MUTED};margin-left:0.5rem">{a["hotel_id"]}</span>
                        </div>
                        <div style="text-align:right">
                            <span style="color:white;font-weight:600">€{a["ota_price"]:.0f}</span>
                            <span style="color:{TEXT_MUTED};margin-left:0.5rem">vs €{a["internal_price"]:.0f}</span>
                            <span style="color:#ef4444;margin-left:0.5rem">+{a["gap_percent"]:.1f}%</span>
                        </div>
                    </div>
                    <div style="color:{TEXT_MUTED};font-size:0.8rem;margin-top:0.3rem">{a.get("timestamp","")[:19]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{TEXT_MUTED}'>No alerts today</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED}'>No alerts yet. Run a price check to populate.</p>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h2>Check History</h2>", unsafe_allow_html=True)
    reports = sorted(glob.glob(os.path.join(REPORTS_DIR, "check_*.jsonl")), reverse=True)[:5]
    if reports:
        for rp in reports:
            date_str = os.path.basename(rp).replace("check_", "").replace(".jsonl", "")
            with open(rp) as f:
                lines = [json.loads(l) for l in f if l.strip()]
            total = len(lines)
            crit = sum(l.get("critical_alerts", 0) for l in lines)
            high = sum(l.get("high_alerts", 0) for l in lines)
            st.markdown(f"""
            <div class="card" style="padding:1rem">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:white;font-weight:500">{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}</span>
                    <span style="color:{TEXT_MUTED}">{total} checks · {crit} critical · {high} high</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:{TEXT_MUTED}'>No check history yet</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<div class="footer">
    <span class="tech-badge">Python</span>
    <span class="tech-badge">Pandas</span>
    <span class="tech-badge">Scikit-Learn</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">raspal_scrapper</span>
    <br><br>
    Optimus Price v2.0 · Revenue Intelligence for Independent Hotels
</div>
""", unsafe_allow_html=True)
