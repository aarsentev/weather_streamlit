import pandas as pd


def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["city", "timestamp"]).reset_index(drop=True)
    return df


def get_city_data(df, city):
    city_df = df[df["city"] == city].copy()
    city_df = city_df.sort_values("timestamp").reset_index(drop=True)
    return city_df


def get_basic_stats(city_df):
    stats = city_df["temperature"].describe().to_frame().T
    return stats


def add_rolling_stats(city_df, window=30):
    city_df = city_df.copy()

    city_df["rolling_mean"] = (
        city_df["temperature"]
        .rolling(window=window, min_periods=1)
        .mean()
    )

    city_df["rolling_std"] = (
        city_df["temperature"]
        .rolling(window=window, min_periods=1)
        .std()
    )

    city_df["rolling_std"] = city_df["rolling_std"].fillna(0)

    return city_df


def compute_seasonal_stats(city_df):
    stats = city_df.groupby("season")["temperature"].agg(["mean", "std"]).reset_index()
    stats.columns = ["season", "season_mean", "season_std"]
    return stats


def detect_anomalies(city_df):
    city_df = city_df.copy()

    # Вычисляем сезонную статистику
    seasonal_stats = city_df.groupby("season")["temperature"].agg(["mean", "std"])

    # Присоединяем к данным
    city_df = city_df.merge(
        seasonal_stats,
        left_on="season",
        right_index=True,
        how="left"
    )

    # Определяем аномалии
    city_df["is_anomaly"] = (
            (city_df["temperature"] < city_df["mean"] - 2 * city_df["std"]) |
            (city_df["temperature"] > city_df["mean"] + 2 * city_df["std"])
    )

    return city_df

