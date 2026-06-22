import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimus Price Advisor", layout="centered")

page_bg_gradient = """
<style>
    .stApp {
        background: linear-gradient(to bottom, #E0E0E0, #A9A9A9); /* Degradado gris claro */
    }
</style>
"""

st.markdown(page_bg_gradient, unsafe_allow_html=True)




# Cargar el modelo y el scaler
modelo = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\Optimus_Price_proyecto_final_ML\models\trained_model_1.pkl')
scaler = joblib.load(
    r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\Optimus_Price_proyecto_final_ML\models\scaler_trained_model_1.pkl')


# Título e imagen
st.image(r"C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\Optimus_Price_proyecto_final_ML\docs\img\optimus_price_logo.jpg",
         caption=None, use_container_width=True)
st.title("🏨 Optimus Price Advisor")

st.markdown("##### Complete los datos de la reserva para analizar estrategias de precios:")

# Fecha actual y fecha de llegada
today = date.today()
fecha_llegada = st.date_input("📅 Fecha de llegada", min_value=datetime(2025, 1, 1), max_value=datetime(2027, 12, 31))

# Calcular lead time automáticamente
lead_time = (fecha_llegada - today).days
arrival_year = fecha_llegada.year
arrival_month = fecha_llegada.month
arrival_date = fecha_llegada.day

# Mostrar lead time calculado
st.info(f"🕒 Anticipación: {lead_time} días | Temporada: {'Alta' if arrival_month in [6,7,8,12] else 'Media' if arrival_month in [4,5,9,10,11] else 'Baja'}")

# Dividir en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Perfil del Cliente")
    required_car_parking_space = st.toggle('🚗 Estacionamiento', help="Espacio de parking requerido")
    repeated_guest = st.toggle('🔁 Cliente recurrente', help="¿Es un huésped frecuente?")
    no_of_previous_bookings_not_canceled = st.number_input('✅ Reservas previas cumplidas', 0, 50, 0)
    no_of_special_requests = st.number_input('⭐ Solicitudes especiales', 0, 5, 0)
    
    st.subheader("🧮 Ocupación")
    total_guests = st.number_input('👥 Huéspedes totales', 1, 10, 2)
    total_nights = st.number_input('🌙 Noches de estancia', 1, 30, 2)

with col2:
    st.subheader("🍽 Servicios")
    meal_2 = st.radio("Plan de comidas:", ['Ninguno', 'Desayuno incluido', 'Cena incluida'])
    meal_plan_2 = int(meal_2 == 'Desayuno incluido')
    meal_plan_3 = int(meal_2 == 'Cena incluida')
    meal_not_selected = int(meal_2 == 'Ninguno')

    st.subheader("🛏 Configuración")
    room_type = st.radio("Tipo de habitación:", ['Predeterminado', 'Individual', 'Doble', 'Twin', 'Triple', 'Suite', 'Familiar'])
    rt2 = int(room_type == 'Individual')
    rt3 = int(room_type == 'Doble')
    rt4 = int(room_type == 'Twin')
    rt5 = int(room_type == 'Triple')
    rt6 = int(room_type == 'Suite')
    rt7 = int(room_type == 'Familiar')

    st.subheader("📈 Canal")
    market = st.radio("Origen reserva:", ['Predeterminado', 'Complementario', 'Corporativo', 'Offline', 'Online'])
    ms_compl = int(market == 'Complementario')
    ms_corp = int(market == 'Corporativo')
    ms_off = int(market == 'Offline')
    ms_onl = int(market == 'Online')

# Datos ocultos
no_of_previous_cancellations = 0
booking_ok = True

# Datos de entrada
input_data = np.array([[
    int(required_car_parking_space), lead_time, arrival_year, arrival_month, arrival_date,
    int(repeated_guest), no_of_previous_cancellations, no_of_previous_bookings_not_canceled,
    no_of_special_requests, meal_plan_2, meal_plan_3, meal_not_selected,
    rt2, rt3, rt4, rt5, rt6, rt7,
    ms_compl, ms_corp, ms_off, ms_onl,
    int(booking_ok), total_guests, total_nights
]])

# PREDICCIÓN BASE
input_scaled = scaler.transform(input_data)
prediccion_base = modelo.predict(input_scaled)[0]

# Sección de ajuste de precios
st.markdown("---")
st.subheader("💰 Estrategia de Precios")

base_col, adj_col = st.columns(2)
with base_col:
    st.markdown(f"**Precio base recomendado:** ${prediccion_base:.2f} USD")
    st.markdown(f"**Ingreso total estimado:** ${prediccion_base * total_nights:.2f} USD")

with adj_col:
    adjustment = st.slider("Ajuste de precio (%)", -20, 30, 0, 5,
                          help="Ajuste porcentual sobre el precio base recomendado")
    precio_ajustado = prediccion_base * (1 + adjustment/100)
    st.markdown(f"**Precio ajustado:** ${precio_ajustado:.2f} USD")
    st.markdown(f"**Nuevo ingreso estimado:** ${precio_ajustado * total_nights:.2f} USD")

# Análisis de sensibilidad
st.markdown("---")
st.subheader("📊 Análisis de Sensibilidad")

tab1, tab2, tab3 = st.tabs(["Por anticipación", "Por ocupación", "Por temporada"])

with tab1:
    st.markdown("**Impacto del tiempo de anticipación en el precio**")
    fig1, ax1 = plt.subplots()
    lead_times = np.linspace(0, 400, 20)
    prices = []
    
    for lt in lead_times:
        input_data[0, 1] = lt
        input_scaled = scaler.transform(input_data)
        prices.append(modelo.predict(input_scaled)[0])
    
    ax1.plot(lead_times, prices)
    ax1.scatter(lead_time, prediccion_base, color='red', s=100)
    ax1.set_xlabel('Días de anticipación')
    ax1.set_ylabel('Precio recomendado (USD)')
    st.pyplot(fig1)

with tab2:
    st.markdown("**Impacto del número de huéspedes en el precio**")
    fig2, ax2 = plt.subplots()
    guests_range = range(1, 11)
    prices = []
    
    for guests in guests_range:
        input_data[0, 22] = guests
        input_scaled = scaler.transform(input_data)
        prices.append(modelo.predict(input_scaled)[0])
    
    ax2.plot(guests_range, prices)
    ax2.scatter(total_guests, prediccion_base, color='red', s=100)
    ax2.set_xlabel('Número de huéspedes')
    ax2.set_ylabel('Precio recomendado (USD)')
    st.pyplot(fig2)

with tab3:
    st.markdown("**Variación de precios por mes**")
    fig3, ax3 = plt.subplots()
    months = range(1, 13)
    month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    prices = []
    
    for month in months:
        input_data[0, 3] = month
        input_scaled = scaler.transform(input_data)
        prices.append(modelo.predict(input_scaled)[0])
    
    ax3.plot(month_names, prices)
    ax3.scatter(month_names[arrival_month-1], prediccion_base, color='red', s=100)
    ax3.set_xlabel('Mes')
    ax2.set_ylabel('Precio recomendado (USD)')
    st.pyplot(fig3)

# Descargar reporte
st.markdown("---")
report_data = {
    'Fecha llegada': [fecha_llegada.strftime("%Y-%m-%d")],
    'Lead time': [lead_time],
    'Temporada': ['Alta' if arrival_month in [6,7,8,12] else 'Media' if arrival_month in [4,5,9,10,11] else 'Baja'],
    'Tipo habitación': [room_type],
    'Plan comidas': [meal_2],
    'Huéspedes': [total_guests],
    'Noches': [total_nights],
    'Precio base': [prediccion_base],
    'Ajuste (%)': [adjustment],
    'Precio final': [precio_ajustado],
    'Ingreso total': [precio_ajustado * total_nights]
}

df_report = pd.DataFrame(report_data)
csv = df_report.to_csv(index=False).encode('utf-8')

st.download_button("📄 Descargar reporte completo", data=csv,
                  file_name=f"estrategia_precios_{fecha_llegada.strftime('%Y%m%d')}.csv",
                  mime="text/csv")


