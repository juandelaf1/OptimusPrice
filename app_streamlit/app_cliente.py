# -*- coding: utf-8 -*-
"""
Optimus Price V1 — Customer Portal
Predicts hotel room prices with confidence range and key drivers.
"""

import streamlit as st
import os, sys
from datetime import datetime, date

APP_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(APP_DIR, ".."))

from optimus_db import db
from src.optimus_price.prediction_service import PredictionService

# V2 Market Context
try:
    from src.v2_pipeline.market_context import MarketContextProvider
    market_context_available = True
except ImportError:
    market_context_available = False

st.set_page_config(page_title="Optimus Price — Reservas", layout="centered", page_icon="▌")

DARK_BG = "#0F1720"
SAGE = "#A3B18A"
TEXT_SEC = "#B0B8C5"
TEXT_MUTED = "#7C8595"
BORDER = "#242D3D"

page_style = f"""
<style>
    .stApp {{ background: {DARK_BG}; }}
    .block-container {{ padding: 2rem; }}
    h1,h2,h3,h4,h5,h6,p,li,span {{ font-family: -apple-system, 'Inter', 'SF Pro', sans-serif; }}
    h1 {{ color: white; font-size: 1.75rem; font-weight: 600; }}
    h2 {{ color: white; font-size: 1.25rem; font-weight: 500; }}
    h3 {{ color: white; font-size: 1rem; font-weight: 500; }}
    p, label, .stTextInput label, .stSelectbox label, .stNumberInput label {{ color: {TEXT_SEC} !important; font-size: 0.9rem !important; }}
    div[data-testid="stMetricValue"] {{ font-size: 2rem !important; color: white !important; }}
    .stButton button {{ background: white; color: {DARK_BG}; border-radius: 12px; font-weight: 500; border: none; padding: 0.5rem 2rem; }}
    .stButton button:hover {{ background: {SAGE}; }}
    .stSuccess, .stInfo {{ background: #111827; border: 1px solid {BORDER}; border-radius: 12px; color: {TEXT_SEC}; }}
    hr {{ border-color: {BORDER}; }}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

@st.cache_resource
def load_prediction_service():
    service = PredictionService()
    service.load()
    return service

try:
    prediction_service = load_prediction_service()
except Exception as e:
    st.error("Error al cargar el modelo. Contacte al administrador.")
    st.stop()

st.markdown("""<div style="font-size:1.5rem;font-weight:700;color:white;">▌ Optimus Price</div>""", unsafe_allow_html=True)
st.markdown("<p style='margin-top:-0.5rem'>Sistema de Prediccion de Precios Hoteleros</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Nueva Reserva", "Mis Datos"])

session_id = datetime.now().strftime("%y%m%d%H%M%S") + str(os.getpid())

with tab1:
    st.markdown("<h2>Datos Personales</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre completo *")
        email = st.text_input("Email *")
    with col2:
        telefono = st.text_input("Telefono *")
        nacionalidad = st.text_input("Nacionalidad", "Espanola")

    st.markdown("<h2>Detalles de la Reserva</h2>", unsafe_allow_html=True)
    today = date.today()
    col3, col4 = st.columns(2)
    with col3:
        fecha_llegada = st.date_input("Fecha de llegada", min_value=date(2025,1,1))
    with col4:
        fecha_salida = st.date_input("Fecha de salida", min_value=fecha_llegada)

    lead_time = (fecha_llegada - today).days
    total_nights = (fecha_salida - fecha_llegada).days
    season = "Alta" if fecha_llegada.month in [6,7,8,12] else "Media" if fecha_llegada.month in [4,5,9,10,11] else "Baja"
    st.markdown(f"<p style='color:{TEXT_MUTED};font-size:0.85rem'>Anticipacion: {lead_time} dias · Duracion: {total_nights} noches · Temporada: {season}</p>", unsafe_allow_html=True)

    st.markdown("<h2>Preferencias</h2>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        meal_plan = st.radio("Plan de comidas", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
        room_type = st.selectbox("Tipo de habitacion", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
    with col6:
        total_guests = st.number_input("Numero de huespedes", 1, 10, 2)
        parking = st.checkbox("Requiere estacionamiento")
        special = st.text_area("Solicitudes especiales")

    if st.button("Calcular Precio", type="primary"):
        if not all([nombre, email, telefono]):
            st.error("Complete los campos obligatorios (nombre, email, telefono)")
        else:
            try:
                from shared_utils import build_input_data
                input_array = build_input_data(
                    parking, lead_time, fecha_llegada, 0,
                    len([r for r in special.split(",") if r.strip()]) if special else 0,
                    meal_plan, room_type, total_guests, total_nights
                )
                
                import numpy as np
                feature_names = [
                    "room_type_value", "arrival_year", "market_segment_value",
                    "total_guests", "children", "arrival_month", "lead_time",
                    "booking_status", "arrival_week_number", "distribution_channel",
                    "meal_plan", "deposit_type", "adults", "special_requests",
                    "arrival_date", "booking_changes", "customer_type",
                    "previous_cancellations", "weekend_nights", "previous_bookings",
                    "week_nights", "parking_spaces", "waiting_list",
                    "repeated_guest", "arrival_day_of_week", "total_nights", "babies"
                ]
                input_dict = dict(zip(feature_names, input_array[0]))
                input_dict["total_nights"] = total_nights
                input_dict["total_guests"] = total_guests
                input_dict["children"] = max(0, total_guests - 2)
                input_dict["adults"] = min(total_guests, 2)
                
                result = prediction_service.predict(input_dict)
                
                override = db.get_active_override()
                override_pct = override["modifier_percent"] if override else 0
                final_price = result.predicted_price * (1 + override_pct / 100)
                total = final_price * total_nights

                st.markdown(f"""<div style="display:flex;gap:1rem;margin:1rem 0">
                    <div style="flex:1;background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1.5rem;text-align:center">
                        <p style="color:{TEXT_MUTED};font-size:0.8rem">Precio estimado por noche</p>
                        <p style="color:{SAGE};font-size:2rem;font-weight:700">€{final_price:.2f}</p>
                    </div>
                    <div style="flex:1;background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1.5rem;text-align:center">
                        <p style="color:{TEXT_MUTED};font-size:0.8rem">Total {total_nights} noches</p>
                        <p style="color:white;font-size:2rem;font-weight:700">€{total:.2f}</p>
                    </div>
                </div>""", unsafe_allow_html=True)

                low = result.confidence_range["low"] * (1 + override_pct / 100)
                high = result.confidence_range["high"] * (1 + override_pct / 100)
                st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1rem;margin:0.5rem 0">
                    <p style="color:{TEXT_MUTED};font-size:0.8rem;margin:0">
                        Rango de estimacion: €{low:.2f} — €{high:.2f} por noche
                    </p>
                </div>""", unsafe_allow_html=True)

                if result.key_drivers:
                    st.markdown("<h3>Factores que influyen en el precio</h3>", unsafe_allow_html=True)
                    drivers_html = ""
                    for d in result.key_drivers[:5]:
                        color = SAGE if d["impact"] > 0 else "#EF4444"
                        sign = "+" if d["impact"] > 0 else ""
                        drivers_html += f"""<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid {BORDER}">
                            <span style="color:{TEXT_SEC};font-size:0.85rem">{d['feature'].replace('_', ' ').title()}</span>
                            <span style="color:{color};font-size:0.85rem;font-weight:500">{sign}€{d['impact']:.2f}</span>
                        </div>"""
                    st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1rem">
                        {drivers_html}
                    </div>""", unsafe_allow_html=True)

                # V2 Market Context
                if market_context_available:
                    try:
                        ctx_provider = MarketContextProvider()
                        market_ctx = ctx_provider.adjust_prediction(
                            base_price=float(result.predicted_price),
                            region='mallorca',
                            segment='playa_costa',
                            target_date=fecha_llegada,
                        )
                        
                        st.markdown("<h3>Contexto de Mercado</h3>", unsafe_allow_html=True)
                        
                        # Market context metrics
                        col_m1, col_m2, col_m3 = st.columns(3)
                        
                        with col_m1:
                            if market_ctx['context'].get('seasonality'):
                                factor = market_ctx['context']['seasonality']['factor']
                                is_peak = market_ctx['context']['seasonality']['is_peak']
                                label = "Peak" if is_peak else "Baja" if factor < 0.8 else "Normal"
                                color_peak = "#EF4444" if is_peak else SAGE if factor >= 0.8 else "#F59E0B"
                                st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1rem;text-align:center">
                                    <p style="color:{TEXT_MUTED};font-size:0.75rem">Temporada</p>
                                    <p style="color:{color_peak};font-size:1.2rem;font-weight:600">{label}</p>
                                    <p style="color:{TEXT_SEC};font-size:0.8rem">Factor: x{factor:.2f}</p>
                                </div>""", unsafe_allow_html=True)
                        
                        with col_m2:
                            if market_ctx['context'].get('market_index'):
                                avg_price = market_ctx['context']['market_index'].get('avg_price', 0)
                                st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1rem;text-align:center">
                                    <p style="color:{TEXT_MUTED};font-size:0.75rem">Precio Medio Mercado</p>
                                    <p style="color:white;font-size:1.2rem;font-weight:600">€{avg_price:.0f}</p>
                                    <p style="color:{TEXT_SEC};font-size:0.8rem">Mallorca</p>
                                </div>""", unsafe_allow_html=True)
                        
                        with col_m3:
                            if market_ctx['adjustment_factor'] != 1.0:
                                adj_color = "#22C55E" if market_ctx['adjusted_price'] > result.predicted_price else "#EF4444"
                                st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1rem;text-align:center">
                                    <p style="color:{TEXT_MUTED};font-size:0.75rem">Ajuste Mercado</p>
                                    <p style="color:{adj_color};font-size:1.2rem;font-weight:600">€{market_ctx['adjusted_price']:.2f}</p>
                                    <p style="color:{TEXT_SEC};font-size:0.8rem">x{market_ctx['adjustment_factor']:.3f}</p>
                                </div>""", unsafe_allow_html=True)
                        
                        # Recommendations
                        if market_ctx['context'].get('recommendations'):
                            st.markdown("<p style='color:{TEXT_SEC};font-size:0.85rem;margin-top:0.5rem'><b>Recomendaciones de Mercado:</b></p>", unsafe_allow_html=True)
                            recs_html = ""
                            for rec in market_ctx['context']['recommendations'][:3]:
                                priority_color = "#EF4444" if rec['priority'] == 'high' else "#F59E0B"
                                recs_html += f"""<div style="padding:0.3rem 0;border-bottom:1px solid {BORDER}">
                                    <span style="color:{priority_color};font-size:0.75rem">[{rec['priority'].upper()}]</span>
                                    <span style="color:{TEXT_SEC};font-size:0.8rem">{rec['message']}</span>
                                </div>"""
                            st.markdown(f"""<div style="background:#111827;border:1px solid {BORDER};border-radius:12px;padding:0.8rem;margin-top:0.5rem">
                                {recs_html}
                            </div>""", unsafe_allow_html=True)
                    
                    except Exception as e:
                        pass  # Silently fail if market context unavailable

                db.save_query({
                    "session_id": session_id, "total_guests": total_guests,
                    "total_nights": total_nights, "lead_time": lead_time,
                    "arrival_month": fecha_llegada.month, "room_type": room_type,
                    "meal_plan": meal_plan, "predicted_price": float(result.predicted_price),
                    "market_adjustment": override_pct, "final_price": float(final_price),
                    "source": "customer_portal"
                })

                if st.button("Confirmar Reserva"):
                    db.save_reservation({
                        "nombre": nombre, "email": email, "telefono": telefono,
                        "documento": "", "nacionalidad": nacionalidad,
                        "tipo_cliente": "Normal",
                        "fecha_llegada": fecha_llegada.isoformat(),
                        "fecha_salida": fecha_salida.isoformat(),
                        "noches": total_nights, "tipo_habitacion": room_type,
                        "huespedes": total_guests, "plan_comidas": meal_plan,
                        "solicitudes_especiales": special,
                        "estacionamiento": int(parking),
                        "precio_noche": round(final_price, 2),
                        "precio_total": round(total, 2),
                        "lead_time": lead_time, "temporada": season,
                        "override_modifier": override_pct,
                        "precio_final": round(total, 2),
                        "source": "customer_portal"
                    })
                    st.success(f"Reserva confirmada! Total: EUR {total:.2f}")
                    st.balloons()
            except Exception as e:
                st.error("Error al calcular el precio. Intente de nuevo.")

with tab2:
    st.markdown("<h2>Consultar Reserva</h2>", unsafe_allow_html=True)
    search_email = st.text_input("Ingrese su email para consultar")
    if search_email:
        reservations = db.get_reservations(limit=100)
        user_reservations = [r for r in reservations if r.get("email") == search_email]
        if user_reservations:
            import pandas as pd
            df = pd.DataFrame(user_reservations)
            display_cols = {
                "created_at": "Fecha",
                "fecha_llegada": "Llegada",
                "fecha_salida": "Salida",
                "precio_total": "Total (EUR)"
            }
            st.dataframe(df[list(display_cols.keys())].rename(columns=display_cols), use_container_width=True, hide_index=True)
        else:
            st.markdown(f"<p style='color:{TEXT_MUTED}'>No se encontraron reservas para este email</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""<div style="text-align:center;color:{TEXT_MUTED};font-size:0.75rem">
    Optimus Price V1 + V2 Market Intelligence · Prediccion de Precios Hoteleros
</div>""", unsafe_allow_html=True)
