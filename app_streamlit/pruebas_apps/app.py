import streamlit as st
import joblib
import numpy as np


# Cargar el modelo
modelo = joblib.load(r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\trained_model_1.pkl')
scaler = joblib.load(r'C:\Users\JUAN\Desktop\BOOTCAMP - DATA SCIENCE\Ejercicios Juan\HotelPricePredictor_proyecto_final_ML\models\scaler_trained_model_1.pkl')
# Título
st.title("HotelPricePredictor")

# Entradas del usuario
# Ya tienes:
lead_time = st.slider('Tiempo de anticipación', 0, 400, 100)
arrival_year = st.selectbox('Año de llegada', [2025, 2026, 2027])
arrival_month = st.slider('Mes de llegada', 1, 12, 5)

# Faltantes:
arrival_date = st.slider('Día de llegada', 1, 31, 15)
required_car_parking_space = st.selectbox('¿Requiere espacio para estacionar?', [0, 1])
repeated_guest = st.selectbox('¿Es cliente recurrente?', [0, 1])
no_of_previous_cancellations = st.number_input('N° de cancelaciones previas', 0, 20, 0)
no_of_previous_bookings_not_canceled = st.number_input('N° de reservas previas no canceladas', 0, 50, 0)
no_of_special_requests = st.number_input('N° de solicitudes especiales', 0, 5, 0)
total_guests = st.number_input('Total de huéspedes', 1, 10, 2)
total_nights = st.number_input('Total de noches', 1, 30, 2)

# Variables booleanas tipo one-hot (convertidas desde variables categóricas)
type_of_meal_plan_Meal_Plan_2 = st.checkbox('Plan de comida: Meal Plan 2')
type_of_meal_plan_Not_Selected = st.checkbox('Plan de comida: Not Selected')

room_type_reserved_Room_Type_2 = st.checkbox('Tipo de habitación: Room Type 2')
room_type_reserved_Room_Type_3 = st.checkbox('Tipo de habitación: Room Type 3')
room_type_reserved_Room_Type_4 = st.checkbox('Tipo de habitación: Room Type 4')
room_type_reserved_Room_Type_5 = st.checkbox('Tipo de habitación: Room Type 5')
room_type_reserved_Room_Type_6 = st.checkbox('Tipo de habitación: Room Type 6')
room_type_reserved_Room_Type_7 = st.checkbox('Tipo de habitación: Room Type 7')

market_segment_type_Complementary = st.checkbox('Segmento: Complementary')
market_segment_type_Corporate = st.checkbox('Segmento: Corporate')
market_segment_type_Offline = st.checkbox('Segmento: Offline')
market_segment_type_Online = st.checkbox('Segmento: Online')

booking_status_Not_Canceled = st.checkbox('Estado: Not Canceled')

# Agrega más características aquí si tu modelo las necesita

# Botón para hacer la predicción
if st.button("Predecir"):
    # Crear array en el orden correcto (24 variables)
    input_data = np.array([[
        required_car_parking_space,
        lead_time,
        arrival_year,
        arrival_month,
        arrival_date,
        repeated_guest,
        no_of_previous_cancellations,
        no_of_previous_bookings_not_canceled,
        no_of_special_requests,
        type_of_meal_plan_Meal_Plan_2,
        type_of_meal_plan_Not_Selected,
        room_type_reserved_Room_Type_2,
        room_type_reserved_Room_Type_3,
        room_type_reserved_Room_Type_4,
        room_type_reserved_Room_Type_5,
        room_type_reserved_Room_Type_6,
        room_type_reserved_Room_Type_7,
        market_segment_type_Complementary,
        market_segment_type_Corporate,
        market_segment_type_Offline,
        market_segment_type_Online,
        booking_status_Not_Canceled,
        total_guests,
        total_nights
    ]])

    # Escalar
    input_scaled = scaler.transform(input_data)

    # Predicción
    prediccion = modelo.predict(input_scaled)

    # Mostrar resultado
    st.success(f"el precio de la habitacion es : {prediccion[0]}")

