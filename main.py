from utils import run_experiments, plot_experiment_results

if __name__ == "__main__":
    input_csv = "data/aisdk-2024-11-11.csv"

    # Chunk sizes and number of workers can be toggled for the experiment
    chunk_sizes = [500000]
    worker_list = [7, 8]

    df_results = run_experiments(input_csv, chunk_sizes, worker_list)
    print(df_results)
    df_results.to_csv("experiment_results.csv", index=False)

    plot_experiment_results(df_results)
