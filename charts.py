import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Shared theme ──────────────────────────────────────────────────────────────
BG      = "#0f1117"
SURFACE = "#181c27"
ACCENT  = "#e8533a"
BLUE    = "#3a7bd5"
GREEN   = "#4caf80"
TEXT    = "#c8cdd8"
MUTED   = "#555d70"
GRID    = "#2a2f3e"

MONTH_NAMES = {4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep"}
DAY_ORDER   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
DAY_SHORT   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def _style(fig, ax):
    """Apply dark theme to a figure/axes."""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
    fig.tight_layout()
    return fig, ax

def _new(w=7, h=3.5):
    return plt.subplots(figsize=(w, h))


# ── 1. Bar Chart — Pickups by Hour ────────────────────────────────────────────
def plot_hourly_bar(df):
    hourly = df.groupby("Hour").size().reindex(range(24), fill_value=0)
    fig, ax = _new()
    colors = [ACCENT if h == hourly.idxmax() else "#e8533a55" for h in range(24)]
    ax.bar(hourly.index, hourly.values, color=colors, width=0.8, zorder=2)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Pickups")
    ax.set_title("Pickups by Hour of Day")
    ax.set_xticks(range(0, 24, 2))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    return _style(fig, ax)[0]


# ── 2. Histogram — Pickup Frequency by Hour ───────────────────────────────────
def plot_histogram(df):
    fig, ax = _new()
    ax.hist(df["Hour"], bins=24, range=(0,24), color=ACCENT, alpha=0.8, edgecolor=BG, zorder=2)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Frequency")
    ax.set_title("Frequency Distribution of Pickup Hours")
    return _style(fig, ax)[0]


# ── 3. Line Chart — Monthly Trend ────────────────────────────────────────────
def plot_monthly_line(df):
    monthly = df.groupby("Month").size().reindex(sorted(df["Month"].unique()), fill_value=0)
    fig, ax = _new()
    ax.plot(monthly.index, monthly.values, color=ACCENT, linewidth=2.5,
            marker="o", markersize=6, markerfacecolor=BG, markeredgecolor=ACCENT, zorder=3)
    ax.fill_between(monthly.index, monthly.values, alpha=0.15, color=ACCENT)
    ax.set_xticks(monthly.index)
    ax.set_xticklabels([MONTH_NAMES.get(m, m) for m in monthly.index])
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Pickups")
    ax.set_title("Monthly Pickup Trend")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    return _style(fig, ax)[0]


# ── 4. Bar Chart — Weekday ────────────────────────────────────────────────────
def plot_weekday_bar(df):
    wd = df.groupby("DayName").size().reindex(DAY_ORDER, fill_value=0)
    fig, ax = _new()
    colors = [ACCENT if d == wd.idxmax() else BLUE+"99" for d in DAY_ORDER]
    ax.bar(DAY_SHORT, wd.values, color=colors, zorder=2)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Pickups")
    ax.set_title("Pickups by Day of Week")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    return _style(fig, ax)[0]


# ── 5. Scatter Plot — Lat vs Lon ──────────────────────────────────────────────
def plot_scatter(df):
    sample = df.sample(min(5000, len(df)), random_state=42)
    fig, ax = _new(5, 4)
    ax.scatter(sample["Lon"], sample["Lat"], alpha=0.15, s=1.5,
               c=sample["Hour"], cmap="inferno", zorder=2)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Pickup Locations (sample)")
    ax.set_xlim(-74.3, -73.65)
    ax.set_ylim(40.45, 40.95)
    return _style(fig, ax)[0]


# ── 6. Box Plot — Hour by Base ────────────────────────────────────────────────
def plot_box(df):
    fig, ax = _new(6, 4)
    bases = sorted(df["Base"].unique())
    data  = [df[df["Base"] == b]["Hour"].dropna().values for b in bases]
    bp = ax.boxplot(data, labels=bases, patch_artist=True,
                    medianprops=dict(color=ACCENT, linewidth=2),
                    whiskerprops=dict(color=TEXT),
                    capprops=dict(color=TEXT),
                    flierprops=dict(marker=".", color=MUTED, markersize=3, alpha=0.4))
    for patch in bp["boxes"]:
        patch.set_facecolor(SURFACE)
        patch.set_edgecolor(GRID)
    ax.set_xlabel("Base")
    ax.set_ylabel("Hour of Day")
    ax.set_title("Hour Distribution by Base (Box Plot)")
    return _style(fig, ax)[0]


# ── 7. Heatmap — Day × Hour ───────────────────────────────────────────────────
def plot_heatmap(df):
    pivot = df.groupby(["DayName","Hour"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(DAY_ORDER)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.3,
                linecolor=BG, cbar_kws={"shrink":0.6},
                xticklabels=2, yticklabels=True)
    ax.set_title("Pickups Heatmap (Day × Hour)")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("")
    ax.tick_params(colors=TEXT, labelsize=8)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(SURFACE)
    fig.tight_layout()
    return fig


# ── 8. Area Chart — Cumulative Pickups by Month ───────────────────────────────
def plot_area(df):
    monthly = df.groupby("Month").size().reindex(sorted(df["Month"].unique()), fill_value=0)
    cumulative = monthly.cumsum()
    fig, ax = _new()
    ax.fill_between(cumulative.index, cumulative.values, alpha=0.4, color=GREEN)
    ax.plot(cumulative.index, cumulative.values, color=GREEN, linewidth=2.5,
            marker="o", markersize=5, markerfacecolor=BG, markeredgecolor=GREEN)
    ax.set_xticks(monthly.index)
    ax.set_xticklabels([MONTH_NAMES.get(m, m) for m in monthly.index])
    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Pickups")
    ax.set_title("Cumulative Pickups Over Time (Area Chart)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    return _style(fig, ax)[0]


# ── 9. Count Plot — Base Frequency ───────────────────────────────────────────
def plot_count(df):
    fig, ax = _new(6, 3.5)
    order = df["Base"].value_counts().index.tolist()
    counts = df["Base"].value_counts().reindex(order)
    colors = [ACCENT if i == 0 else BLUE+"99" for i in range(len(order))]
    ax.barh(order[::-1], counts.values[::-1], color=colors[::-1], zorder=2)
    ax.set_xlabel("Count")
    ax.set_title("Ride Count by Dispatch Base")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
    return _style(fig, ax)[0]


# ── 10. Violin Plot — Hour by Weekday ────────────────────────────────────────
def plot_violin(df):
    sample = df.sample(min(20000, len(df)), random_state=1)
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.violinplot(data=sample, x="DayName", y="Hour",
                   order=DAY_ORDER, ax=ax,
                   hue="DayName", legend=False,
                   palette=["#e8533a","#e8533a","#3a7bd5","#3a7bd5","#e8533a","#4caf80","#4caf80"],
                   inner="quartile", linewidth=0.8, cut=0)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Hour of Day")
    ax.set_title("Hour Distribution by Weekday (Violin Plot)")
    ax.tick_params(colors=TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5, axis="y")
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(SURFACE)
    fig.tight_layout()
    return fig


# ── Pie Chart — Base Share ────────────────────────────────────────────────────
def plot_base_pie(df):
    counts = df["Base"].value_counts()
    colors = [ACCENT, BLUE, GREEN, "#f0b429", "#9b6dff"]
    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=counts.index,
        autopct="%1.1f%%", colors=colors[:len(counts)],
        startangle=140, pctdistance=0.75,
        wedgeprops=dict(width=0.6, edgecolor=BG, linewidth=2)
    )
    for t in texts:
        t.set_color(TEXT); t.set_fontsize(9)
    for at in autotexts:
        at.set_color(BG); at.set_fontsize(8); at.set_fontweight("bold")
    ax.set_title("Ride Share by Base", color=TEXT)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    fig.tight_layout()
    return fig


# ── FOIL Trend — Active Vehicles & Trips ─────────────────────────────────────
def plot_foil_trend(df_foil):
    daily = df_foil.groupby("Date").agg({"ActiveVehicles":"sum","Trips":"sum"}).reset_index()
    fig, ax1 = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor(BG)
    ax1.set_facecolor(SURFACE)
    ax1.plot(daily["Date"], daily["Trips"], color=ACCENT, linewidth=2, label="Trips")
    ax1.set_ylabel("Total Trips", color=ACCENT)
    ax1.tick_params(axis="y", colors=ACCENT)
    ax1.tick_params(axis="x", colors=TEXT, labelsize=8)
    ax2 = ax1.twinx()
    ax2.set_facecolor(SURFACE)
    ax2.plot(daily["Date"], daily["ActiveVehicles"], color=BLUE, linewidth=2, linestyle="--", label="Active Vehicles")
    ax2.set_ylabel("Active Vehicles", color=BLUE)
    ax2.tick_params(axis="y", colors=BLUE)
    ax1.set_title("FOIL: Daily Trips vs Active Vehicles (Jan–Feb 2015)", color=TEXT, fontsize=13)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, facecolor=SURFACE, labelcolor=TEXT, fontsize=9)
    for spine in ax1.spines.values(): spine.set_color(GRID)
    ax1.grid(color=GRID, linewidth=0.5, alpha=0.5)
    fig.tight_layout()
    return fig


# ── FHV Companies Bar ─────────────────────────────────────────────────────────
def plot_fhv_companies(df_fhv):
    top = df_fhv.groupby("BaseName")["NumTrips"].sum().nlargest(15).sort_values()
    fig, ax = _new(8, 4)
    colors = [ACCENT if i == len(top)-1 else BLUE+"88" for i in range(len(top))]
    ax.barh(top.index, top.values, color=colors, zorder=2)
    ax.set_xlabel("Total Trips")
    ax.set_title("FHV Services: Top 15 Bases by Trips (2015)", fontsize=13)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    ax.grid(axis="x", color=GRID, linewidth=0.5, alpha=0.5)
    return _style(fig, ax)[0]


# ── Year Comparison Line ───────────────────────────────────────────────────────
def plot_year_comparison(df_all):
    fig, ax = _new(10, 4)
    colors_map = {2014: ACCENT, 2015: BLUE}
    for yr, grp in df_all.groupby("Year"):
        monthly = grp.groupby("Month").size()
        ax.plot(monthly.index, monthly.values,
                color=colors_map.get(yr, GREEN), linewidth=2.5,
                marker="o", markersize=6, markerfacecolor=BG,
                markeredgecolor=colors_map.get(yr, GREEN),
                label=str(yr), zorder=3)
        ax.fill_between(monthly.index, monthly.values, alpha=0.08,
                        color=colors_map.get(yr, GREEN))
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Pickups")
    ax.set_title("2014 vs 2015 Monthly Pickup Comparison", fontsize=13)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
    ax.legend(facecolor=SURFACE, labelcolor=TEXT, fontsize=9)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
    return _style(fig, ax)[0]
