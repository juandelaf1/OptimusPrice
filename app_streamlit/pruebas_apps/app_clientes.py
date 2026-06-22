import streamlit as st
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, date
import csv

st.set_page_config(page_title="Hotel Reservation System", layout="centered")


page_bg_gradient = """
<style>
    .stApp {
        background: linear-gradient(to bottom, #E0E0E0, #A9A9A9); /* Degradado gris claro */
    }
</style>
"""

st.markdown(page_bg_gradient, unsafe_allow_html=True)


# Configuración de archivos
DATA_FILE = "hotel_reservations.csv"
MODEL_FILE = r"C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\Optimus_Price_proyecto_final_ML\models\trained_model_1.pkl"
SCALER_FILE = r"C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\Optimus_Price_proyecto_final_ML\models\scaler_trained_model_1.pkl"

# Función para guardar datos
def save_to_csv(data):
    file_exists = os.path.isfile(DATA_FILE)
    
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Cargar modelo (con manejo de errores)
try:
    modelo = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)
except FileNotFoundError:
    st.error("❌ Error: Archivos del modelo no encontrados")
    st.write(f"Por favor asegúrate que estos archivos existan:")
    st.write(f"- {MODEL_FILE}")
    st.write(f"- {SCALER_FILE}")
    st.stop()

# Título e imagen
st.image("https://media.istockphoto.com/id/1028630524/es/foto/servicio-de-portero-en-recepci%C3%B3n-del-hotel.jpg?s=612x612&w=0&k=20&c=vmAibFhevHSeOlyrj0nzoZtAt-zCYtFmZd0cPqEIYQI=",
         caption=None, use_container_width=True)
st.title("🏨 Sistema de Reservas Hoteleras")

# Sección 1: Datos Personales
st.header("👤 Datos Personales del Cliente")

col_pers1, col_pers2 = st.columns(2)

with col_pers1:
    nombre = st.text_input("Nombre completo*", help="Nombre y apellidos del cliente")
    email = st.text_input("Email*", help="Email de contacto")
    telefono = st.text_input("Teléfono*", help="Número de contacto")

with col_pers2:
    documento = st.text_input("Documento de identidad*", help="DNI, pasaporte o identificación")
    nacionalidad = st.text_input("Nacionalidad", "Española")
    vip_status = st.selectbox("Tipo de cliente", ["Normal", "VIP", "Corporativo"])

# Sección 2: Detalles de la Reserva
st.header("📅 Detalles de la Reserva")

# Fecha actual y fecha de llegada
today = date.today()
col_fechas1, col_fechas2 = st.columns(2)

with col_fechas1:
    fecha_llegada = st.date_input("Fecha de llegada*", min_value=datetime(2025, 1, 1), max_value=datetime(2027, 12, 31))

with col_fechas2:
    fecha_salida = st.date_input("Fecha de salida*", min_value=fecha_llegada)

# Calcular estadísticas
lead_time = (fecha_llegada - today).days
total_nights = (fecha_salida - fecha_llegada).days
arrival_year = fecha_llegada.year
arrival_month = fecha_llegada.month
arrival_date = fecha_llegada.day

st.info(f"""
📊 Resumen estadístico:
- **Anticipación:** {lead_time} días
- **Duración:** {total_nights} noches
- **Temporada:** {'Alta' if arrival_month in [6,7,8,12] else 'Media' if arrival_month in [4,5,9,10,11] else 'Baja'}
""")

# Sección 3: Preferencias de Hospedaje
st.header("🛌 Preferencias de Hospedaje")

col_pref1, col_pref2 = st.columns(2)

with col_pref1:
    st.subheader("🍽 Servicios")
    meal_plan = st.radio("Plan de comidas*", ['Ninguno', 'Desayuno incluido', 'Cena incluida', 'Todo incluido'])
    special_requests = st.text_area("Solicitudes especiales")

with col_pref2:
    st.subheader("🛏 Habitación")
    room_type = st.selectbox("Tipo de habitación*", 
                           ['Individual', 'Doble', 'Twin', 'Suite', 'Familiar', 'Presidencial'])
    total_guests = st.number_input("Número de huéspedes*", 1, 10, 2)
    required_car_parking = st.checkbox("Requiere estacionamiento")

# Sección 4: Método de Pago
st.header("💳 Información de Pago")

col_pago1, col_pago2 = st.columns(2)

with col_pago1:
    payment_method = st.selectbox("Método de pago*", 
                                ['Tarjeta Crédito', 'Tarjeta Débito', 'Transferencia', 'Efectivo'])
    
with col_pago2:
    if payment_method in ['Tarjeta Crédito', 'Tarjeta Débito']:
        card_number = st.text_input("Número de tarjeta*", max_chars=16)
        expiry_date = st.text_input("Fecha expiración (MM/YY)*", max_chars=5)

# Convertir datos para el modelo
meal_plan_2 = int(meal_plan == 'Desayuno incluido')
meal_plan_3 = int(meal_plan == 'Cena incluida')
meal_not_selected = int(meal_plan == 'Cena incluida')
rt2 = int(room_type == 'Individual')
rt3 = int(room_type == 'Doble')
rt4 = int(room_type == 'Twin')
rt6 = int(room_type == 'Suite')
rt7 = int(room_type == 'Familiar')

input_data = np.array([[
    int(required_car_parking), lead_time, arrival_year, arrival_month, arrival_date,
    0, 0, 0,  # Datos de historial no solicitados
    len(special_requests.split(',') if special_requests else []),  # Número de solicitudes especiales
    meal_plan_2, meal_plan_3, meal_not_selected,
    rt2, rt3, rt4, 0, rt6, rt7,  # Tipos de habitación
    0, 0, 0, 0,  # Segmento de mercado
    1,  # Reserva confirmada
    total_guests, total_nights
]])

# Botón de procesamiento
if st.button("💳 Confirmar Reserva y Calcular Precio", type="primary"):
    # Validar campos obligatorios
    mandatory_fields = {
        "Nombre": nombre,
        "Email": email,
        "Teléfono": telefono,
        "Documento": documento,
        "Fechas": fecha_llegada and fecha_salida,
        "Método de pago": payment_method
    }
    
    missing_fields = [field for field, value in mandatory_fields.items() if not value]
    
    if missing_fields:
        st.error(f"❌ Faltan campos obligatorios: {', '.join(missing_fields)}")
    else:
        # Realizar predicción
        input_scaled = scaler.transform(input_data)
        predicted_price = modelo.predict(input_scaled)[0]
        total_price = predicted_price * total_nights
        
        # Mostrar resultados
        st.success(f"**Precio por noche:** ${predicted_price:.2f}")
        st.success(f"**Total a pagar ({total_nights} noches):** ${total_price:.2f}")
        
        # Preparar datos para guardar
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
            "precio_noche": round(predicted_price, 2),
            "precio_total": round(total_price, 2),
            "lead_time": lead_time,
            "temporada": 'Alta' if arrival_month in [6,7,8,12] else 'Media' if arrival_month in [4,5,9,10,11] else 'Baja'
        }
        
        # Guardar en CSV
        save_to_csv(reservation_data)
        st.balloons()
        st.success("✅ Reserva registrada correctamente")
        
        # Mostrar resumen
        st.subheader("📝 Recibo de Reserva")
        st.json({k: v for k, v in reservation_data.items() if k not in ['timestamp']})
        
        # Opción para descargar
        df_reserva = pd.DataFrame([reservation_data])
        csv = df_reserva.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Descargar comprobante",
            data=csv,
            file_name=f"reserva_{documento}_{fecha_llegada.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Mostrar historial si existe
if os.path.exists(DATA_FILE):
    st.sidebar.header("📊 Historial de Reservas")
    historico = pd.read_csv(DATA_FILE)
    st.sidebar.dataframe(historico.tail(5))
    st.sidebar.download_button(
        "Descargar historial completo",
        historico.to_csv(index=False).encode('utf-8'),
        "historial_reservas.csv",
        "text/csv"
    )



