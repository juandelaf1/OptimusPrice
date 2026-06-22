import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Hotel Price Predictor", layout="centered")

# Cargar el modelo y el scaler
modelo = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\trained_model_1.pkl')
scaler = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\scaler_trained_model_1.pkl')

# Título e imagen
st.image("https://media.istockphoto.com/id/1028630524/es/foto/servicio-de-portero-en-recepci%C3%B3n-del-hotel.jpg?s=612x612&w=0&k=20&c=vmAibFhevHSeOlyrj0nzoZtAt-zCYtFmZd0cPqEIYQI=",
         caption= None, use_container_width=True)
st.title("🏨 Predicción de Precio de Hotel")

st.markdown("##### Rellena los detalles de tu reserva para estimar el precio:")

# Fecha de llegada con datetime
fecha_llegada = st.date_input("📅 Fecha de llegada", min_value=datetime(2025, 1, 1), max_value=datetime(2027, 12, 31))
arrival_year = fecha_llegada.year
arrival_month = fecha_llegada.month
arrival_date = fecha_llegada.day

# Dividir en columnas
col1, col2 = st.columns(2)

with col1:
    required_car_parking_space = st.toggle('🚗 ¿Necesita estacionamiento?')
    repeated_guest = st.toggle('🔁 ¿Es cliente recurrente?')
    lead_time = st.slider('⏱ Tiempo de anticipación (días)', 0, 400, 100)
    no_of_previous_cancellations = st.number_input('❌ Cancelaciones previas', 0, 20, 0)
    no_of_previous_bookings_not_canceled = st.number_input('✅ Reservas exitosas anteriores', 0, 50, 0)
    no_of_special_requests = st.number_input('⭐ Solicitudes especiales', 0, 5, 0)
    total_guests = st.number_input('👥 Total de huéspedes', 1, 10, 2)
    total_nights = st.number_input('🌙 Total de noches', 1, 30, 2)

with col2:
    st.subheader("🍽 Plan de comida")
    meal_2 = st.radio("Selecciona uno:", ['Ninguno', 'Desayuno incluido', 'Cena incluida'])
    meal_plan_2 = int(meal_2 == 'Desayuno incluido')
    meal_not_selected = int(meal_2 == 'Cena incluida')

    st.subheader("🛏 Tipo de habitación")
    room_type = st.radio("Selecciona uno:", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
    rt2 = int(room_type == 'Individual')
    rt3 = int(room_type == 'Doble')
    rt4 = int(room_type == 'Twin')
    rt5 = int(room_type == 'Triple')
    rt6 = int(room_type == 'Suite')
    rt7 = int(room_type == 'Familiar')

    st.subheader("🧭 Segmento de mercado")
    market = st.radio("Selecciona uno:", ['Predeterminado', 'Complementario', 'Corporativo', 'Offline', 'Online'])
    ms_compl = int(market == 'Complementario')
    ms_corp = int(market == 'Corporativo')
    ms_off = int(market == 'Offline')
    ms_onl = int(market == 'Online')

    booking_ok = st.toggle('📌 ¿Reserva no cancelada?')

# Datos de entrada
input_data = np.array([[
    int(required_car_parking_space), lead_time, arrival_year, arrival_month, arrival_date,
    int(repeated_guest), no_of_previous_cancellations, no_of_previous_bookings_not_canceled,
    no_of_special_requests, meal_plan_2, meal_not_selected,
    rt2, rt3, rt4, rt5, rt6, rt7,
    ms_compl, ms_corp, ms_off, ms_onl,
    int(booking_ok), total_guests, total_nights
]])

# Botón de predicción
if st.button("🔮 Predecir precio"):
    input_scaled = scaler.transform(input_data)
    prediccion = modelo.predict(input_scaled)


 
    st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(45deg, #0077b6, #00b4d8); 
                    border-radius: 12px; text-align: center; font-size: 26px; color: white; 
                    font-weight: bold; box-shadow: 4px 4px 12px rgba(0,0,0,0.3);">
            🏨 <strong>Precio estimado de la habitación</strong> 🏨 <br>
            <span style="font-size: 36px;">💰 ${prediccion[0]:.2f} USD</span> <br>
            <em style="font-size: 18px;">Reserva ahora y disfruta de tu estancia</em>
        </div>
    """, unsafe_allow_html=True)

    # Descargar CSV
    df = pd.DataFrame({
        'Precio estimado': [prediccion[0]]
    })
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Descargar CSV", data=csv, file_name="prediccion.csv", mime="text/csv")

    # Celebración
    st.balloons()
