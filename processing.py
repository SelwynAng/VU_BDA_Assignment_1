import multiprocessing as mp
import pandas as pd
from tqdm import tqdm
from gps_spoofing_detection import find_location_anomalies, find_speed_course_anomalies, find_neighbour_conflict_anolmalies

CHUNK_SIZE_DEFAULT = 500000

def process_chunk(
    df_chunk: pd.DataFrame,
    timestamp_col: str = "# Timestamp",
    location_speed_threshold: float = 200,
    speed_diff_threshold: float = 5.0,
    bearing_diff_threshold: float = 30.0,
    time_window_minutes: float = 5.0,
    distance_threshold_km: float = 2.0,
    lat_lon_precision: int = 2
):
    df_chunk = df_chunk.dropna(subset=["Latitude", "Longitude"])
    df_chunk = df_chunk[(df_chunk["Latitude"].between(-90, 90)) & (df_chunk["Longitude"].between(-180, 180))]

    df_chunk[timestamp_col] = pd.to_datetime(df_chunk[timestamp_col], format="%m/%d/%Y %H:%M:%S", errors="coerce")
    df_chunk.dropna(subset=[timestamp_col], inplace=True)

    mmsi_groups = df_chunk.groupby("MMSI", group_keys=False)

    processed_groups = []
    location_anomalies_list = []
    speed_course_anomalies_list = []

    # Check for anomalies
    for _, vessel_df in mmsi_groups:
        updated_vessel_df, vessel_anolmaly_df = find_location_anomalies(vessel_df,timestamp_col,location_speed_threshold)
        if not vessel_anolmaly_df.empty:
            location_anomalies_list.append(vessel_anolmaly_df)
        
        updated_vessel_df2, speed_course_anom_df = find_speed_course_anomalies(updated_vessel_df, timestamp_col, speed_diff_threshold, bearing_diff_threshold)
        if not speed_course_anom_df.empty:
            speed_course_anomalies_list.append(speed_course_anom_df)

        processed_groups.append(updated_vessel_df)

    cleaned_chunk = pd.concat(processed_groups, ignore_index=True)
    
    # cross_vessel_anomalies_df = find_neighbour_conflict_anolmalies(cleaned_chunk, timestamp_col, time_window_minutes, distance_threshold_km, lat_lon_precision)
    
    all_anomalies = []
    if location_anomalies_list:
        all_anomalies.append(pd.concat(location_anomalies_list, ignore_index=True))
    if speed_course_anomalies_list:
        all_anomalies.append(pd.concat(speed_course_anomalies_list, ignore_index=True))
    # if not cross_vessel_anomalies_df.empty:
    #     all_anomalies.append(cross_vessel_anomalies_df)
    
    if all_anomalies:
        all_anomalies_df = pd.concat(all_anomalies, ignore_index=True)
        all_anomalies_df.drop_duplicates(inplace=True)
    else:
        all_anomalies_df = pd.DataFrame(columns=cleaned_chunk.columns)

    return cleaned_chunk, all_anomalies_df

def sequential_processing(input_csv, chunk_size=CHUNK_SIZE_DEFAULT):
    total_valid_df = []
    anomaly_df = []
    
    total_rows = sum(1 for row in open(input_csv)) - 1
    total_chunks = total_rows // chunk_size + 1
    
    with tqdm(total=total_chunks, unit='chunk', desc=f'Processing chunks sequentially with chunksize {chunk_size}') as pbar:
        for chunk in pd.read_csv(input_csv, chunksize=chunk_size):
            total_valid_chunk, anomaly_chunk = process_chunk(
                df_chunk=chunk,
                timestamp_col="# Timestamp",
                location_speed_threshold=200,
                speed_diff_threshold=5.0,
                bearing_diff_threshold=30.0,
                time_window_minutes=5.0,
                distance_threshold_km=2.0,
                lat_lon_precision=2
            )
            total_valid_df.append(total_valid_chunk)
            anomaly_df.append(anomaly_chunk)
            pbar.update(1)
    
    total_valid_df = pd.concat(total_valid_df, ignore_index=True)
    anomaly_df = pd.concat(anomaly_df, ignore_index=True)
    
    return total_valid_df, anomaly_df

def parallel_processing(input_csv, chunk_size=CHUNK_SIZE_DEFAULT, num_workers=None):
    if num_workers is None:
        num_workers = mp.cpu_count() - 1
    pool = mp.Pool(processes=num_workers)

    async_results = []
    
    total_rows = sum(1 for row in open(input_csv)) - 1
    total_chunks = total_rows // chunk_size + 1

    with tqdm(total=total_chunks, unit='chunk', desc=f'Processing chunks in parallel with chunksize {chunk_size} with {num_workers} workers') as pbar:
        for chunk in pd.read_csv(input_csv, chunksize=chunk_size):
            async_result = pool.apply_async(process_chunk, (chunk, "# Timestamp", 200, 5.0, 30.0, 2.0, 2))
            async_results.append(async_result)
            pbar.update(1)

    pool.close()
    pool.join()

    cleaned_data_frames, anomaly_data_frames = zip(*[r.get() for r in async_results])

    all_valid_df = pd.concat(cleaned_data_frames, ignore_index=True)
    all_anomaly_df = pd.concat(anomaly_data_frames, ignore_index=True)

    return all_valid_df, all_anomaly_df