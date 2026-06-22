import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from filters import load_data, load_foil, load_fhv, load_other_bases, apply_filters
from charts import (
    plot_hourly_bar, plot_monthly_line, plot_base_pie,
    plot_weekday_bar, plot_heatmap, plot_scatter,
    plot_box, plot_area, plot_count, plot_violin,
    plot_foil_trend, plot_fhv_companies, plot_year_comparison, plot_histogram
)

st.set_page_config(
    page_title="NYC Uber Pickups Dashboard",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #181c27; }
    [data-testid="stSidebar"] * { color: #c8cdd8 !important; }
    .stMetric { background: #181c27; border-radius: 10px; padding: 10px; border: 1px solid #2a2f3e; }
    h1, h2, h3 { color: #e8e3d5 !important; }
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_all_data():
    return load_data("data/")

@st.cache_data
def get_foil():
    return load_foil("data/")

@st.cache_data
def get_fhv():
    return load_fhv("data/")

@st.cache_data
def get_others():
    return load_data("https://raw.githubusercontent.com/fivethirtyeight/uber-TLC-foil-response/master/uber-trip-data/uber-raw-data-apr14.csv")

df_all    = get_all_data()
df_foil   = get_foil()
df_fhv    = get_fhv()
df_others = get_others()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
st.sidebar.markdown("---")

years_available = ["All"] + sorted(df_all["Year"].unique().astype(str).tolist())
selected_year = st.sidebar.selectbox("Year", years_available)

months_available = sorted(df_all["Month"].unique())
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
selected_months = st.sidebar.multiselect(
    "Month", options=months_available, default=months_available,
    format_func=lambda x: month_names.get(x, str(x))
)

bases = ["All"] + sorted(df_all["Base"].unique().tolist())
selected_base = st.sidebar.selectbox("Dispatch Base", bases)

hour_range = st.sidebar.slider("Hour Range", 0, 23, (0, 23))

days = ["All","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
selected_day = st.sidebar.selectbox("Day of Week", days)

lat_range = st.sidebar.slider(
    "Latitude Range",
    float(df_all["Lat"].min()), float(df_all["Lat"].max()),
    (float(df_all["Lat"].quantile(0.01)), float(df_all["Lat"].quantile(0.99)))
)

source_opts = ["All"] + sorted(df_all["source"].unique().tolist())
selected_source = st.sidebar.selectbox("Data Source", source_opts)

if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = apply_filters(df_all, selected_months, selected_base, hour_range, selected_day, lat_range, selected_year)
if selected_source != "All":
    df = df[df["source"] == selected_source]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 🚖 NYC Uber & FHV Pickups Dashboard")
st.markdown("**Dataset:** Uber NYC 2014 + 2015 · Other FHV Companies · FOIL Aggregate Data | **Course:** Exploratory Data Analysis")
st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("📦 Total Pickups",    f"{len(df):,}")
c2.metric("🕐 Peak Hour",        f"{df['Hour'].mode()[0]:02d}:00" if len(df) > 0 else "N/A")
c3.metric("📅 Busiest Day",      df["DayName"].mode()[0] if len(df) > 0 else "N/A")
c4.metric("🏢 Top Base",         df["Base"].mode()[0] if len(df) > 0 else "N/A")
c5.metric("🗓️ Years Covered",   f"{df['Year'].nunique()}")
c6.metric("📊 Months Shown",     len(df["Month"].unique()))

st.markdown("---")

# ── SECTION 1: Temporal ───────────────────────────────────────────────────────
st.markdown("### 📊 Temporal Analysis")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Pickups by Hour** (Bar Chart)")
    fig = plot_hourly_bar(df); st.pyplot(fig); plt.close()
with col2:
    st.markdown("**Monthly Trend** (Line Chart)")
    fig = plot_monthly_line(df); st.pyplot(fig); plt.close()

col3, col4 = st.columns(2)
with col3:
    st.markdown("**Hour Frequency** (Histogram)")
    fig = plot_histogram(df); st.pyplot(fig); plt.close()
with col4:
    st.markdown("**Cumulative Pickups** (Area Chart)")
    fig = plot_area(df); st.pyplot(fig); plt.close()

# ── SECTION 2: Category ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🏢 Base & Category Analysis")
col5, col6, col7 = st.columns(3)
with col5:
    st.markdown("**Base Share** (Pie Chart)")
    fig = plot_base_pie(df); st.pyplot(fig); plt.close()
with col6:
    st.markdown("**Rides per Base** (Count Plot)")
    fig = plot_count(df); st.pyplot(fig); plt.close()
with col7:
    st.markdown("**Pickups by Weekday** (Bar Chart)")
    fig = plot_weekday_bar(df); st.pyplot(fig); plt.close()

# ── SECTION 3: Distributions ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Distribution Analysis")
col8, col9 = st.columns(2)
with col8:
    st.markdown("**Hour Distribution by Base** (Box Plot)")
    fig = plot_box(df); st.pyplot(fig); plt.close()
with col9:
    st.markdown("**Hour Distribution by Weekday** (Violin Plot)")
    fig = plot_violin(df); st.pyplot(fig); plt.close()

st.markdown("**Pickup Locations** (Scatter Plot)")
fig = plot_scatter(df); st.pyplot(fig); plt.close()

st.markdown("**Hour × Day Heatmap**")
fig = plot_heatmap(df); st.pyplot(fig); plt.close()

# ── SECTION 4: Extra Datasets ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔗 Additional Dataset Insights")

if df_foil is not None:
    st.markdown("**Active Vehicles & Trips Over Time** — FOIL Aggregate Data (Jan–Feb 2015)")
    fig = plot_foil_trend(df_foil); st.pyplot(fig); plt.close()

if df_fhv is not None:
    col10, col11 = st.columns(2)
    with col10:
        st.markdown("**FHV Trips by Base** (Jan–Aug 2015)")
        fig = plot_fhv_companies(df_fhv); st.pyplot(fig); plt.close()

if df_all["Year"].nunique() > 1:
    col12, _ = st.columns(2)
    with col12:
        st.markdown("**2014 vs 2015 Monthly Comparison**")
        fig = plot_year_comparison(df_all); st.pyplot(fig); plt.close()

if df_others is not None:
    st.markdown("**Other FHV Companies — Hourly Pickup Pattern** (Lyft, Carmel, Dial7, etc.)")
    fig = plot_count(df_others.rename(columns={"Company":"Base"})); st.pyplot(fig); plt.close()

st.markdown("---")
st.markdown("*Built with Python · Pandas · Matplotlib · Seaborn · Streamlit*")
