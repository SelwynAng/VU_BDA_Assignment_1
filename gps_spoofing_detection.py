import pandas as pd
import numpy as np

def hs_distance(lat1, lon1, lat2, lon2):
    radius = 6371
    lat_diff = np.radians(lat2 - lat1)
    lon_diff = np.radians(lon2 - lon1)
    a = (np.sin(lat_diff / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(lon_diff / 2) ** 2)
    c = np.arcsin(np.sqrt(a)) * 2

    return radius * c

def find_location_anomalies(
    vessel_df: pd.DataFrame,
    timestamp_col: str = "# Timestamp",
    speed_threshold: float = 200
):
    vessel_df = vessel_df.sort_values(timestamp_col).copy()

    vessel_df["lat_shift"] = vessel_df["Latitude"].shift()
    vessel_df["lon_shift"] = vessel_df["Longitude"].shift()
    vessel_df["time_shift"] = vessel_df[timestamp_col].shift()

    vessel_df["dist_km"] = hs_distance(
        vessel_df["Latitude"], vessel_df["Longitude"],
        vessel_df["lat_shift"], vessel_df["lon_shift"]
    )

    vessel_df["time_diff_hr"] = (
        vessel_df[timestamp_col] - vessel_df["time_shift"]
    ).dt.total_seconds() / 3600.0

    vessel_df["speed_kmh"] = vessel_df["dist_km"] / vessel_df["time_diff_hr"]
    vessel_df.loc[vessel_df["time_diff_hr"] == 0, "speed_kmh"] = 0.0

    condition = (vessel_df["speed_kmh"] > speed_threshold)
    anolmaly_rows_df = vessel_df[condition].copy()

    return vessel_df, anolmaly_rows_df

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    lon_rad_diff = np.radians(lon2 - lon1)

    x = np.sin(lon_rad_diff) * np.cos(lat2_rad)
    y = (np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(lon_rad_diff))
    
    bearing = np.degrees(np.arctan2(x, y))
    bearing = (bearing + 360) % 360
    
    return bearing

def find_speed_course_anomalies(
    vessel_df: pd.DataFrame,
    timestamp_col: str = "# Timestamp",
    speed_diff_threshold: float = 5.0,
    bearing_diff_threshold: float = 30.0
):
    df = vessel_df.copy()
    
    if "SOG" not in df.columns:
        df["SOG"] = 0.0
    if "COG" not in df.columns:
        df["COG"] = 0.0

    df["speed_diff"] = (df["speed_kmh"] - df["SOG"]).abs()

    df = df.sort_values(timestamp_col)
    df["lat_shift2"] = df["Latitude"].shift()
    df["lon_shift2"] = df["Longitude"].shift()
    df["computed_bearing"] = calculate_bearing(df["lat_shift2"], df["lon_shift2"], df["Latitude"], df["Longitude"])
    df["bearing_diff"] = (df["computed_bearing"] - df["COG"]).abs()
    df["bearing_diff"] = df["bearing_diff"].apply(lambda x: min(x, 360 - x))

    condition = (df["speed_diff"] > speed_diff_threshold) | (df["bearing_diff"] > bearing_diff_threshold)
    anomaly_rows_df = df[condition].copy()

    return df, anomaly_rows_df


def find_neighbour_conflict_anolmalies(
    chunk_df: pd.DataFrame,
    timestamp_col: str = "# Timestamp",
    time_window_minutes: float = 5.0,
    distance_threshold_km: float = 2.0,
    lat_lon_precision: int = 2
):
    df = chunk_df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
    df.dropna(subset=[timestamp_col], inplace=True)

    df["lat_bin"] = df["Latitude"].round(lat_lon_precision)
    df["lon_bin"] = df["Longitude"].round(lat_lon_precision)

    bin_size_seconds = time_window_minutes * 60
    t0 = df[timestamp_col].min()
    df["time_bin"] = ((df[timestamp_col] - t0).dt.total_seconds() // bin_size_seconds).astype(int)

    anolmalous_pairs = []

    grouped = df.groupby(["lat_bin", "lon_bin", "time_bin"], group_keys=False)
    for (latb, lonb, tb), group_df in grouped:
        n = len(group_df)
        if n <= 1:
            continue
        rows = group_df.to_dict("records")
        for i in range(n):
            row_i = rows[i]
            for j in range(i+1, n):
                row_j = rows[j]
                if row_i["MMSI"] == row_j["MMSI"]:
                    continue
                dist_km = hs_distance(
                    row_i["Latitude"], row_i["Longitude"],
                    row_j["Latitude"], row_j["Longitude"]
                )
                if dist_km < distance_threshold_km:
                    anolmalous_pairs.append(row_i)
                    anolmalous_pairs.append(row_j)


    conflicts_df = pd.DataFrame(anolmalous_pairs).drop_duplicates()
    return conflicts_df