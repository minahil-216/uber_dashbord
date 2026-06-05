import pandas as pd
import numpy as np
import os
import glob
import requests

# ─────────────────────────────────────────────────────────────────────────────
# PASTE YOUR GOOGLE DRIVE FILE IDs BELOW
#
# How to get a File ID:
#   1. Right-click the file in Google Drive → Share → Copy link
#   2. Link looks like: https://drive.google.com/file/d/THIS_IS_THE_ID/view?usp=sharing
#   3. Copy only the part between /d/ and /view  →  paste below
# ─────────────────────────────────────────────────────────────────────────────

FILE_IDS = {
    # ── Main Uber raw pickups (2014) ──
    "uber-raw-data-apr14.csv":          "1sCFKinh8ZkV1ilZqYO_pRnlOAFfaCz1J",
    "uber-raw-data-may14.csv":          "14RnipKZ_lAnfk3OBFu9jWbPpVnb1acEi",
    "uber-raw-data-jun14.csv":          "1K9SZ-2EGoaOpp5euOdtrz6e9iNKg9VhF",
    "uber-raw-data-jul14.csv":          "1-Jha8FsxMhvHo93_SOl6KNkjdVmXkzcC",
    "uber-raw-data-aug14.csv":          "1IWMQgs3vtjzEaU4RI_lONMhPFRGPmAZP",
    "uber-raw-data-sep14.csv":          "1TXjh6JV8M8xIoYgSa1jqK5q87YeK_kj8",

    # ── Uber Jan-Jun 2015 ──
    "uber-raw-data-janjune-15.csv":     "1PeFlACPt0TtKA73WiBgiTGZU1zUrXZ-R",

    # ── FOIL aggregate ──
    "Uber-Jan-Feb-FOIL.csv":            "1OjmkZu-fy6hxCRfNy6WebNK2vbpc6Rzf",

    # ── FHV summary ──
    "other-FHV-services_jan-aug-2015.csv": "15nsxdRJl1MxBJO4B3i1L4yh7NmRGq1Dg",

    # ── Other companies ──
    "other-Skyline_B00111.csv":         "1ZwGOInM5mY94KnNfM4gAYo_2o_esmkDQ",
    "other-Highclass_B01717.csv":       "1ZIe9WB7iiSS3QNXii68FvJDanxa8kBYE",
    "other-Federal_02216.csv":          "1qjW3mSYJwU9-fwoinpMrMwOOT8l7gZuy",
    "other-Carmel_B00256.csv":          "1HirbZK6Xnx8TVEJQX1S2jwFVN6IcLWwC",
    "other-Firstclass_B01536.csv":      "1iVxII-2Rwjy1znYSnePlvvM_H7lWE5oQ",
    "other-Prestige_B01338.csv":        "1jHEf_XzGc9qilsoYMp-CeMNtfuIK3MCl",
    "other-American_B01362.csv":        "11iGIVvitI7Nzz6mxmUDP2rToTFfHOwWB",
    "other-Lyft_B02510.csv":            "1L4PAeHUuH8NjQ_XaQgjjOZE64ynd5Nns",
    "other-Dial7_B00887.csv":           "1g93dDORWvpDRyomZssTFBy65411CstN8",
    "other-Diplo_B01196.csv":           "10c6SlgJzbDrRsXjNN7zLYVB3UDKEkx4t",
}


def download_from_drive(file_id: str, dest_path: str):
    """Download a single file from Google Drive by file ID."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
    print(f"  ⬇ Downloading {os.path.basename(dest_path)} ...")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    print(f"  ✓ Done: {os.path.basename(dest_path)}")


def ensure_data_folder(data_folder: str = "data/"):
    """Check every file — download from Drive if missing locally."""
    os.makedirs(data_folder, exist_ok=True)
    for filename, file_id in FILE_IDS.items():
        dest = os.path.join(data_folder, filename)
        if os.path.exists(dest):
            print(f"  ✓ {filename} already exists, skipping.")
            continue
        if file_id == "PASTE_ID_HERE":
            print(f"  ⚠️  {filename} — File ID not set, skipping.")
            continue
        download_from_drive(file_id, dest)


def load_data(data_folder="data/"):
    """Load all Uber raw pickup files and combine them."""
    ensure_data_folder(data_folder)

    uber_files = sorted(
        glob.glob(os.path.join(data_folder, "uber-raw-data-apr14.csv")) +
        glob.glob(os.path.join(data_folder, "uber-raw-data-may14.csv")) +
        glob.glob(os.path.join(data_folder, "uber-raw-data-jun14.csv")) +
        glob.glob(os.path.join(data_folder, "uber-raw-data-jul14.csv")) +
        glob.glob(os.path.join(data_folder, "uber-raw-data-aug14.csv")) +
        glob.glob(os.path.join(data_folder, "uber-raw-data-sep14.csv"))
    )

    dfs = []
    for f in uber_files:
        tmp = pd.read_csv(f)
        tmp.columns = ["DateTime", "Lat", "Lon", "Base"]
        tmp["source"] = "uber_2014"
        dfs.append(tmp)

    janjune = os.path.join(data_folder, "uber-raw-data-janjune-15.csv")
    if False:
        tmp = pd.read_csv(janjune, usecols=[0, 1, 2, 3], header=0, nrows=500000)
        tmp.columns = ["DateTime", "Lat", "Lon", "Base"]
        tmp["source"] = "uber_2015"
        dfs.append(tmp)

    df = pd.concat(dfs, ignore_index=True)

    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
    df.dropna(subset=["DateTime", "Lat", "Lon", "Base"], inplace=True)
    df = df[(df["Lat"] > 40.4) & (df["Lat"] < 41.0)]
    df = df[(df["Lon"] > -74.3) & (df["Lon"] < -73.6)]

    df["Date"]    = df["DateTime"].dt.date
    df["Month"]   = df["DateTime"].dt.month
    df["Year"]    = df["DateTime"].dt.year
    df["Hour"]    = df["DateTime"].dt.hour
    df["Weekday"] = df["DateTime"].dt.weekday
    day_names     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["DayName"] = df["Weekday"].map(lambda x: day_names[x])
    df["Week"]    = df["DateTime"].dt.isocalendar().week.astype(int)

    return df


def load_foil(data_folder="data/"):
    path = os.path.join(data_folder, "Uber-Jan-Feb-FOIL.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df.columns = ["Base", "Date", "ActiveVehicles", "Trips"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(inplace=True)
    return df


def load_fhv(data_folder="data/"):
    path = os.path.join(data_folder, "other-FHV-services_jan-aug-2015.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df.columns = ["BaseNumber", "BaseName", "PickupDate", "NumTrips", "NumVehicles"]
    df["PickupDate"] = pd.to_datetime(df["PickupDate"], errors="coerce")
    df["NumTrips"]    = pd.to_numeric(df["NumTrips"].astype(str).str.strip(), errors="coerce")
    df["NumVehicles"] = pd.to_numeric(df["NumVehicles"].astype(str).str.strip(), errors="coerce")
    df.dropna(inplace=True)
    return df


def load_other_bases(data_folder="data/"):
    files = glob.glob(os.path.join(data_folder, "other-*.csv"))
    files = [f for f in files if "FHV-services" not in f]

    dfs = []
    for f in files:
        try:
            tmp = pd.read_csv(f, usecols=[0, 1, 2], header=0,
                              names=["Date", "Time", "Address"], nrows=50000)
            company = os.path.basename(f).replace("other-", "").split("_")[0]
            tmp["Company"] = company
            dfs.append(tmp)
        except Exception:
            pass
    if not dfs:
        return None
    df = pd.concat(dfs, ignore_index=True)
    df["DateTime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str), errors="coerce")
    print("Columns:",df.columns.tolist())
    print(df[["Date","Time"]].head(5))
    df.dropna(subset=["DateTime"], inplace=True)
    df["Hour"]    = df["DateTime"].dt.hour
    df["Month"]   = df["DateTime"].dt.month
    df["Weekday"] = df["DateTime"].dt.weekday
    day_names     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["DayName"] = df["Weekday"].map(lambda x: day_names[x])
    return df


def apply_filters(df, months, base, hour_range, day, lat_range, year="All"):
    out = df.copy()
    if months:
        out = out[out["Month"].isin(months)]
    if base != "All":
        out = out[out["Base"] == base]
    out = out[(out["Hour"] >= hour_range[0]) & (out["Hour"] <= hour_range[1])]
    if day != "All":
        out = out[out["DayName"] == day]
    out = out[(out["Lat"] >= lat_range[0]) & (out["Lat"] <= lat_range[1])]
    if year != "All":
        out = out[out["Year"] == int(year)]
    return out
