# pages/1_📊_Пассажиропоток.py.py

import streamlit as st
from components.passenger_dashboard import PassengerDashboard


def main():
    st.set_page_config(page_title="📊 Пассажиропоток", layout="wide")

    st.title("📊 Анализ пассажиропотока")
    st.markdown("Интерактивный анализ на основе рейсовых данных")

    dashboard = PassengerDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
