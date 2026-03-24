import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from analysis import (
    load_data,
    get_city_data,
    get_basic_stats,
    add_rolling_stats,
    detect_anomalies,
    compute_seasonal_stats
)
from weather_api import (
    get_current_temperature,
    get_current_season,
    check_temperature_anomaly
)

st.title("Анализ температурных данных")

DEFAULT_DATA_PATH = "data/temperature_data.csv"

st.header("Шаг 1: Загрузка данных")
uploaded_file = st.file_uploader("Выберите CSV-файл (или используйте данные по умолчанию)", type=["csv"])

if uploaded_file is not None:
    data = load_data(uploaded_file)
else:
    data = load_data(DEFAULT_DATA_PATH)
    st.info("Используются данные по умолчанию (data/temperature_data.csv)")

cities = data["city"].unique().tolist()

st.write("Превью данных:")
st.dataframe(data.head())

st.header("Шаг 2: Выбор города")
city = st.selectbox("Выберите город", cities)

city_df = get_city_data(data, city)
city_df = add_rolling_stats(city_df)
city_df = detect_anomalies(city_df)
seasonal_stats = compute_seasonal_stats(city_df)

st.header("Шаг 3: Статистика города")
if st.checkbox("Показать статистику города"):
    stats = get_basic_stats(city_df)
    st.dataframe(stats)

st.header("Шаг 4: Временной график температур")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    city_df["timestamp"],
    city_df["temperature"],
    label="Температура",
    color="blue",
    linewidth=0.5
)

ax.plot(
    city_df["timestamp"],
    city_df["rolling_mean"],
    label="Скользящее среднее (30 дней)",
    color="orange",
    linewidth=2
)

anomalies = city_df[city_df["is_anomaly"]]
ax.scatter(
    anomalies["timestamp"],
    anomalies["temperature"],
    color="red",
    s=10,
    label="Аномалии"
)

ax.set_xlabel("Дата")
ax.set_ylabel("Температура (°C)")
ax.legend()
st.pyplot(fig)

anomaly_count = city_df["is_anomaly"].sum()
st.write(f"Найдено аномалий: {anomaly_count} из {len(city_df)} ({100*anomaly_count/len(city_df):.1f}%)")

st.header("Шаг 5: Сезонные профили")

season_order = ["winter", "spring", "summer", "autumn"]
seasonal_stats["season"] = pd.Categorical(
    seasonal_stats["season"], categories=season_order, ordered=True
)
seasonal_stats = seasonal_stats.sort_values("season")

fig2, ax2 = plt.subplots()
ax2.bar(
    seasonal_stats["season"],
    seasonal_stats["season_mean"],
    yerr=seasonal_stats["season_std"],
    capsize=5,
    color="red",
    edgecolor="black"
)
ax2.set_xlabel("Сезон")
ax2.set_ylabel("Температура (°C)")
ax2.set_title(f"Сезонный профиль для {city}")
st.pyplot(fig2)

# Шаг 6: Текущая температура
st.header("Шаг 6: Текущая температура")
api_key = st.text_input("Введите API-ключ OpenWeatherMap", type="password")

if api_key:
    weather = get_current_temperature(city, api_key)
    
    if "error" in weather:
        st.error(f"Ошибка API: {weather['error']}")
    else:
        current_temp = weather["temperature"]
        current_season = get_current_season()
        
        season_row = seasonal_stats[seasonal_stats["season"] == current_season].iloc[0]
        result = check_temperature_anomaly(
            current_temp,
            season_row["season_mean"],
            season_row["season_std"]
        )
        
        st.write(f"**Город:** {city}")
        st.write(f"**Текущая температура:** {current_temp:.1f}°C")
        st.write(f"**Описание:** {weather['description']}")
        st.write(f"**Сезон:** {current_season}")
        st.write(f"**Нормальный диапазон:** {result['lower_bound']:.1f}°C — {result['upper_bound']:.1f}°C")
        
        if result["is_anomaly"]:
            st.error("Температура аномальна для данного сезона")
        else:
            st.success("Температура в норме для данного сезона")
