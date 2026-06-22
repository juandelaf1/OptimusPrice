import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, date
import csv

# Configuración de la página y fondo
st.set_page_config(page_title="Hotel Reservation System", layout="centered")
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

def save_to_csv(data):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Cargar el pipeline completo (modelo + scaler integrado)
try:
    pipeline = joblib.load(PIPELINE_FILE)
except FileNotFoundError:
    st.error("❌ Error: Pipeline del modelo no encontrado")
    st.write(f"Asegúrate de que exista: {PIPELINE_FILE}")
    st.stop()

# Título e imagen
st.image("https://media.istockphoto.com/id/1028630524/es/foto/servicio-de-portero-en-recepci%C3%B3n-del-hotel.jpg?s=612x612&w=0&k=20&c=vmAibFhevHSeOlyrj0nzoZtAt-zCYtFmZd0cPqEIYQI=", use_container_width=True)
st.title("🏨 Sistema de Reservas Hoteleras")

# --- Sección 1: Datos Personales ---
st.header("👤 Datos Personales del Cliente")
col_pers1, col_pers2 = st.columns(2)
with col_pers1:
    nombre = st.text_input("Nombre completo*", help="Nombre y apellidos")
    email = st.text_input("Email*", help="Email de contacto")
    telefono = st.text_input("Teléfono*", help="Número de contacto")
with col_pers2:
    documento = st.text_input("Documento de identidad*", help="DNI, pasaporte u otra identificación")
    nacionalidad = st.text_input("Nacionalidad", "Española")
    vip_status = st.selectbox("Tipo de cliente", ["Normal", "VIP", "Corporativo"])

# --- Sección 2: Detalles de la Reserva ---
st.header("📅 Detalles de la Reserva")
today = date.today()
col_fechas1, col_fechas2 = st.columns(2)
with col_fechas1:
    fecha_llegada = st.date_input("Fecha de llegada*", min_value=datetime(2025,1,1), max_value=datetime(2027,12,31))
with col_fechas2:
    fecha_salida = st.date_input("Fecha de salida*", min_value=fecha_llegada)
lead_time = (fecha_llegada - today).days
total_nights = (fecha_salida - fecha_llegada).days
arrival_year = fecha_llegada.year
arrival_month = fecha_llegada.month
arrival_date = fecha_llegada.day
# Variables derivadas de fecha
arrival_day_of_week = fecha_llegada.weekday()         # 0 = lunes, 6 = domingo
arrival_week_number = fecha_llegada.isocalendar()[1]
st.info(f"""📊 Resumen:
- **Anticipación:** {lead_time} días
- **Duración:** {total_nights} noches
- **Temporada:** {"Alta" if arrival_month in [6,7,8,12] else "Media" if arrival_month in [4,5,9,10,11] else "Baja"}""")

# --- Sección 3: Preferencias de Hospedaje ---
st.header("🛌 Preferencias de Hospedaje")
col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    st.subheader("🍽 Servicios")
    meal_plan = st.radio("Plan de comidas*", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
    special_requests = st.text_area("Solicitudes especiales")
with col_pref2:
    st.subheader("🛏 Habitación")
    room_type = st.selectbox("Tipo de habitación*", ['Individual', 'Doble', 'Twin', 'Suite', 'Familiar', 'Presidencial'])
    total_guests = st.number_input("Número de huéspedes*", min_value=1, max_value=10, value=2)
    required_car_parking = st.checkbox("Requiere estacionamiento")

# --- Sección 4: Método de Pago ---
st.header("💳 Información de Pago")
payment_method = st.selectbox("Método de pago*", ['Transferencia', 'Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito'])

# --- Preparar datos para el modelo (26 features) ---

# Variables no solicitadas (por defecto)
repeated_guest = 0
no_of_previous_cancellations = 0
no_of_previous_bookings_not_canceled = 0
special_requests_count = len([r.strip() for r in special_requests.split(",") if r.strip()]) if special_requests else 0

# Conversion de plan de comidas a variables binarias
if meal_plan == "Todo incluido":
    meal_plan_2, meal_plan_3, meal_not_selected = 1, 1, 0
else:
    meal_plan_2 = int(meal_plan == "Desayuno incluido")
    meal_plan_3 = int(meal_plan == "Cena incluida")
    meal_not_selected = int(meal_plan == "Ninguno")

# Codificación para el tipo de habitación (one-hot con drop_first, Room_Type_1 es referencia)
rt2 = int(room_type == "Individual")
rt3 = int(room_type == "Doble")
rt4 = int(room_type == "Twin")
rt5 = int(room_type == "Triple")
rt6 = int(room_type == "Suite")
rt7 = int(room_type == "Familiar")

# Variables de mercado (todas 0 = categoría de referencia)
ms_compl = 0
ms_corp = 0
ms_off = 0
ms_onl = 0

booking_not_canceled = 1  # Nueva reserva, no cancelada

# Construir vector de entrada (26 features) en el orden exacto del modelo entrenado
input_data = np.array([[
    int(required_car_parking),
    lead_time,
    arrival_year,
    arrival_month,
    arrival_date,
    repeated_guest,
    no_of_previous_cancellations,
    no_of_previous_bookings_not_canceled,
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

# --- Mostrar el precio por noche antes de confirmar ---
try:
    precio_sugerido = pipeline.predict(input_data)[0]
    st.markdown("### Precio medio por noche")
    st.success(f"**Precio por noche :** ${precio_sugerido:.2f} USD")
except Exception as e:
    st.error(f"Error en la predicción: {e}")

# --- Botón de Proceso para confirmar reserva ---
if st.button("💳 Confirmar Reserva y Calcular Precio", type="primary"):
    mandatory_fields = {
        "Nombre": nombre,
        "Email": email,
        "Teléfono": telefono,
        "Documento": documento,
        "Fechas": fecha_llegada and fecha_salida,
        "Método de pago": payment_method
    }
    missing_fields = [k for k, v in mandatory_fields.items() if not v]
    if missing_fields:
        st.error(f"❌ Faltan campos obligatorios: {', '.join(missing_fields)}")
    else:
        # Reutilizamos el precio sugerido calculado anteriormente
        total_price = precio_sugerido * total_nights
        st.success(f"**Total a pagar ({total_nights} noches):** ${total_price:.2f}")

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
            "plan_comidas": meal_plan,
            "solicitudes_especiales": special_requests,
            "estacionamiento": required_car_parking,
            "metodo_pago": payment_method,
            "precio_noche": round(precio_sugerido, 2),
            "precio_total": round(total_price, 2),
            "lead_time": lead_time,
            "temporada": "Alta" if arrival_month in [6,7,8,12] else "Media" if arrival_month in [4,5,9,10,11] else "Baja"
        }
        save_to_csv(reservation_data)
        st.balloons()
        st.success("✅ Reserva registrada correctamente")
        st.subheader("📝 Recibo de Reserva")
        st.json({k: v for k, v in reservation_data.items() if k != "timestamp"})
        df_reserva = pd.DataFrame([reservation_data])
        csv_data = df_reserva.to_csv(index=False).encode("utf-8")
        st.download_button(label="📄 Descargar comprobante", data=csv_data,
                           file_name=f"reserva_{documento}_{fecha_llegada.strftime('%Y%m%d')}.csv",
                           mime="text/csv")