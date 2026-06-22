# -*- coding: utf-8 -*-
"""Shared utility functions for Optimus Price Streamlit apps"""

import numpy as np
from datetime import date, datetime


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
        int(required_car_parking), lead_time, arrival_year, arrival_month,
        arrival_date, int(repeated_guest), no_prev_cancel, no_prev_bookings,
        special_requests_count, meal_plan_2, meal_not_selected,
        rt2, rt3, rt4, rt5, rt6, rt7,
        ms_compl, ms_corp, ms_off, ms_onl, booking_not_canceled,
        total_guests, total_nights, arrival_day_of_week, arrival_week_number
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
    data_mod = np.array([[
        int(required_car_parking_mod), lead_time_mod, arrival_year_mod,
        mes_mod, arrival_date_mod, 0, 0, 0, special_requests_mod,
        m_plan2, m_not_selected, rt2_mod, rt3_mod, rt4_mod, rt5_mod, rt6_mod, rt7_mod,
        0, 0, 0, 0, 1, total_guests_mod, total_nights_mod,
        arrival_day_of_week_mod, arrival_week_number_mod
    ]])
    return data_mod
