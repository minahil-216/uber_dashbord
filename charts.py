import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# ── Global Style ──────────────────────────────────────────────────────────────
BG      = "#0b0f1a"
PANEL   = "#1a2235"
BORDER  = "#1e2d45"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"
PALETTE = ["#00c6ff","#7b5ea7","#ff6b6b","#43e97b","#f7971e","#f64f59","#c471ed","#12c2e9"]

def _style(fig, ax):
    """Apply dark theme to any figure/axes."""
    fig.patch.set_facecolor(BG)
    if isinstance(ax, np.ndarray):
        axes = ax.flatten()
    else:
        axes = [ax]
    for a in axes:
        a.set_facecolor(PANEL)
        a.tick_params(colors=MUTED, labelsize=9)
        a.xaxis.label.set_color(MUTED)
        a.yaxis.label.set_color(MUTED)
        a.title.set_color(TEXT)
        for spine in a.spines.values():
            spine.set_edgecolor(BORDER)
    fig.tight_layout(pad=2)
    return fig, ax


# ── 1. Pie Chart ──────────────────────────────────────────────────────────────
def plot_pie_chart(df):
    counts = df["Base"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(counts)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=1.5),
        pctdistance=0.82
    )
    for t in texts:   t.set_color(TEXT);  t.set_fontsize(9)
    for t in autotexts: t.set_color(BG); t.set_fontweight("bold"); t.set_fontsize(8)
    ax.set_title("Base Dispatch Distribution", color=TEXT, fontsize=11, fontweight="bold", pad=10)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    fig.tight_layout()
    return fig


# ── 2. Histogram ──────────────────────────────────────────────────────────────
def plot_histogram(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(df["Hour"], bins=24, range=(0, 24), color="#00c6ff",
            edgecolor=BG, linewidth=0.8, alpha=0.85)
    ax.set_xlabel("Hour of Day", color=MUTED)
    ax.set_ylabel("Frequency", color=MUTED)
    ax.set_title("Pickup Frequency by Hour", color=TEXT, fontsize=11, fontweight="bold")
    ax.axvline(df["Hour"].mean(), color="#ff6b6b", linestyle="--", linewidth=1.5,
               label=f"Mean: {df['Hour'].mean():.1f}h")
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    return _style(fig, ax)[0]


# ── 3. Line Chart ─────────────────────────────────────────────────────────────
def plot_line_chart(df):
    hourly = df.groupby("Hour").size().reset_index(name="Pickups")
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(hourly["Hour"], hourly["Pickups"], color="#00c6ff",
            linewidth=2, marker="o", markersize=3, markerfacecolor="#ff6b6b")
    ax.fill_between(hourly["Hour"], hourly["Pickups"], alpha=0.15, color="#00c6ff")
    ax.set_xlabel("Hour of Day", color=MUTED)
    ax.set_ylabel("Number of Pickups", color=MUTED)
    ax.set_title("Hourly Pickup Trend", color=TEXT, fontsize=11, fontweight="bold")
    ax.set_xticks(range(0, 24, 2))
    return _style(fig, ax)[0]


# ── 4. Bar Chart ──────────────────────────────────────────────────────────────
def plot_bar_chart(df):
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    daily = df.groupby("DayOfWeek").size().reindex(days_order, fill_value=0)
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(range(len(daily)), daily.values,
                  color=PALETTE[:len(daily)], edgecolor=BG, linewidth=0.8, width=0.7)
    ax.set_xticks(range(len(daily)))
    ax.set_xticklabels([d[:3] for d in days_order], color=MUTED, fontsize=9)
    ax.set_xlabel("Day of Week", color=MUTED)
    ax.set_ylabel("Number of Pickups", color=MUTED)
    ax.set_title("Pickups by Day of Week", color=TEXT, fontsize=11, fontweight="bold")
    for bar, val in zip(bars, daily.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + daily.values.max()*0.01,
                f"{val:,}", ha="center", va="bottom", color=MUTED, fontsize=7)
    return _style(fig, ax)[0]


# ── 5. Scatter Plot ───────────────────────────────────────────────────────────
def plot_scatter(df):
    sample = df.sample(min(3000, len(df)), random_state=42) if len(df) > 0 else df
    fig, ax = plt.subplots(figsize=(5, 4))
    scatter = ax.scatter(
        sample["Lon"], sample["Lat"],
        c=sample["Hour"], cmap="plasma",
        alpha=0.35, s=2, linewidths=0
    )
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=MUTED, labelsize=8)
    cbar.set_label("Hour of Day", color=MUTED, fontsize=9)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=MUTED)
    ax.set_xlim(-74.1, -73.75)
    ax.set_ylim(40.6, 40.92)
    ax.set_xlabel("Longitude", color=MUTED)
    ax.set_ylabel("Latitude", color=MUTED)
    ax.set_title("Geospatial Pickup Distribution", color=TEXT, fontsize=11, fontweight="bold")
    return _style(fig, ax)[0]


# ── 6. Box Plot ───────────────────────────────────────────────────────────────
def plot_box_plot(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    bases = sorted(df["Base"].unique())
    data  = [df[df["Base"] == b]["Hour"].values for b in bases]
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="#ff6b6b", linewidth=2),
                    whiskerprops=dict(color=MUTED),
                    capprops=dict(color=MUTED),
                    flierprops=dict(marker=".", color=MUTED, markersize=3, alpha=0.5))
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color + "55")
        patch.set_edgecolor(color)
    ax.set_xticklabels(bases, color=MUTED, fontsize=8)
    ax.set_xlabel("Dispatch Base", color=MUTED)
    ax.set_ylabel("Hour of Day", color=MUTED)
    ax.set_title("Hour Distribution by Base (Box Plot)", color=TEXT, fontsize=11, fontweight="bold")
    return _style(fig, ax)[0]


# ── 7. Heatmap ────────────────────────────────────────────────────────────────
def plot_heatmap(df):
    num_cols = ["Hour", "Lat", "Lon", "DayNum", "Month", "WeekOfYear"]
    available = [c for c in num_cols if c in df.columns]
    corr = df[available].corr()
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        corr, ax=ax, annot=True, fmt=".2f",
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        linewidths=0.5, linecolor=BG,
        annot_kws={"size": 8, "color": TEXT},
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Feature Correlation Heatmap", color=TEXT, fontsize=11, fontweight="bold")
    ax.tick_params(axis="x", rotation=30, colors=MUTED, labelsize=8)
    ax.tick_params(axis="y", rotation=0,  colors=MUTED, labelsize=8)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    fig.tight_layout()
    return fig


# ── 8. Area Chart ─────────────────────────────────────────────────────────────
def plot_area_chart(df):
    if "Date" not in df.columns:
        df = df.copy()
        df["Date"] = df["Date/Time"].dt.date
    daily = df.groupby("Date").size().reset_index(name="Pickups")
    daily = daily.sort_values("Date")
    daily["Cumulative"] = daily["Pickups"].cumsum()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.fill_between(range(len(daily)), daily["Cumulative"],
                    alpha=0.3, color="#00c6ff")
    ax.plot(range(len(daily)), daily["Cumulative"],
            color="#00c6ff", linewidth=1.8)
    step = max(1, len(daily) // 5)
    ax.set_xticks(range(0, len(daily), step))
    ax.set_xticklabels([str(daily["Date"].iloc[i]) for i in range(0, len(daily), step)],
                       rotation=25, ha="right", fontsize=7)
    ax.set_xlabel("Date", color=MUTED)
    ax.set_ylabel("Cumulative Pickups", color=MUTED)
    ax.set_title("Cumulative Pickups Over Time", color=TEXT, fontsize=11, fontweight="bold")
    return _style(fig, ax)[0]


# ── 9. Count Plot ─────────────────────────────────────────────────────────────
def plot_count_plot(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    order = df["Base"].value_counts().index
    sns.countplot(data=df, y="Base", order=order,
                  palette=PALETTE[:len(order)], ax=ax,
                  edgecolor=BG, linewidth=0.8)
    ax.set_xlabel("Count", color=MUTED)
    ax.set_ylabel("Dispatch Base", color=MUTED)
    ax.set_title("Pickups Count by Base", color=TEXT, fontsize=11, fontweight="bold")
    ax.tick_params(colors=MUTED, labelsize=9)
    for bar in ax.patches:
        w = bar.get_width()
        ax.text(w + ax.get_xlim()[1]*0.005, bar.get_y() + bar.get_height()/2,
                f"{int(w):,}", va="center", ha="left", color=MUTED, fontsize=8)
    return _style(fig, ax)[0]


# ── 10. Violin Plot ───────────────────────────────────────────────────────────
def plot_violin_plot(df):
    top_bases = df["Base"].value_counts().head(4).index.tolist()
    sub = df[df["Base"].isin(top_bases)]
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.violinplot(data=sub, x="Base", y="Hour", order=top_bases,
                   palette=PALETTE[:len(top_bases)], ax=ax,
                   inner="quartile", linewidth=1.2, cut=0)
    ax.set_xlabel("Dispatch Base", color=MUTED)
    ax.set_ylabel("Hour of Day", color=MUTED)
    ax.set_title("Hour Distribution by Base (Violin)", color=TEXT, fontsize=11, fontweight="bold")
    ax.tick_params(colors=MUTED, labelsize=9)
    return _style(fig, ax)[0]
