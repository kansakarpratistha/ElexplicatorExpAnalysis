import pandas as pd
import numpy as np
import math


def partition_data(csv_file, output_dir, partition_size):
    df = pd.read_csv(csv_file, sep=",")
    max_value = df["Axiom Count"].max()
    min_value = df["Axiom Count"].min()
    # Always create integer boundaries
    bins=[
        0,
        105000,
        210000,
        315000,
        420000,
        525000,
        630000,
        735000,
        840000,
        # 1050000,
        # 1260000,
        # 1470000,
        # 1680000,
        1890000,
        3150000
    ]
    # partition_width = math.ceil((max_value + 1) / partition_size)

    # bins = [
    #     i * partition_width
    #     for i in range(partition_size + 1)
    # ]

    # Ensure the final bin covers max_value
    # bins[-1] = max_value + 1
    # labels = [
    #     f"{bins[i]}-{bins[i+1]-1}"
    #     for i in range(len(bins)-1)
    # ]
    labels = [
        "0-105K",
        "105K-210K",
        "210K-315K",
        "315K-420K",
        "420K-525K",
        "525K-630K",
        "630K-735K",
        "735K-840K",
        "840K-1.890M",
        "1.89M-3.15M"
    ]
    df_sorted = df.sort_values(by=["Axiom Count"]).reset_index(drop=True)

    df_sorted["partition"] = pd.cut(
        df_sorted["Axiom Count"],
        bins=bins,
        include_lowest=True,
        right=False,
        labels=labels
    )

    df_sorted = df_sorted[["partition", "example", "Axiom Count", "opt1 Average Runtime", "opt2 Average Runtime", "opt3 Average Runtime"]]
    return df_sorted

def handle_timeouts(df):
    # keep record of number of timeouts in each partition
    timeouts_dict = {}
    print(df.columns)
    for partition, data in df.groupby("partition"):
        opt1_timeouts = data[data["opt1 Average Runtime"] == 90001]
        opt2_timeouts = data[data["opt2 Average Runtime"] == 90001]
        opt3_timeouts = data[data["opt3 Average Runtime"] == 90001]
        timeouts_dict[partition] = {
            "opt1_timeouts": len(opt1_timeouts),
            "opt2_timeouts": len(opt2_timeouts),
            "opt3_timeouts": len(opt3_timeouts),
            }
    return timeouts_dict

def calculate_partition_means(df, output_directory):
    # mean of each column: opt1, opt2, opt3 for each partition without timeouts
    cols = ["opt1 Average Runtime", "opt2 Average Runtime", "opt3 Average Runtime"]
    opts = ["opt1", "opt2", "opt3"]
    df_no_timeouts = df.copy()
    df_no_timeouts[cols] = df_no_timeouts[cols].replace(90001, pd.NA)
    partition_means = df_no_timeouts.groupby("partition", as_index=False)[cols].mean()
    partition_means[cols] = partition_means[cols].fillna(90001)

    complete_runs = df_no_timeouts.groupby("partition", as_index=False)[cols].count()
    complete_runs = complete_runs.rename(columns={f"{opt} Average Runtime": f"{opt}_Complete_Runs" for opt in opts})
    print("Complete runs:")
    print(complete_runs)
    partition_means = pd.merge(partition_means, complete_runs, on="partition")

    timeouts = handle_timeouts(df)
    timeouts_df = pd.DataFrame.from_dict(timeouts, orient="index").reset_index().rename(columns={"index": "partition"})
    partition_means = pd.merge(partition_means, timeouts_df, on="partition")
    print(partition_means)
    partition_means = partition_means.rename(columns={f"{opt} Average Runtime": f"{opt}_Average_Runtime" for opt in opts})
    partition_means.to_csv(f"{output_directory}/benchmark.csv", index=False, sep=";")

def main():
    input_csv = "plotExamples\\data\\benchmarking_result.csv"
    output_directory = "plotExamples\\processed\\benchmark"
    partition_size = 15  # Number of partitions
    df_partitioned = partition_data(input_csv, output_directory, partition_size)
    # # handle_timeouts(df_partitioned)
    calculate_partition_means(df_partitioned, output_directory)

if __name__ == "__main__":
    main()