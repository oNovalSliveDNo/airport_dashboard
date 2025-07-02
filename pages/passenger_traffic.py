# pages/passenger_traffic.py
import streamlit as st
import pandas as pd
from utils.preprocessing import load_passenger_data

st.title("📊 Пассажиропоток")

df = load_passenger_data()

# Пример простого графика
st.line_chart(df.set_index("date")["Total_Passengers"])

# TODO: Добавить фильтры, группировки по дням/месяцам/годам
