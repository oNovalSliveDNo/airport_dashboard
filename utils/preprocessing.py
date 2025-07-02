# utils/preprocessing.py
import pandas as pd

def load_passenger_data():
    df = pd.read_csv("data/transformed.csv", parse_dates=["date"])
    return df

def load_temperature_data():
    return pd.read_excel("data/Средняя_температура_в_помещениях_Аэровокзала Приведенная.xlsx")

def load_co2_data():
    return pd.read_excel("data/Средняя_CO2_в_помещениях_Аэровокзала Приведенная.xlsx")

def load_complaints():
    return pd.read_csv("data/Жалобы пассажиров.csv")
