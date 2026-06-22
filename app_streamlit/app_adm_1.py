import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import os
import csv

st.set_page_config(page_title="Optimus Price Advisor", layout="centered")
page_bg_gradient = """
<style>
.stApp {
    background: linear-gradient(to bottom, #E0E0E0, #A9A9A9);
}
</style>
"""
st.markdown(page_bg_gradient, unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "hotel_reservations.csv")
PIPELINE_FILE = os.path.join(BASE_DIR, "..", "models", "pipeline_trained_model.pkl")
OVERRIDE_FILE = os.path.join(BASE_DIR, "price_override.txt")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def save_to_csv(data):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def build_input_data(required_car_parking, lead_time, fecha_llegada,
                     repeated_guest, special_requests_count, meal_plan, room_type,
                     total_guests, total_nights):
    arrival_year = fecha_llegada.year
    arrival_month = fecha_llegada.month
    arrival_date = fecha_llegada.day
    arrival_day_of_week = fecha_llegada.weekday()
    arrival_week_number = fecha_llegada.isocalendar()[1]
    no_prev_cancel = 0
    no_prev_bookings = 0
    meal_plan_2 = int(meal_plan in ["Desayuno incluido", "Cena incluida", "Todo incluido"])
    meal_not_selected = int(meal_plan == "Ninguno")
    rt2 = int(room_type == "Individual")
    rt3 = int(room_type == "Doble")
    rt4 = int(room_type == "Twin")
    rt5 = int(room_type == "Triple")
    rt6 = int(room_type == "Suite")
    rt7 = int(room_type == "Familiar")
    ms_compl = 0
    ms_corp = 0
    ms_off = 0
    ms_onl = 0
    booking_not_canceled = 1
    data = np.array([[
        int(required_car_parking),
        lead_time,
        arrival_year,
        arrival_month,
        arrival_date,
        int(repeated_guest),
        no_prev_cancel,
        no_prev_bookings,
        special_requests_count,
        meal_plan_2,
        meal_not_selected,
        rt2,
        rt3,
        rt4,
        rt5,
        rt6,
        rt7,
        ms_compl,
        ms_corp,
        ms_off,
        ms_onl,
        booking_not_canceled,
        total_guests,
        total_nights,
        arrival_day_of_week,
        arrival_week_number
    ]])
    return data

def build_input_mod(required_car_parking_mod, lead_time_mod, mes_mod, special_requests_mod,
                    meal_plan_mod, room_type_mod, total_guests_mod, total_nights_mod, fecha_ref):
    try:
        fecha_mod = fecha_ref.replace(month=mes_mod)
    except ValueError:
        fecha_mod = fecha_ref.replace(month=mes_mod, day=28)
    arrival_year_mod = fecha_mod.year
    arrival_date_mod = fecha_mod.day
    arrival_day_of_week_mod = fecha_mod.weekday()
    arrival_week_number_mod = fecha_mod.isocalendar()[1]
    m_plan2 = int(meal_plan_mod in ["Desayuno incluido", "Cena incluida", "Todo incluido"])
    m_not_selected = int(meal_plan_mod == "Ninguno")
    rt2_mod = int(room_type_mod == "Individual")
    rt3_mod = int(room_type_mod == "Doble")
    rt4_mod = int(room_type_mod == "Twin")
    rt5_mod = int(room_type_mod == "Triple")
    rt6_mod = int(room_type_mod == "Suite")
    rt7_mod = int(room_type_mod == "Familiar")
    ms_compl_mod = 0
    ms_corp_mod = 0
    ms_off_mod = 0
    ms_onl_mod = 0
    booking_not_canceled_mod = 1
    data_mod = np.array([[
        int(required_car_parking_mod),
        lead_time_mod,
        arrival_year_mod,
        mes_mod,
        arrival_date_mod,
        0,
        0,
        0,
        special_requests_mod,
        m_plan2,
        m_not_selected,
        rt2_mod,
        rt3_mod,
        rt4_mod,
        rt5_mod,
        rt6_mod,
        rt7_mod,
        ms_compl_mod,
        ms_corp_mod,
        ms_off_mod,
        ms_onl_mod,
        booking_not_canceled_mod,
        total_guests_mod,
        total_nights_mod,
        arrival_day_of_week_mod,
        arrival_week_number_mod
    ]])
    return data_mod

role = st.sidebar.selectbox("Selecciona el rol", ["Cliente", "Administrador"])
show_admin = False
if role == "Administrador":
    admin_password = st.sidebar.text_input("Contraseña de Administrador", type="password")
    if admin_password:
        if admin_password == ADMIN_PASSWORD:
            st.sidebar.success("Acceso de administrador concedido")
            show_admin = True
        else:
            st.sidebar.error("Contraseña incorrecta.")

page = st.sidebar.selectbox("Seleccione la Página", ["Reservas", "Recomendaciones"])

if show_admin:
    st.sidebar.markdown("### Configuración de Precio Manual")
    manual_modifier = st.sidebar.slider("Ajuste manual de precio (%)", -20, 30, 0, step=1)
    if st.sidebar.button("Guardar Ajuste Manual"):
        with open(OVERRIDE_FILE, "w") as f:
            f.write(str(manual_modifier))
        st.sidebar.success("Ajuste manual guardado.")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Historial de Reservas")
    if os.path.exists(DATA_FILE):
        hist = pd.read_csv(DATA_FILE)
        st.sidebar.dataframe(hist.tail(5))
        csv_hist = hist.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Descargar historial", data=csv_hist, file_name="historial_reservas.csv", mime="text/csv")
    else:
        st.sidebar.info("No hay reservas aún.")

try:
    pipeline = joblib.load(PIPELINE_FILE)
except FileNotFoundError:
    st.error(f"Error: Pipeline del modelo no encontrado en {PIPELINE_FILE}")
    st.stop()

logo_path = os.path.join(BASE_DIR, "..", "docs", "img", "optimus_price_logo.jpg")
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)

st.title("Optimus Price Advisor")
st.markdown("##### Complete los datos de la reserva para analizar estrategias de precios:")

if page == "Reservas":
    st.header("Formulario de Reserva")
    col_pers1, col_pers2 = st.columns(2)
    with col_pers1:
        nombre = st.text_input("Nombre completo*", help="Nombre y apellidos")
        email = st.text_input("Email*", help="Email de contacto")
        telefono = st.text_input("Teléfono*", help="Número de contacto")
    with col_pers2:
        documento = st.text_input("Documento de identidad*", help="DNI, pasaporte u otra identificación")
        nacionalidad = st.text_input("Nacionalidad", "Española")
        vip_status = st.selectbox("Tipo de cliente", ["Normal", "VIP", "Corporativo"])

    st.header("Detalles de la Reserva")
    today = date.today()
    col_fechas1, col_fechas2 = st.columns(2)
    with col_fechas1:
        fecha_llegada = st.date_input("Fecha de llegada*", min_value=datetime(2025,1,1), max_value=datetime(2027,12,31))
    with col_fechas2:
        fecha_salida = st.date_input("Fecha de salida*", min_value=fecha_llegada)
    lead_time = (fecha_llegada - today).days
    total_nights = (fecha_salida - fecha_llegada).days
    st.info(f"""Resumen:
- Anticipacion: {lead_time} dias
- Duracion: {total_nights} noches
- Temporada: {"Alta" if fecha_llegada.month in [6,7,8,12] else "Media" if fecha_llegada.month in [4,5,9,10,11] else "Baja"}""")

    st.header("Preferencias de Hospedaje")
    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        st.markdown("**Servicios:**")
        meal_2 = st.radio("Plan de comidas*", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
        special_requests = st.text_area("Solicitudes especiales")
    with col_pref2:
        st.markdown("**Habitacion:**")
        room_type = st.selectbox("Tipo de habitacion*", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
        total_guests = st.number_input("Numero de huespedes*", min_value=1, max_value=10, value=2)
        required_car_parking = st.checkbox("Requiere estacionamiento")

    input_data = build_input_data(required_car_parking, lead_time, fecha_llegada,
                                  repeated_guest=0,
                                  special_requests_count=len([r for r in special_requests.split(",") if r.strip()]) if special_requests else 0,
                                  meal_plan=meal_2,
                                  room_type=room_type,
                                  total_guests=total_guests,
                                  total_nights=total_nights)

    try:
        prediccion_base = pipeline.predict(input_data)[0]
        override_modifier = 0
        if os.path.exists(OVERRIDE_FILE):
            with open(OVERRIDE_FILE, "r") as f:
                try:
                    override_modifier = float(f.read().strip())
                except Exception:
                    override_modifier = 0
        precio_ajustado = prediccion_base * (1 + override_modifier/100)
        st.markdown("### Precio Sugerido")
        st.success(f"Precio por noche sugerido: ${precio_ajustado:.2f} USD")
    except Exception as e:
        st.error(f"Error en la prediccion: {e}")

    if st.button("Confirmar Reserva y Calcular Precio", type="primary"):
        mandatory_fields = {
            "Nombre": nombre,
            "Email": email,
            "Telefono": telefono,
            "Documento": documento,
            "Fechas": fecha_llegada and fecha_salida
        }
        missing_fields = [k for k, v in mandatory_fields.items() if not v]
        if missing_fields:
            st.error(f"Faltan campos obligatorios: {', '.join(missing_fields)}")
        else:
            total_price = precio_ajustado * total_nights
            st.success(f"Total a pagar ({total_nights} noches): ${total_price:.2f}")

            reservation_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre_cliente": nombre,
                "email": email,
                "telefono": telefono,
                "documento": documento,
                "nacionalidad": nacionalidad,
                "tipo_cliente": vip_status,
                "fecha_llegada": fecha_llegada.strftime("%Y-%m-%d"),
                "fecha_salida": fecha_salida.strftime("%Y-%m-%d"),
                "noches": total_nights,
                "tipo_habitacion": room_type,
                "huespedes": total_guests,
                "plan_comidas": meal_2,
                "solicitudes_especiales": special_requests,
                "estacionamiento": required_car_parking,
                "precio_noche": round(precio_ajustado, 2),
                "precio_total": round(total_price, 2),
                "lead_time": lead_time,
                "temporada": "Alta" if fecha_llegada.month in [6,7,8,12] else "Media" if fecha_llegada.month in [4,5,9,10,11] else "Baja"
            }
            save_to_csv(reservation_data)
            st.balloons()
            st.success("Reserva registrada correctamente")
            st.subheader("Recibo de Reserva")
            st.json({k: v for k, v in reservation_data.items() if k != "timestamp"})
            df_reserva = pd.DataFrame([reservation_data])
            csv_data = df_reserva.to_csv(index=False).encode("utf-8")
            st.download_button(label="Descargar comprobante", data=csv_data,
                               file_name=f"reserva_{documento}_{fecha_llegada.strftime('%Y%m%d')}.csv",
                               mime="text/csv")

elif page == "Recomendaciones":
    st.header("Recomendaciones de Precio")
    st.markdown("Ajuste los parametros para simular diferentes escenarios de reserva y vea como cambia el precio recomendado.")

    today = date.today()
    fecha_ref = st.date_input("Fecha de referencia para la simulacion", today)
    col1, col2 = st.columns(2)
    with col1:
        lead_time_mod = st.number_input("Anticipacion (dias)", min_value=0, max_value=365, value=30)
        mes_mod = st.selectbox("Mes de llegada", range(1, 13), format_func=lambda x: datetime(2025, x, 1).strftime("%B"))
        total_nights_mod = st.number_input("Numero de noches", min_value=1, max_value=30, value=3)
        meal_plan_mod = st.selectbox("Plan de comidas", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
    with col2:
        room_type_mod = st.selectbox("Tipo de habitacion", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
        total_guests_mod = st.number_input("Numero de huespedes", min_value=1, max_value=10, value=2)
        required_car_parking_mod = st.checkbox("Requiere estacionamiento")
        special_requests_mod = st.number_input("Solicitudes especiales", min_value=0, max_value=10, value=0)

    input_mod = build_input_mod(required_car_parking_mod, lead_time_mod, mes_mod, special_requests_mod,
                                meal_plan_mod, room_type_mod, total_guests_mod, total_nights_mod, fecha_ref)

    try:
        precio_mod = pipeline.predict(input_mod)[0]
        st.markdown("### Resultado de la Simulacion")
        st.success(f"Precio estimado por noche: ${precio_mod:.2f} USD")
    except Exception as e:
        st.error(f"Error en la prediccion: {e}")
