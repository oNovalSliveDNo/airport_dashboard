# components/complaints_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.preprocessing import load_complaints


class ComplaintsDashboard:
    def __init__(self):
        pass

    def load_data(self):
        pass


    def run(self):
        st.title("🗣️ Жалобы")
        self.load_data()
        pass
