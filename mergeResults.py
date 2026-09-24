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
    df["min"] = df[options].min(axis=1, skipna=True)
    df["max"] = df[options].max(axis=1, skipna=True)
    for opt in options:
        df[opt] = df.apply(lambda row: (row[opt] - row["min"]) / (row["max"] - row["min"]) if not pd.isna(row[opt]) and row["max"] != row["min"] else 0, axis=1)
    df[["Example", "Defect Axiom"] + options].to_csv(output_file, index=False, sep=";")

def main():
    # relative_scaling_cost("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed\\rel_scaled_unnormalized.csv")
    # pairwise_result_comparison("plotExamples\\processed\\rel_scaled_unnormalized\\rel_scaled_unnormalized.csv", "plotExamples\\processed\\Scaled_unnormalized")
    # z_score_normalize("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed\\z_scaled_unnormalized\\z_scaled_unnormalized.csv")
    # pairwise_result_comparison("plotExamples\\processed\\z_scaled_unnormalized\\z_scaled_unnormalized.csv", "plotExamples\\processed\\z_scaled_unnormalized\\pairwise_z_scaled_unnormalized")
    # compute_deviation_from_original("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed\\dev_original_unnormalized\\deviation_original_unnormalized.csv")
    pairwise_result_comparison("plotExamples\\processed\\dev_original_unnormalized\\deviation_original_unnormalized.csv", "plotExamples\\processed\\dev_original_unnormalized\\pairwise_dev_original_unnormalized")
    # min_max_normalize("plotExamples\\data\\result_unnormalized.csv", "plotExamples\\processed\\minmax_scaled_unnormalized\\minmax_scaled_unnormalized.csv")
    # pairwise_result_comparison("plotExamples\\processed\\minmax_scaled_unnormalized\\minmax_scaled_unnormalized.csv", "plotExamples\\processed\\minmax_scaled_unnormalized\\pairwise_minmax_scaled_unnormalized")

main()

# # read from json file and a csv file.
# # map the examples in json file to the examples in csv file and add the respective defect attr from JSON to the CSV.
# def result_defect_mapping(json_file, csv_file, output_file):
#     with open(json_file, 'r') as decisionFile:
#         data = json.load(decisionFile)

#     onto_defect_mapping = dict()
#     for example, info in data.items():
#         defect = info.get("Defect")
#         onto_defect_mapping[example] = defect


#     defect_mapping_df = pd.DataFrame(list(onto_defect_mapping.items()), columns=["Example", "Defect Axiom"])


#     results_df = pd.read_csv(csv_file)

#     df_merged = results_df.merge(defect_mapping_df, left_on="Example", right_on="Example", how="inner")
#     df_merged.to_csv(output_file, index=False, sep=";")

# #join the unnormalized evaluation results and normalized-multdefect results on matching defect axioms.
# def join_on_defect_axioms(file1, file2, output_file):
#     df_unnormalized = pd.read_csv(file1)
#     df_normalized = pd.read_csv(file2, sep=";")
#     df_joined = df_unnormalized.merge(df_normalized, on=["Example", "Defect Axiom"], how="inner", suffixes=('_Unnormalized', '_Normalized'))
#     df_joined = df_joined[["Example", "Defect Axiom", "option1_Unnormalized", "option2_Unnormalized", "option3_Unnormalized", "mix_Unnormalized", "user_Unnormalized", "option1_Normalized", "option2_Normalized", "option3_Normalized", "mix_Normalized", "user_Normalized"]]
#     df_joined.to_csv(output_file, index=False, sep=";")
#     print("Joined on defect axioms and saved to: ", output_file)

# #concatenate the results csv files within the folders of folder
# def concatenate_results(input_folder, output_file):
#     all_files = [os.path.join(dir_path, f_name) for dir_path, dir_names, f_names in os.walk(input_folder) for f_name in f_names if f_name == 'result.csv']
#     print("All files to concatenate: ", len(all_files))
#     df_list = [pd.read_csv(file) for file in all_files]
#     concatenated_df = pd.concat(df_list, ignore_index=True)
#     #make defect axiom column as string type to avoid issues with merging later on.
#     concatenated_df["Defect Axiom"] = concatenated_df["Defect Axiom"].astype(str)
#     concatenated_df.to_csv(output_file, index=False, sep=";")

# # concatenate_results("../Logs_Multiple_Defects(VM3)", "../Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full.csv")
# # result_defect_mapping("..\\Logs_Unnormalized(VM1)\\merged_decisions_unnormalized_VM1.json", "..\\Logs_Unnormalized(VM1)\\Results.csv", "..\Logs_Unnormalized(VM1)\\Result_Unnormalized_Full.csv")
# # join_on_defect_axioms("..\\Logs_Unnormalized(VM1)\\Result_Unnormalized_Full.csv", "..\\Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full.csv", "plotExamples\\data\\Evaluation_Results_Comparison.csv")

# # concatenate_results("Logs_Multiple_Defects(VM3)", "Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full.csv")

# #log scaling evaluation results for option1, option2, option3, mix and user columns in the csv file and save the log-scaled results in a new csv file.
# def log_scale_results(input_file, output_file):
#     df = pd.read_csv(input_file, sep=";")
#     for col in ["option1", "option2", "option3", "mix", "user"]:
#         df[col] = df[col].apply(lambda x: np.log2(x) if x > 0 else 0)
#     df = df[["Example", "Defect Axiom", "option1", "option2", "option3", "mix", "user"]]
#     #datatype of Defect Axiom column should be string, convert it to string if it is not already.
#     df["Defect Axiom"] = df["Defect Axiom"].astype(str)
#     df.to_csv(output_file, index=False, sep=";")

# # log_scale_results("..\\Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full.csv", "plotExamples\\data\\Results_Multiple_Defects_Full_LogScaled.csv")

# # for each pair of options (log-scaled), if any of them has 0 values, discard that row and save the remaining rows to a new csv file.
# def handleTimeouts(input_file, output_file):
#     df = pd.read_csv(input_file, sep=";")
#     # for each pair of options, if any of them has 0 values, discard that row and save the remaining rows to a new csv file.
#     columns = ["option1", "option2", "option3", "mix", "user"]
#     print("Original number of rows: ", len(df))
#     for i in range(len(columns)-1):
#         for j in range(i+1, len(columns)):
#             col1 = columns[i]
#             col2 = columns[j]
#             df_clean = df[~((df[col1] == 0) | (df[col2] == 0))]
#             df_clean = df_clean[["Example", "Defect Axiom", col1, col2]]
#             print(f"Max value: {df_clean[[col1, col2]].max().max()}")
#             df_clean.to_csv(output_file+f"_{col1}_{col2}.csv", index=False, sep=";")

# # handleTimeouts("plotExamples\\data\\Results_Multiple_Defects_Full_LogScaled.csv", "plotExamples\\data\\Results_Multiple_Defects_NoTimeout")

# #rowise min-max normalization for option1, option2, option3, mix and user columns in the csv file and save the normalized results in a new csv file.
# def min_max_normalize(input_file, output_file):
#     df = pd.read_csv(input_file, sep=";")
#     for index, row in df.iterrows():
#         values = row[["option1", "option2", "option3", "mix", "user"]]
#         #for -1 values, set them to 0 for normalization
#         values = values.apply(lambda x: 0 if x == -1 else x)
#         min_val = values.min()
#         max_val = values.max()
#         if max_val > min_val:
#             #leave the 0 values as 0 after normalization, as they represent the cases where the option was not applicable or not selected.
#             values = values.apply(lambda x: 0 if x == 0 else (x - min_val) / (max_val - min_val))
#             df.loc[index, ["option1", "option2", "option3", "mix", "user"]] = values
#         else:
#             df.loc[index, ["option1", "option2", "option3", "mix", "user"]] = 0
#     df = df[["Example", "Defect Axiom", "option1", "option2", "option3", "mix", "user"]]
#     df.to_csv(output_file, index=False, sep=";")

# # min_max_normalize("Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full.csv", "Logs_Multiple_Defects(VM3)\\Results_Multiple_Defects_Full_MinMaxNormalized.csv")

# #compute deviation from mean for each options in the combined results and save to a new csv file.
# def compute_deviation_from_mean(input_file):
#     df = pd.read_csv(input_file, sep=";")

#     un_cols = ["option1_Unnormalized", "option2_Unnormalized", "option3_Unnormalized", "mix_Unnormalized", "user_Unnormalized"]
#     norm_cols = ["option1_Normalized", "option2_Normalized", "option3_Normalized", "mix_Normalized", "user_Normalized"]

#     # Replace invalid values
#     df[un_cols] = df[un_cols].replace([-1, 0], np.nan)
#     df[norm_cols] = df[norm_cols].replace([-1, 0], np.nan)

#     # Row-wise means exclude NaN values
#     df["mean_unnorm"] = df[un_cols].mean(axis=1, skipna=True)
#     df["mean_norm"] = df[norm_cols].mean(axis=1, skipna=True)

#     options = ["option1", "option2", "option3", "mix", "user"]

#     for opt in options:
#         un_col = f"{opt}_Unnormalized"
#         norm_col = f"{opt}_Normalized"

#         # Keep valid rows for this option
#         subset = df[df[un_col].notna() & df[norm_col].notna()].copy()

#         # Compute deviations
#         subset["dev_unnorm"] = ((subset[un_col] - subset["mean_unnorm"]).abs()/subset["mean_unnorm"])*100
#         subset["dev_norm"] = ((subset[norm_col] - subset["mean_norm"]).abs()/subset["mean_norm"])*100

#         # get single max value from norm and unnorm for this option and print it
#         max_dev_unnorm = subset["dev_unnorm"].max()
#         max_dev_norm = subset["dev_norm"].max()
#         print(f"Max deviation for {opt} - Unnormalized: {max_dev_unnorm}, Normalized: {max_dev_norm}")

#         subset[[norm_col, un_col, "mean_norm", "mean_unnorm", "dev_norm", "dev_unnorm"]] \
#             .to_csv(f"plotExamples\\data\\{opt}.csv", index=False, sep=";")
#     print("Deviation from mean computed and saved to respective csv files.")
# # compute_deviation_from_mean("plotExamples\\data\\Evaluation_Results_Comparison.csv")

# def min_max_normalize_full(input_file, output_file):
#     df = pd.read_csv(input_file, sep=";")
#     # for each row, get min and max values across all the options (option1, option2, option3, mix, user) for both unnormalized and normalized columns and apply min-max normalization using the row-wise min and max values.
#     un_cols = ["option1_Unnormalized", "option2_Unnormalized", "option3_Unnormalized", "mix_Unnormalized", "user_Unnormalized"]
#     norm_cols = ["option1_Normalized", "option2_Normalized", "option3_Normalized", "mix_Normalized", "user_Normalized"]

#     # Replace invalid values
#     df[un_cols] = df[un_cols].replace([-1, 0], np.nan)
#     df[norm_cols] = df[norm_cols].replace([-1, 0], np.nan)

#     # Row-wise min and max values across all options
#     df["min_unnorm"] = df[un_cols].min(axis=1, skipna=True)
#     df["max_unnorm"] = df[un_cols].max(axis=1, skipna=True)
#     df["min_norm"] = df[norm_cols].min(axis=1, skipna=True)
#     df["max_norm"] = df[norm_cols].max(axis=1, skipna=True)

#     options = ["option1", "option2", "option3", "mix", "user"]

#     for opt in options:
#         un_col = f"{opt}_Unnormalized"
#         norm_col = f"{opt}_Normalized"

#         # Keep valid rows for this option
#         subset = df[df[un_col].notna() & df[norm_col].notna()].copy()

#         # Compute deviations
#         subset["minmax_unnorm"] = subset.apply(lambda row: (row[un_col]-row["min_unnorm"])/(row["max_unnorm"]-row["min_unnorm"]) if row["max_unnorm"]-row["min_unnorm"] != 0 else 0.5, axis=1)
#         subset["minmax_norm"] = subset.apply(lambda row: (row[norm_col]-row["min_norm"])/(row["max_norm"]-row["min_norm"]) if row["max_norm"]-row["min_norm"] != 0 else 0.5, axis=1)

#         subset[["Example", "Defect Axiom", "minmax_norm", "minmax_unnorm"]].to_csv(f"plotExamples\\data\\{opt}_minmax_normalized.csv", index=False, sep=";")
#     print("Min-Max normalized values computed and saved to respective csv files.")
# # min_max_normalize_full("plotExamples\\data\\Evaluation_Results_Comparison.csv", "Evaluation_Results_MinMaxNormalized.csv")



# def relative_scaling(input_file, output_file):
#     df = pd.read_csv(input_file, sep=",")
#     # for each option, normalize it w.r.t the respective cost.get the max value across all the options (option1, option2, option3, mix, user) for both unnormalized and normalized columns and apply relative scaling by dividing each value by the row-wise max value.
#     options = ["option1", "option2", "option3", "mix", "user"]

#     # Replace invalid values
#     df[options] = df[options].replace([-1, 0], np.nan)
#     for opt in options:
#         df[f"relative_{opt}"] = df.apply(lambda row: row[opt]/row["Cost"] if not pd.isna(row[opt]) and row["Cost"] > 0 else 0, axis=1)
#     df[["Example", "Defect Axiom"] + [f"relative_{opt}" for opt in options]].to_csv(output_file, index=False, sep=";")
#     print("Relative scaling computed and saved to: ", output_file)

# relative_scaling("plotExamples\\ResultsNew\\ResultNormalized.csv", "plotExamples\\ResultsNew\\Normalized_RelScaled.csv")
    