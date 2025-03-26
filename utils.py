import psutil
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt

from processing import parallel_processing, sequential_processing

def measure_resource_usage(func, *args, **kwargs):
    process = psutil.Process()
    
    cpu_usages = []
    mem_usages = []

    start_time = time.time()

    def monitor():
        while not done[0]:
            cpu_usages.append(psutil.cpu_percent(interval=0.1))
            mem_info = process.memory_info()
            mem_usages.append(mem_info.rss / (1024 * 1024))

    done = [False]
    
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.start()

    result = func(*args, **kwargs)

    end_time = time.time()
    done[0] = True
    monitor_thread.join()

    duration = end_time - start_time

    peak_cpu_percent = max(cpu_usages) if cpu_usages else 0
    peak_memory_MB = max(mem_usages) if mem_usages else 0

    return result, duration, peak_cpu_percent, peak_memory_MB

def run_experiments(input_csv, chunk_sizes, worker_list):
    results = []

    for c in chunk_sizes:
        (sq_result, sq_time, sq_cpu, sq_mem) = measure_resource_usage(sequential_processing, input_csv, c)
        sq_cleaned_df, sq_anomaly_df = sq_result
        
        for w in worker_list:
            (pl_result, pl_time, pl_cpu, pl_mem) = measure_resource_usage(parallel_processing, input_csv, c, w)
            pl_cleaned_df, pl_anomaly_df = pl_result

            speedup = sq_time / pl_time if pl_time > 0 else float('inf')

            results.append({
                "chunk_size": c,
                "num_workers": w,
                "time_sq": sq_time,
                "time_pl": pl_time,
                "speedup": speedup,
                "peak_cpu_sq": sq_cpu,
                "peak_cpu_pr": pl_cpu,
                "peak_mem_sq_MB": sq_mem,
                "peak_mem_pl_MB": pl_mem,
                "sq_total_valid_records": len(sq_cleaned_df),
                "sq_anomaly_records": len(sq_anomaly_df),
                "pl_total_valid_records": len(pl_cleaned_df),
                "pl_anomaly_records": len(pl_anomaly_df)
            })

    df_results = pd.DataFrame(results)
    return df_results

def plot_experiment_results(df_results):
    chunk_sizes = df_results["chunk_size"].unique()
    for c in chunk_sizes:
        subset = df_results[df_results["chunk_size"] == c]
        subset = subset.sort_values("num_workers")
        
        plt.plot(
            subset["num_workers"].values,
            subset["speedup"].values,
            marker='o',
            label=f"Chunk={c}"
        )

    plt.title("Speedup vs. Number of Workers for various chunk sizes")
    plt.xlabel("Number of Workers")
    plt.ylabel("Speedup (Sequential/Parallel)")
    plt.legend()
    plt.show()