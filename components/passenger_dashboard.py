# components/passenger_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.preprocessing import load_passenger_data  # реализуй эту функцию для чтения transformed.csv
from statsmodels.tsa.seasonal import seasonal_decompose


class PassengerDashboard:
    def __init__(self):
        self.df = load_passenger_data()
        self.filtered_df = self.df.copy()

    def render_sidebar_filters(self):
        st.sidebar.header("🔎 Фильтры")

        self.years = st.sidebar.multiselect("Год", sorted(self.df["Year"].unique()),
                                            default=sorted(self.df["Year"].unique()))
        # self.quarters = st.sidebar.multiselect("Квартал", ["Q1", "Q2", "Q3", "Q4"], default=["Q1", "Q2", "Q3", "Q4"])
        # self.seasons = st.sidebar.multiselect("Сезон", ["Зима", "Весна", "Лето", "Осень"],
        #                                       default=["Зима", "Весна", "Лето", "Осень"])

        self.months = st.sidebar.multiselect("Месяц", sorted(self.df["Month"].unique()),
                                             default=sorted(self.df["Month"].unique()))
        self.weekdays = st.sidebar.multiselect("День недели", sorted(self.df["DayOfWeek"].unique()),
                                               default=sorted(self.df["DayOfWeek"].unique()))
        self.times_of_day = st.sidebar.multiselect("Время суток", self.df["TimeOfDay"].unique(),
                                                   default=self.df["TimeOfDay"].unique())
        self.airlines = st.sidebar.multiselect("Авиакомпания", sorted(self.df["Airline_name"].unique()), default=None)
        self.dep_arr = st.sidebar.multiselect("Вылет / Прилет", self.df["Departure_Arrival"].unique(),
                                              default=self.df["Departure_Arrival"].unique())
        # Аэропорт назначения / вылета
        # self.airports = st.sidebar.multiselect("Аэропорт назначения/вылета", sorted(self.df["Airport"].unique()),
        #                                        default=None)
        self.reg_type = st.sidebar.multiselect("Тип рейса", self.df["Reg_type"].unique(),
                                               default=self.df["Reg_type"].unique())
        self.reg_sr_type = st.sidebar.multiselect("Регулярность", self.df["Reg_sr_type"].unique(),
                                                  default=self.df["Reg_sr_type"].unique())
        self.cancelled = st.sidebar.multiselect("Отменён", [True, False], default=[True, False])
        self.delay_cat = st.sidebar.multiselect("Категория задержки", self.df["DelayCategory"].unique(),
                                                default=self.df["DelayCategory"].unique())

        self.filtered_df = self.df[
            (self.df["Year"].isin(self.years)) &
            (self.df["Month"].isin(self.months)) &
            (self.df["DayOfWeek"].isin(self.weekdays)) &
            (self.df["TimeOfDay"].isin(self.times_of_day)) &
            (self.df["Departure_Arrival"].isin(self.dep_arr)) &
            (self.df["Reg_type"].isin(self.reg_type)) &
            (self.df["Reg_sr_type"].isin(self.reg_sr_type)) &
            (self.df["IsCancelled"].isin(self.cancelled)) &
            (self.df["DelayCategory"].isin(self.delay_cat))
            ]

        # Фильтрация по кварталу
        # if self.quarters:
        #     self.filtered_df = self.filtered_df[self.filtered_df['Quarter'].isin(self.quarters)]

        # Фильтрация по сезону
        # if self.seasons:
        #     self.filtered_df = self.filtered_df[self.filtered_df['Season'].isin(self.seasons)]

        # Фильтрация по аэропорту
        # if self.airports:
        #     self.filtered_df = self.filtered_df[self.filtered_df["Airport"].isin(self.airports)]

        # Фильтрация по авиакомпании
        if self.airlines:
            self.filtered_df = self.filtered_df[self.filtered_df["Airline_name"].isin(self.airlines)]

    def render_main_metrics(self):
        st.subheader("📌 Основные показатели")

        total_passengers = self.filtered_df["Total_Passengers"].sum()
        avg_load = self.filtered_df["Total_Passengers"].mean()
        total_cancellations = self.filtered_df["IsCancelled"].sum()
        avg_delay = self.filtered_df["DelayTime"].mean()
        top_airline = self.filtered_df.groupby("Airline_name")["Total_Passengers"].sum().idxmax()
        top_day = self.filtered_df.groupby("Date")["Total_Passengers"].sum().idxmax()

        # Обработка случая, если данных нет
        if not self.filtered_df.empty and "Airline_name" in self.filtered_df.columns:
            top_airline = self.filtered_df.groupby("Airline_name")["Total_Passengers"].sum().idxmax()
        else:
            top_airline = "—"

        if not self.filtered_df.empty and "Date" in self.filtered_df.columns:
            top_day = self.filtered_df.groupby("Date")["Total_Passengers"].sum().idxmax()
            top_day_str = top_day.strftime("%d.%m.%Y")
        else:
            top_day_str = "—"

        col1, col2, col3 = st.columns(3)
        col1.metric("🎫 Общий пассажиропоток", f"{total_passengers:,}")
        col2.metric("🧍‍♂️ Средняя загрузка борта", f"{avg_load:.0f} чел")
        col3.metric("❌ Кол-во отмен", f"{int(total_cancellations):,}")

        col4, col5, col6 = st.columns(3)
        col4.metric("⏱ Средняя задержка", f"{avg_delay:.1f} мин")
        col5.metric("🏆 Топ авиакомпания", top_airline)
        col6.metric("📈 Пиковый день", top_day.strftime("%d.%m.%Y"))

    def render_by_time(self):
        st.subheader("📅 Пассажиропоток во времени")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📈 Динамика по времени (drill-down)",
             "📊 По дням недели",
             "⏰ По времени суток",
             "🔥 Тепловая карта",
             "📅 Сравнение по месяцам"])

        # Drilldown: Год → Месяц → Неделя → День
        with tab1:
            level = st.selectbox("Уровень детализации", ["Год", "Месяц", "Неделя", "День"])

            if level == "Год":
                df_time = self.filtered_df.groupby("Year")["Total_Passengers"].sum().reset_index()
                fig = px.bar(df_time, x="Year", y="Total_Passengers", title="Пассажиропоток по годам")

            elif level == "Месяц":
                df_time = self.filtered_df.groupby("YearMonth")["Total_Passengers"].sum().reset_index()
                fig = px.line(df_time, x="YearMonth", y="Total_Passengers", title="По месяцам", markers=True)

            elif level == "Неделя":
                self.filtered_df["Week"] = self.filtered_df["Date"].dt.isocalendar().week
                df_time = self.filtered_df.groupby(["Year", "Week"])["Total_Passengers"].sum().reset_index()
                df_time["YearWeek"] = df_time["Year"].astype(str) + "-W" + df_time["Week"].astype(str)
                fig = px.line(df_time, x="YearWeek", y="Total_Passengers", title="По неделям", markers=True)

            elif level == "День":
                df_time = self.filtered_df.groupby("Date")["Total_Passengers"].sum().reset_index()
                fig = px.line(df_time, x="Date", y="Total_Passengers", title="По дням", markers=True)

            st.plotly_chart(fig, use_container_width=True)

        # Bar chart по дням недели
        with tab2:
            df_weekday = self.filtered_df.groupby("DayOfWeek")["Total_Passengers"].mean().reset_index()
            fig = px.bar(df_weekday, x="DayOfWeek", y="Total_Passengers", title="Средний пассажиропоток по дням недели")
            st.plotly_chart(fig, use_container_width=True)

        # Boxplot пассажиропотока по времени суток
        with tab3:
            # Удаление экстремальных выбросов
            q1 = self.filtered_df["Total_Passengers"].quantile(0.25)
            q3 = self.filtered_df["Total_Passengers"].quantile(0.75)
            iqr = q3 - q1
            filtered_no_outliers = self.filtered_df[
                (self.filtered_df["Total_Passengers"] >= q1 - 1.5 * iqr) &
                (self.filtered_df["Total_Passengers"] <= q3 + 1.5 * iqr)
                ]

            fig = px.box(filtered_no_outliers,
                         x="TimeOfDay",
                         y="Total_Passengers",
                         title="Распределение по времени суток (без выбросов)")
            st.plotly_chart(fig, use_container_width=True)

        # Тепловая карта: день недели vs час
        with tab4:
            heat_df = self.filtered_df.groupby(["DayOfWeek", "Hour"])["Total_Passengers"].mean().reset_index()
            heatmap_data = heat_df.pivot(index="DayOfWeek", columns="Hour", values="Total_Passengers")
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale="YlGnBu"
            ))
            fig.update_layout(title="Тепловая карта: день недели vs час")
            st.plotly_chart(fig, use_container_width=True)

        # Линейный график пассажиропотока по месяцам с наложением по годам
        with tab5:
            df_month_year = self.filtered_df.groupby(["Year", "Month"])["Total_Passengers"].sum().reset_index()
            fig = px.line(df_month_year, x="Month", y="Total_Passengers", color="Year",
                          title="Пассажиропоток по месяцам (по годам наложением)",
                          labels={"Total_Passengers": "Пассажиропоток", "Month": "Месяц"})
            st.plotly_chart(fig, use_container_width=True)

    def render_delay_relation(self):
        st.subheader("🔗 Связь с задержками и отменами")

        # Вычисляем статистики для каждого значения пассажиропотока
        df_stats = self.filtered_df.groupby("Total_Passengers")["DelayTime"].agg(
            mean_delay="mean",
            median_delay="median",
            # max_delay="max"
        ).reset_index()

        # Построение одного графика с тремя линиями для каждой статистики
        fig = px.line(df_stats,
                      x="Total_Passengers",
                      y=["mean_delay",
                         "median_delay",
                         # "max_delay"
                         ],
                      title="Зависимость задержки от пассажиропотока",
                      labels={"mean_delay": "Средняя задержка",
                              "median_delay": "Медианная задержка",
                              # "max_delay": "Максимальная задержка"
                              })

        st.plotly_chart(fig, use_container_width=True)

    def render_airline_comparison(self):
        st.subheader("✈️ Сравнение авиакомпаний")

        df_airlines = self.filtered_df.groupby("Airline_name")["Total_Passengers"].sum().reset_index().sort_values(
            by="Total_Passengers", ascending=False).head(10)
        fig = px.bar(df_airlines, x="Airline_name", y="Total_Passengers",
                     title="Топ-10 авиакомпаний по пассажиропотоку")
        st.plotly_chart(fig, use_container_width=True)

        # Группировка по авиакомпаниям и подсчёт количества отменённых рейсов
        df_cancel = self.filtered_df[self.filtered_df["IsCancelled"] == 1]
        df_cancel = df_cancel.groupby("Airline_name").size().reset_index(name="Cancelled_Count")

        # Удаление авиакомпаний с нулём отмен (на всякий случай) и сортировка по убыванию
        df_cancel = df_cancel[df_cancel["Cancelled_Count"] > 0].sort_values(by="Cancelled_Count", ascending=False)

        # Построение столбчатой диаграммы с количеством отмен по авиакомпаниям
        fig2 = px.bar(df_cancel, x="Airline_name", y="Cancelled_Count",
                      title="Количество отмен по авиакомпаниям",
                      labels={"Cancelled_Count": "Количество отмен", "Airline_name": "Авиакомпания"})

        st.plotly_chart(fig2, use_container_width=True)

    def render_anomaly_detection(self):
        st.subheader("⚠️ Выявление аномалий")

        df_date = self.filtered_df.groupby("Date")["Total_Passengers"].sum().reset_index()
        df_date["rolling"] = df_date["Total_Passengers"].rolling(window=7).mean()
        df_date["diff"] = df_date["Total_Passengers"] - df_date["rolling"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_date["Date"], y=df_date["Total_Passengers"], mode='lines', name='Пассажиры'))
        fig.add_trace(go.Scatter(x=df_date["Date"], y=df_date["rolling"], mode='lines', name='7-дн среднее'))
        fig.update_layout(title="Отклонения от среднего (7 дней)")
        st.plotly_chart(fig, use_container_width=True)

    def run(self):
        self.render_sidebar_filters()
        self.render_main_metrics()
        self.render_by_time()
        self.render_delay_relation()
        self.render_airline_comparison()
        self.render_anomaly_detection()








# ## 📈 3. ГРАФИКИ ПО ВРЕМЕНИ
#
# | Визуализация | Цель |
# | -------------------------------------------------------------------- | -------------------------------------------------------------- |
# | Линейный график пассажиропотока по месяцам (по годам наложением) | Сравнить сезонность по годам |
# | Bar chart по дням недели | Найти пиковые и минимальные дни |
# | Boxplot пассажиропотока по времени суток | Выявить, в какое время суток рейсы наиболее/наименее загружены |
# | Heatmap: день недели vs час | Тепловая карта интенсивности |
# | Drilldown: Год → Месяц → Неделя → День | Анализ вплоть до конкретных дат |
#
# ---
#
# ## 📦 4. АНАЛИТИКА СВЯЗЕЙ
#
# | Анализ | Цель |
# | ---------------------------------------------------- | ---------------------------------------------------- |
# | Связь между пассажиропотоком и задержками | Показать: больше пассажиров → выше средняя задержка? |
# | Отмена рейсов по авиакомпаниям | Кто чаще отменяет? |
# | Груз + пассажиры: общая загрузка по направлениям | Пригодится для логистики |
# | График % отмен по дням | Влияет ли день недели или сезон на отмены? |
#
# ---
#
# ## 🧠 5. ВЫЯВЛЕНИЕ АНОМАЛИЙ
#
# | Подход | Идея |
# | ------------------------------------------------------------- | -------------------------------------------------------- |
# | Rolling average + отклонения | Выделить дни с резкими всплесками или провалами |
# | Дни, где пассажиропоток сильно ниже средней по дню недели | Подсказка для оптимизации расписания |
# | Сравнение выходных и будней | Сравнить поведение в субботу/воскресенье с будними днями |
#
# ---
#
# ## 🔄 6. СРАВНЕНИЕ С ПРОШЛЫМИ ГОДАМИ
#
# | График | Назначение |
# | ------------------------------------------ | ---------------------- |
# | Линии «Пассажиры 2023» vs «Пассажиры 2024» | Показать рост или спад |
# | График YoY % изменения по месяцам | Тренды в развитии |
# | Топ-10 направлений, где произошёл рост | Пригодится аналитикам |
#
# ---
#
# ## ✈️ 7. НАПРАВЛЕНИЯ И АВИАКОМПАНИИ
#
# | Визуализация | Цель |
# | ----------------------------------------------------- | ---------------------------------------- |
# | Bar chart по авиакомпаниям | Кто перевозит больше всех? |
# | Treemap по направлениям (из аэропортов) | Визуально понять, куда чаще всего летают |
# | Sunburst: Авиакомпания → Регулярность → Пассажиры | Вложенная аналитика |
#
# ---
#
# ## 📌 8. ПРОГНОЗ (модель или доп. блок)
#
# Можно построить простой прогноз пассажиропотока (например, ARIMA, Prophet или линейная регрессия) и:
#
# * Отобразить предсказание на следующий месяц
# * Отмечать, когда реальное значение вышло за доверительный интервал
#
# ---
#
# ## 🔍 9. ИНТЕРАКТИВНЫЙ SCENARIO EXPLORER (если успеешь)
#
# 🔹 Выбор сценария в st.selectbox(), например:
#
# * “Пассажиропоток в выходные vs будни”
# * “Загруженность по часам суток”
# * “Влияние авиакомпании на задержки”
# * “Анализ отмен в зимний сезон”
