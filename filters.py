import os
import glob
import pandas as pd
 
 
# ── Load main Uber raw data (2014 + 2015) ─────────────────────────────────────
def load_data(data_dir: str) -> pd.DataFrame:
    """
    Loads all uber-raw-data-*.csv files from data_dir.
    Expected columns (2014 format): Date/Time, Lat, Lon, Base
    Also handles 2015 format:       Date/Time, Lat, Lon, Base, key, dispatching_base_num
    """
    pattern = os.path.join(data_dir, "uber-raw-data-*.csv")
    files = sorted(glob.glob(pattern))
 
    if not files:
        raise FileNotFoundError(
            f"No Uber raw data CSV files found in '{data_dir}'.\n"
            "Expected files like: uber-raw-data-apr14.csv, uber-raw-data-sep14.csv …"
        )
 
    frames = []
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            # Normalise column names
            df.columns = df.columns.str.strip()
 
            # Rename to standard names
            rename_map = {}
            for col in df.columns:
                lc = col.lower().replace("/", "_").replace(" ", "_")
                if lc in ("date_time", "datetime"):
                    rename_map[col] = "DateTime"
                elif lc == "lat":
                    rename_map[col] = "Lat"
                elif lc == "lon":
                    rename_map[col] = "Lon"
                elif lc == "base":
                    rename_map[col] = "Base"
            df.rename(columns=rename_map, inplace=True)
 
            # Tag source file
            df["source"] = os.path.basename(f).replace(".csv", "")
            frames.append(df)
        except Exception as e:
            print(f"Warning: could not load {f}: {e}")
 
    df_all = pd.concat(frames, ignore_index=True)
 
    # Parse datetime
    df_all["DateTime"] = pd.to_datetime(df_all["DateTime"], infer_datetime_format=True)
 
    # Derived time columns
    df_all["Hour"]    = df_all["DateTime"].dt.hour
    df_all["Month"]   = df_all["DateTime"].dt.month
    df_all["Year"]    = df_all["DateTime"].dt.year
    df_all["DayName"] = df_all["DateTime"].dt.day_name()
 
    # Ensure Lat/Lon are numeric
    df_all["Lat"] = pd.to_numeric(df_all["Lat"], errors="coerce")
    df_all["Lon"] = pd.to_numeric(df_all["Lon"], errors="coerce")
 
    # Drop rows with missing critical fields
    df_all.dropna(subset=["Lat", "Lon", "Hour", "Base"], inplace=True)
 
    return df_all
 
 
# ── Load FOIL aggregate data ───────────────────────────────────────────────────
def load_foil(data_dir: str):
    """
    Loads Uber_Jan_Feb_FOIL.csv (or similar).
    Expected columns: dispatching_base_number, date, active_vehicles, trips
    """
    candidates = [
        "Uber_Jan_Feb_FOIL.csv",
        "uber-trip-data-foil-jan-feb-2015.csv",
        "uber_jan_feb_foil.csv",
    ]
    for name in candidates:
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
 
            # Normalise column names
            col_map = {}
            for c in df.columns:
                lc = c.lower().replace(" ", "_")
                if "date" in lc:
                    col_map[c] = "Date"
                elif "active" in lc:
                    col_map[c] = "ActiveVehicles"
                elif "trip" in lc:
                    col_map[c] = "Trips"
                elif "base" in lc:
                    col_map[c] = "Base"
            df.rename(columns=col_map, inplace=True)
 
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], infer_datetime_format=True)
 
            return df
 
    # No file found — return None (app.py already guards with `if df_foil is not None`)
    return None
 
 
# ── Load FHV trip data ─────────────────────────────────────────────────────────
def load_fhv(data_dir: str):
    """
    Loads FHV trip data (e.g. other-data-fhv-businesses-jan-aug-2015.csv).
    Expected columns: Base Name, Base License Number, NumTrips (or Trips)
    """
    candidates = [
        "other-data-fhv-businesses-jan-aug-2015.csv",
        "fhv_trip_data_jan_aug_2015.csv",
        "fhv-businesses.csv",
    ]
    for name in candidates:
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
 
            col_map = {}
            for c in df.columns:
                lc = c.lower().replace(" ", "_")
                if "base_name" in lc or "name" in lc:
                    col_map[c] = "BaseName"
                elif "license" in lc or "base_number" in lc or "base_license" in lc:
                    col_map[c] = "BaseLicense"
                elif "trip" in lc or "num_trips" in lc:
                    col_map[c] = "NumTrips"
            df.rename(columns=col_map, inplace=True)
 
            if "NumTrips" in df.columns:
                df["NumTrips"] = pd.to_numeric(df["NumTrips"], errors="coerce").fillna(0)
 
            return df
 
    return None
 
 
# ── Load other FHV bases (Lyft, Carmel, Dial7, etc.) ─────────────────────────
def load_other_bases(data_dir: str):
    """
    Loads other-data-lyft-carmel-dial7-ground-2015.csv or similar.
    Expected columns: Company, Date/Time, Lat, Lon, Base
    """
    candidates = [
        "other-data-lyft-carmel-dial7-ground-2015.csv",
        "other_bases_2015.csv",
        "lyft-carmel-dial7.csv",
    ]
    for name in candidates:
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            df.columns = df.columns.str.strip()
 
            col_map = {}
            for c in df.columns:
                lc = c.lower().replace("/", "_").replace(" ", "_")
                if lc in ("date_time", "datetime", "pickup_date"):
                    col_map[c] = "DateTime"
                elif lc == "lat":
                    col_map[c] = "Lat"
                elif lc == "lon":
                    col_map[c] = "Lon"
                elif lc == "base":
                    col_map[c] = "Base"
                elif "company" in lc or "dispatching" in lc:
                    col_map[c] = "Company"
            df.rename(columns=col_map, inplace=True)
 
            if "DateTime" in df.columns:
                df["DateTime"] = pd.to_datetime(df["DateTime"], infer_datetime_format=True)
                df["Hour"]    = df["DateTime"].dt.hour
                df["DayName"] = df["DateTime"].dt.day_name()
 
            # plot_count expects a "Base" column
            if "Company" in df.columns and "Base" not in df.columns:
                df["Base"] = df["Company"]
 
            return df
 
    return None
 
 
# ── Apply sidebar filters ──────────────────────────────────────────────────────
def apply_filters(
    df: pd.DataFrame,
    selected_months: list,
    selected_base: str,
    hour_range: tuple,
    selected_day: str,
    lat_range: tuple,
    selected_year: str,
) -> pd.DataFrame:
    """
    Filter the main dataframe according to sidebar selections.
    All parameters match what app.py passes.
    """
    mask = pd.Series(True, index=df.index)
 
    # Month filter
    if selected_months:
        mask &= df["Month"].isin(selected_months)
 
    # Base filter
    if selected_base != "All":
        mask &= df["Base"] == selected_base
 
    # Hour range filter
    mask &= df["Hour"].between(hour_range[0], hour_range[1])
 
    # Day of week filter
    if selected_day != "All":
        mask &= df["DayName"] == selected_day
 
    # Latitude range filter
    mask &= df["Lat"].between(lat_range[0], lat_range[1])
 
    # Year filter
    if selected_year != "All":
        mask &= df["Year"] == int(selected_year)
 
    return df[mask].copy()
