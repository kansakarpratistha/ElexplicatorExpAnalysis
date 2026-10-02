import json
import os
import pandas as pd
import numpy as np
import sklearn.preprocessing as preprocessing

#scale the results relative to original cost.
def relative_scaling_cost(input_file, output_file):
    original_df = pd.read_csv(input_file)
    print("Original number of rows: ", len(original_df))
    columns = ["option1", "option2", "option3", "mix", "user"]
    print(original_df.head())
    original_df[columns] = original_df[columns].replace([-1], np.nan)
    original_df[columns] = original_df[columns].replace([0], np.nan)
    # Perform relative scaling, if -1 values are present, keep them as -1, else divide by cost.
    for col in columns:
        original_df[col] = original_df.apply(
            lambda x: x[col] if np.isnan(x[col]) or x["Cost"] == 0 else x[col] / x["Cost"],
            axis=1
        )
        print(original_df[[col, "Cost"]].head())

    original_df.to_csv(output_file, index=False, sep=";")
    print("Relative scaling w.r.t cost computed and saved to: ", output_file)


#pairwise result comparison for each pair of options (option1, option2, option3, mix, user) in the csv file and save the results in a new csv file.
def pairwise_result_comparison(input_file, output_file):
    df = pd.read_csv(input_file, sep=";")
    columns = ["option1", "option2", "option3", "mix", "user"]
    for i in range(len(columns)-1):
        for j in range(i+1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]
            df_clean = df[~((df[col1].isna()) | (df[col2].isna()))]
            df_clean = df_clean[["Example", "Defect Axiom", col1, col2]]
            df_clean[col1+"_better"] = df_clean.apply(lambda x: 1 if x[col1] < x[col2] else 0, axis=1)
            df_clean[col2+"_better"] = df_clean.apply(lambda x: 1 if x[col2] < x[col1] else 0, axis=1)
            df_clean.to_csv(output_file+f"_{col1}_{col2}.csv", index=False, sep=";")
            print(f"Pairwise comparison for {col1} and {col2} saved to: {output_file}_{col1}_{col2}.csv")


def z_score_normalize(input_file, output_file):
    df = pd.read_csv(input_file, sep=",")

    options = ["option1", "option2", "option3", "mix", "user"]

    df[options] = df[options].replace([-1], np.nan)
    df[options] = df[options].replace([0], np.nan)
    df["mean"] = df[options].mean(axis=1, skipna=True)
    df["std"] = df[options].std(axis=1, skipna=True, ddof=0)  # Use population standard deviation

    for opt in options:

        # Compute z-scores. For cases where std is 0, set z-score to 0 to avoid division by zero, as all values are the same in that case, if the value is nan, set z-score as nan as well.
        df[opt] = df.apply(lambda row: (row[opt] - row["mean"])/row["std"] if row["std"] > 0 and not pd.isna(row[opt]) else (0 if not pd.isna(row[opt]) else np.nan), axis=1)

    df[["Example", "Defect Axiom"] + options].to_csv(output_file, index=False, sep=";")
    print("Z-score normalized values computed and saved to respective csv files.")

#compute deviation from original for each options in the combined results and save to a new csv file.
def compute_deviation_from_original(input_file, output_file):
    df = pd.read_csv(input_file, sep=",")

    options = ["option1", "option2", "option3", "mix", "user"]

    df[options] = df[options].replace([-1], np.nan)
    df[options] = df[options].replace([0], np.nan)
    for opt in options:
        # Compute deviations
        df[opt] = df.apply(lambda row: abs(row[opt] - row["Cost"])/row["Cost"]*100 if (not pd.isna(row[opt]) and row["Cost"] != 0) else np.nan, axis=1)

    df[["Example", "Defect Axiom"] + options].to_csv(output_file, index=False, sep=";")
    print("Deviation from original computed and saved to respective csv files.")

# #rowise min-max normalization for option1, option2, option3, mix and user columns in the csv file and save the normalized results in a new csv file.
def min_max_normalize(input_file, output_file):
    df = pd.read_csv(input_file, sep=",")
    options = ["option1", "option2", "option3", "mix", "user"]
    df[options] = df[options].replace([-1], np.nan)
    df[options] = df[options].replace([0], np.nan)
    df["min"] = df[options].min(axis=1, skipna=True)
    df["max"] = df[options].max(axis=1, skipna=True)
    for opt in options:
        df[opt] = df.apply(lambda row: (row[opt] - row["min"]) / (row["max"] - row["min"]) if not pd.isna(row[opt]) and row["max"] != row["min"] else 0, axis=1)
    df[["Example", "Defect Axiom"] + options].to_csv(output_file, index=False, sep=";")

def main():
    relative_scaling_cost("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed_unnormalized\\rel_scaled_unnormalized.csv")
    pairwise_result_comparison("plotExamples\\processed_unnormalized\\rel_scaled_unnormalized.csv", "plotExamples\\processed_unnormalized\\pairwise_rel_scaled_unnormalized")
    z_score_normalize("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed_unnormalized\\z_scaled_unnormalized.csv")
    pairwise_result_comparison("plotExamples\\processed_unnormalized\\z_scaled_unnormalized.csv", "plotExamples\\processed_unnormalized\\pairwise_z_scaled_unnormalized")
    compute_deviation_from_original("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed_unnormalized\\deviation_original_unnormalized.csv")
    pairwise_result_comparison("plotExamples\\processed_unnormalized\\deviation_original_unnormalized.csv", "plotExamples\\processed_unnormalized\\pairwise_deviation_original_unnormalized")
    min_max_normalize("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed_unnormalized\\minmax_scaled_unnormalized.csv")
    pairwise_result_comparison("plotExamples\\processed_unnormalized\\minmax_scaled_unnormalized.csv", "plotExamples\\processed_unnormalized\\pairwise_minmax_scaled_unnormalized")

main()
