import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Hotel Price Predictor", layout="wide")

# Cargar el modelo y el scaler
modelo = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\trained_model_1.pkl')
scaler = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\scaler_trained_model_1.pkl')

# Título e imagen
st.title("🏨 Hotel Price Predictor")
st.image("https://images.unsplash.com/photo-1501117716987-c8e2a01d1a17?auto=format&fit=crop&w=1200&q=80", caption="Tu próximo destino", use_container_width=True)

st.markdown("### Ingresa los detalles de la reserva:")

# Organizar los inputs en columnas para una mejor UX
col1, col2, col3 = st.columns(3)

with col1:
    required_car_parking_space = st.selectbox('🚗 ¿Necesita estacionamiento?', ['No', 'Sí']) == 'Sí'
    repeated_guest = st.selectbox('🔁 ¿Es cliente recurrente?', ['No', 'Sí']) == 'Sí'
    lead_time = st.slider('⏱ Tiempo de anticipación (días)', 0, 400, 100)
    arrival_date = st.slider('📅 Día de llegada', 1, 31, 15)
    arrival_month = st.slider('📆 Mes de llegada', 1, 12, 5)
    arrival_year = st.selectbox('🗓 Año de llegada', [2025, 2026, 2027])

with col2:
    no_of_previous_cancellations = st.number_input('❌ Cancelaciones previas', 0, 20, 0)
    no_of_previous_bookings_not_canceled = st.number_input('✅ Reservas previas exitosas', 0, 50, 0)
    no_of_special_requests = st.number_input('⭐ Solicitudes especiales', 0, 5, 0)
    total_guests = st.number_input('👥 Total de huéspedes', 1, 10, 2)
    total_nights = st.number_input('🌙 Total de noches', 1, 30, 2)

with col3:
    st.markdown("#### 🍽 Plan de comida")
    meal_2 = st.checkbox('Meal Plan 2')
    meal_not_selected = st.checkbox('Not Selected')

    st.markdown("#### 🛏 Tipo de habitación")
    rt2 = st.checkbox('Single')
    rt3 = st.checkbox('Double')
    rt4 = st.checkbox('Twin')
    rt5 = st.checkbox('Triple')
    rt6 = st.checkbox('Suite')
    rt7 = st.checkbox('Family')

    st.markdown("#### 🧭 Segmento de mercado")
    ms_compl = st.checkbox('Complementary')
    ms_corp = st.checkbox('Corporate')
    ms_off = st.checkbox('Offline')
    ms_onl = st.checkbox('Online')

    st.markdown("#### 📌 Estado de la reserva")
    booking_ok = st.checkbox('Not Canceled')

# Recolectar datos
input_data = np.array([[

    int(required_car_parking_space),
    lead_time,
    arrival_year,
    arrival_month,
    arrival_date,
    int(repeated_guest),
    no_of_previous_cancellations,
    no_of_previous_bookings_not_canceled,
    no_of_special_requests,
    int(meal_2),
    int(meal_not_selected),
    int(rt2), int(rt3), int(rt4), int(rt5), int(rt6), int(rt7),
    int(ms_compl), int(ms_corp), int(ms_off), int(ms_onl),
    int(booking_ok),
    total_guests,
    total_nights

]])

# Botón de predicción
if st.button("🔮 Predecir precio"):
    input_scaled = scaler.transform(input_data)
    prediccion = modelo.predict(input_scaled)

    st.success(f"💰 El precio estimado de la habitación es: **${prediccion[0]:.2f}**")

    # Mostrar gráfico
    fig, ax = plt.subplots()
    ax.bar(["Precio estimado"], [prediccion[0]], color="skyblue")
    ax.set_ylabel("Precio en USD")
    st.pyplot(fig)

    # Descargar como CSV
    df = pd.DataFrame({
        'Precio estimado': [prediccion[0]]
    })
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Descargar Tarifa CSV", data=csv, file_name="prediccion.csv", mime="text/csv")

    # Celebración
    st.balloons()

