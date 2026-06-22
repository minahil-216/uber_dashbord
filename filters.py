import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], errors="coerce")
    df.dropna(subset=["Date/Time"], inplace=True)
    df.dropna(subset=["Lat", "Lon"], inplace=True)
    df = df[(df["Lat"] >= 40.4) & (df["Lat"] <= 41.0)]
    df = df[(df["Lon"] >= -74.3) & (df["Lon"] <= -73.6)]
    df["Hour"]       = df["Date/Time"].dt.hour
    df["Month"]      = df["Date/Time"].dt.month
    df["DayNum"]     = df["Date/Time"].dt.dayofweek
    df["DayOfWeek"]  = df["Date/Time"].dt.day_name()
    df["WeekOfYear"] = df["Date/Time"].dt.isocalendar().week.astype(int)
    df["Date"]       = df["Date/Time"].dt.date
    df["Base"]       = df["Base"].astype(str).str.strip()
    return df.reset_index(drop=True)


def apply_filters(df, date_range=None, bases=None, hour_range=(0, 23), days=None, search_text=""):
    filtered = df.copy()
    if date_range is not None and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        end = end + pd.Timedelta(days=1)
        filtered = filtered[(filtered["Date/Time"] >= start) & (filtered["Date/Time"] < end)]
    if bases is not None and len(bases) > 0:
        filtered = filtered[filtered["Base"].isin(bases)]
    if hour_range is not None:
        filtered = filtered[(filtered["Hour"] >= hour_range[0]) & (filtered["Hour"] <= hour_range[1])]
    if days is not None and len(days) > 0:
        filtered = filtered[filtered["DayOfWeek"].isin(days)]
    if search_text and search_text.strip() != "":
        keyword = search_text.strip().lower()
        filtered = filtered[filtered["Base"].str.lower().str.contains(keyword, na=False)]
    return filtered.reset_index(drop=True)


def get_kpis(df):
    if len(df) == 0:
        return {"total": 0, "peak_hour": "N/A", "peak_day": "N/A", "top_base": "N/A", "avg_hour": 0}
    return {
        "total":     len(df),
        "peak_hour": df.groupby("Hour").size().idxmax(),
        "peak_day":  df.groupby("DayOfWeek").size().idxmax(),
        "top_base":  df["Base"].value_counts().idxmax(),
        "avg_hour":  round(df["Hour"].mean(), 1),
    }
