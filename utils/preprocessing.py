# utils/preprocessing.py
import pandas as pd


def load_passenger_data():
    passenger_df = pd.read_csv("data/transformed.csv", parse_dates=["Date"])
    print("Датасет 'data/transformed.csv' загружен!")
    return passenger_df


def load_temperature_data():
    temperature_df = pd.read_excel("data/Средняя_температура_в_помещениях_Аэровокзала Приведенная.csv")
    print("Датасет 'data/Средняя_температура_в_помещениях_Аэровокзала Приведенная.csv' загружен!")
    return temperature_df


def load_co2_data():
    co2_df = pd.read_excel("data/Средняя_CO2_в_помещениях_Аэровокзала Приведенная.csv")
    print("Датасет 'data/Средняя_CO2_в_помещениях_Аэровокзала Приведенная.csv' загружен!")
    return co2_df


def load_complaints():
    complaints_df = pd.read_csv("data/Жалобы пассажиров.csv")
    print("Датасет 'data/Жалобы пассажиров.csv' загружен!")
    return complaints_df
