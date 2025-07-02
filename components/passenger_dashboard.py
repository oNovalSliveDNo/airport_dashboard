# components/passenger_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import load_passenger_data


class PassengerTrafficDashboard:
    def __init__(self):
        self.df = None
        self.filtered_df = None
        self.date_range = None

    def load_data(self):
        self.df = load_passenger_data()
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values('Date')

    def render_filters(self):
        st.sidebar.header("Фильтры")

        # Дата
        min_date, max_date = self.df['Date'].min(), self.df['Date'].max()
        self.date_range = st.sidebar.date_input("Диапазон дат", [min_date, max_date])

        # Применение фильтра
        start_date, end_date = self.date_range
        self.filtered_df = self.df[(self.df['Date'] >= pd.to_datetime(start_date)) &
                                   (self.df['Date'] <= pd.to_datetime(end_date))]

    def render_summary(self):
        st.subheader("📈 Сводка")
        total = self.filtered_df['Total_Passengers'].sum()
        st.metric("Всего пассажиров", f"{int(total):,}".replace(",", " "))

    def render_charts(self):
        st.subheader("📊 График пассажиропотока")

        fig = px.line(
            self.filtered_df,
            x='Date',
            y='Total_Passengers',
            title="Пассажиропоток по дате",
            labels={"Total_Passengers": "Пассажиры", "Date": "Дата"}
        )
        st.plotly_chart(fig, use_container_width=True)

    def run(self):
        st.title("📊 Пассажиропоток")
        self.load_data()
        self.render_filters()
        self.render_summary()
        self.render_charts()
