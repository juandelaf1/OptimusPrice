# -*- coding: utf-8 -*-
"""Optimus Price — Customer Portal (connected to shared DB)"""

import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os, sys
from datetime import datetime, date

APP_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(APP_DIR, ".."))
sys.path.insert(0, APP_DIR)
PIPELINE_FILE = os.path.join(APP_DIR, "..", "models", "pipeline_trained_model.pkl")

from optimus_db import db
from shared_utils import build_input_data

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

try:
    pipeline = joblib.load(PIPELINE_FILE)
except FileNotFoundError:
    st.error(f"Modelo no encontrado: {PIPELINE_FILE}")
    st.stop()

st.markdown("""<div style="font-size:1.5rem;font-weight:700;color:white;">▌ Optimus Price</div>""", unsafe_allow_html=True)
st.markdown("<p style='margin-top:-0.5rem'>Sistema de Reservas Hoteleras</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Nueva Reserva", "Mis Datos"])

session_id = datetime.now().strftime("%y%m%d%H%M%S") + str(os.getpid())

with tab1:
    st.markdown("<h2>Datos Personales</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Email")
    with col2:
        telefono = st.text_input("Telefono")
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
            st.error("Complete los campos obligatorios")
        else:
            input_data = build_input_data(
                parking, lead_time, fecha_llegada, 0,
                len([r for r in special.split(",") if r.strip()]) if special else 0,
                meal_plan, room_type, total_guests, total_nights
            )
            try:
                pred = pipeline.predict(input_data)[0]
                override = db.get_active_override()
                override_pct = override["modifier_percent"] if override else 0
                final_price = pred * (1 + override_pct / 100)
                total = final_price * total_nights

                st.markdown(f"""<div style="display:flex;gap:1rem;margin:1rem 0">
                    <div style="flex:1;background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1.5rem;text-align:center">
                        <p style="color:{TEXT_MUTED};font-size:0.8rem">Precio por noche</p>
                        <p style="color:{SAGE};font-size:2rem;font-weight:700">€{final_price:.2f}</p>
                    </div>
                    <div style="flex:1;background:#111827;border:1px solid {BORDER};border-radius:12px;padding:1.5rem;text-align:center">
                        <p style="color:{TEXT_MUTED};font-size:0.8rem">Total {total_nights} noches</p>
                        <p style="color:white;font-size:2rem;font-weight:700">€{total:.2f}</p>
                    </div>
                </div>""", unsafe_allow_html=True)

                db.save_query({
                    "session_id": session_id, "total_guests": total_guests,
                    "total_nights": total_nights, "lead_time": lead_time,
                    "arrival_month": fecha_llegada.month, "room_type": room_type,
                    "meal_plan": meal_plan, "predicted_price": float(pred),
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
                st.error(f"Error en prediccion: {e}")

with tab2:
    st.markdown("<h2>Consultar Reserva</h2>", unsafe_allow_html=True)
    search_email = st.text_input("Ingrese su email para consultar")
    if search_email:
        reservations = db.get_reservations(limit=100)
        user_reservations = [r for r in reservations if r.get("email") == search_email]
        if user_reservations:
            df = pd.DataFrame(user_reservations)
            st.dataframe(df[["created_at", "fecha_llegada", "fecha_salida", "precio_total"]], use_container_width=True, hide_index=True)
        else:
            st.markdown(f"<p style='color:{TEXT_MUTED}'>No se encontraron reservas</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""<div style="text-align:center;color:{TEXT_MUTED};font-size:0.75rem">
    Optimus Price v2.0 · Revenue Intelligence for Independent Hotels
</div>""", unsafe_allow_html=True)
