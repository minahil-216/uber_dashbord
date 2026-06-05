# 🚖 NYC Uber Pickups Dashboard

**Course:** Exploratory Data Analysis  
**Dataset:** Uber NYC Pickups 2014 (600,000+ rides, Apr–Sep)

---

## How to Run (Step by Step)

### Step 1 — Install Python
Download from https://python.org (version 3.10 or newer)

### Step 2 — Open Terminal / Command Prompt
- Windows: press `Win + R`, type `cmd`, press Enter
- Mac: open Terminal from Applications

### Step 3 — Go to this folder
```
cd path/to/dashboard_project
```

### Step 4 — Install required packages
```
pip install -r requirements.txt
```

### Step 5 — Make sure data files are in the data/ folder

- `uber-raw-data-apr14.csv`
- `uber-raw-data-may14.csv`
- `uber-raw-data-jun14.csv`
- `uber-raw-data-jul14.csv`
- `uber-raw-data-aug14.csv`
- `uber-raw-data-sep14.csv`

### Step 6 — Run the dashboard
```
streamlit run app.py
```

A browser window will open automatically at http://localhost:8501

---

## Project Files

| File | What it does |
|------|-------------|
| `app.py` | Main dashboard — layout, KPI cards, calls charts |
| `charts.py` | All 10 chart functions (bar, pie, heatmap, violin, etc.) |
| `filters.py` | Data loading and filter logic |
| `requirements.txt` | Python packages to install |

---

## Key Insights

- **Peak hour** is 17:00 (5 PM) — evening commute drives the most rides
- **Fridays** are the busiest day of the week
- **September** had the highest monthly pickups, showing growth across summer
- **Base B02617** handles the largest share of dispatches (~31%)
- Most rides originate in **Manhattan** (lower lat/lon cluster)

---

## Charts Included

1. Bar Chart — Pickups by hour  
2. Histogram — Hour frequency distribution  
3. Line Chart — Monthly pickup trend  
4. Bar Chart — Pickups by weekday  
5. Scatter Plot — Pickup geo-locations  
6. Box Plot — Hour distribution per base  
7. Heatmap — Day × hour pickup density  
8. Area Chart — Cumulative monthly pickups  
9. Count Plot — Rides per dispatch base  
10. Violin Plot — Hour distribution by weekday  
