# components/environment_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import load_temperature_data
from utils.preprocessing import load_co2_data


class EnvironmentDashboard:
    def __init__(self):
        self.df_temp = None
        self.df_co2 = None

    def load_data(self):
        self.df_temp = load_temperature_data()
        self.df_co2 = load_co2_data()

    def render_temperature_chart(self):
        # TODO: График температуры
        pass

    def render_co2_chart(self):
        # TODO: График CO2
        pass

    def run(self):
        st.title("🌡️ Температура и CO₂")
        self.load_data()
        self.render_temperature_chart()
        self.render_co2_chart()
