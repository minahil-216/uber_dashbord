import streamlit as st
import pandas as pd
import numpy as np
from filters import load_data, apply_filters
from charts import (
    plot_pie_chart, plot_histogram, plot_line_chart, plot_bar_chart,
    plot_scatter, plot_box_plot, plot_heatmap, plot_area_chart,
    plot_count_plot, plot_violin_plot
)

st.set_page_config(
    page_title="Uber NYC Pickups Dashboard",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0b0f1a; color: #e2e8f0; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1e2d45; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .kpi-card {
        background: #1a2235;
        border: 1px solid #1e2d45;
        border-left: 3px solid #00c6ff;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .kpi-value { font-size: 26px; font-weight: 800; color: #00c6ff; font-family: monospace; }
    .kpi-label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-sub   { font-size: 11px; color: #64748b; margin-top: 4px; }
    .section-title {
        font-size: 13px; font-weight: 700; color: #00c6ff;
        text-transform: uppercase; letter-spacing: 1.5px;
        border-bottom: 1px solid #1e2d45; padding-bottom: 6px; margin-bottom: 14px;
    }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

DATA_URL = "https://raw.githubusercontent.com/fivethirtyeight/uber-TLC-foil-response/master/uber-trip-data/uber-raw-data-apr14.csv"

@st.cache_data
def get_data():
    return load_data(DATA_URL)

df_raw = get_data()

with st.sidebar:
    st.markdown("## 🚖 UberNYC EDA")
    st.markdown("**Exploratory Data Analysis Dashboard**")
    st.markdown("---")
    st.markdown("### ⚙️ Filters")

    search_text = st.text_input("🔍 Search (Base)", placeholder="e.g. B02617")

    st.markdown("**📅 Date Range**")
    min_date = df_raw["Date/Time"].dt.date.min()
    max_date = df_raw["Date/Time"].dt.date.max()
    date_range = st.date_input("Select range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    all_bases = sorted(df_raw["Base"].unique().tolist())
    selected_bases = st.multiselect("🏢 Dispatch Base", all_bases, default=all_bases)

    hour_range = st.slider("🕐 Hour of Day", 0, 23, (0, 23))

    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    selected_days = st.multiselect("📆 Day of Week", days_order, default=days_order)

    st.markdown("---")
    if st.button("↺ Reset All Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#64748b;'>
    <b style='color:#00c6ff'>Dataset</b><br>
    Kaggle – Uber NYC Pickups<br>
    600K+ records · Apr 2014<br><br>
    <b style='color:#00c6ff'>Course</b><br>
    Exploratory Data Analysis<br>
    Instructor: Ali Hassan Sherazi
    </div>
    """, unsafe_allow_html=True)

df = apply_filters(
    df_raw,
    date_range=date_range if len(date_range) == 2 else (min_date, max_date),
    bases=selected_bases,
    hour_range=hour_range,
    days=selected_days,
    search_text=search_text
)

st.markdown("# 🚖 Uber Pickups NYC — EDA Dashboard")
st.markdown(f"*Analyzing **{len(df):,}** records after filters · Apr 2014*")
st.markdown("---")

total     = len(df)
peak_hour = df.groupby("Hour").size().idxmax() if total > 0 else "N/A"
peak_day  = df.groupby("DayOfWeek").size().idxmax() if total > 0 else "N/A"
top_base  = df["Base"].value_counts().idxmax() if total > 0 else "N/A"
avg_hour  = round(df["Hour"].mean(), 1) if total > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
for col, label, value, sub, color in [
    (c1, "Total Pickups",  f"{total:,}",      "filtered records",  "#00c6ff"),
    (c2, "Peak Hour",      f"{peak_hour}h",   "busiest hour",      "#7b5ea7"),
    (c3, "Peak Day",       str(peak_day)[:3], "most active day",   "#ff6b6b"),
    (c4, "Top Base",       str(top_base),     "most dispatches",   "#43e97b"),
    (c5, "Avg Hour",       str(avg_hour),     "mean pickup time",  "#f7971e"),
]:
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">📈 Temporal Trends</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown("**③ Hourly Pickup Trend** — Line Chart")
    st.pyplot(plot_line_chart(df))
with col2:
    st.markdown("**④ Pickups by Day of Week** — Bar Chart")
    st.pyplot(plot_bar_chart(df))

st.markdown('<div class="section-title">🥧 Distribution Overview</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    st.markdown("**① Base Dispatch Distribution** — Pie Chart")
    st.pyplot(plot_pie_chart(df))
with col4:
    st.markdown("**② Hour Frequency** — Histogram")
    st.pyplot(plot_histogram(df))

st.markdown('<div class="section-title">📊 Categorical & Cumulative</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)
with col5:
    st.markdown("**⑧ Cumulative Pickups Over Time** — Area Chart")
    st.pyplot(plot_area_chart(df))
with col6:
    st.markdown("**⑨ Pickups by Base** — Count Plot")
    st.pyplot(plot_count_plot(df))

st.markdown('<div class="section-title">📍 Spatial & Statistical</div>', unsafe_allow_html=True)
col7, col8 = st.columns(2)
with col7:
    st.markdown("**⑤ Lat/Lon Pickup Scatter** — Scatter Plot")
    st.pyplot(plot_scatter(df))
with col8:
    st.markdown("**⑥ Hour Distribution by Base** — Box Plot")
    st.pyplot(plot_box_plot(df))

st.markdown('<div class="section-title">🔥 Correlation & Density</div>', unsafe_allow_html=True)
col9, col10 = st.columns(2)
with col9:
    st.markdown("**⑦ Feature Correlation** — Heatmap")
    st.pyplot(plot_heatmap(df))
with col10:
    st.markdown("**⑩ Hour Distribution by Base** — Violin Plot")
    st.pyplot(plot_violin_plot(df))

st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:11px; color:#64748b;'>"
    "Dataset: Kaggle – Uber Pickups NYC · Course: Exploratory Data Analysis · "
    "Instructor: Ali Hassan Sherazi · All charts update dynamically with filters"
    "</div>", unsafe_allow_html=True
)
