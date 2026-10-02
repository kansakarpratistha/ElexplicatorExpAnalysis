import json
import pandas as pd

def getStepsPerProcess(deicisionsFile, costsFile, outputFile):
    #read from the json file - Example, Defect, count number of answers per option
    #df - would have columns - Example, Defect, Option1, Option2, Option3, Mix, User
    #save the df to a csv file
    df = pd.DataFrame(columns=["Example", "Defect", "option1", "option2", "option3", "mix", "user"])
    df_cost = pd.read_csv(costsFile, sep=";")
    with open(deicisionsFile, encoding="utf-8") as f:
        decisionsLog = json.load(f)

    for example, decisions in decisionsLog.items():
        for decision in decisions:  
            noRepair = False        
            defect = decision["Defect"]
            evaluations = decision["Evaluation"]
            decisions_dict = {"Example": example, "Defect": defect}
            for evaluation in evaluations:
                if evaluation["answersMap"]["Status"] != "Repair reached!":
                    noRepair = True
                    break
                if evaluation["cost"] == 0:
                    noRepair = True
                    break
                option = evaluation["optionName"]
                answers = evaluation["answersMap"]
                count_answers = len(answers)-1 # -1 to exclude the status
                decisions_dict[option] = count_answers
            if noRepair:
                continue
            df_dictionary = pd.DataFrame(decisions_dict, index=[0])
            df = pd.concat([df, df_dictionary], ignore_index=True)
    df = df.merge(df_cost, left_on=["Example", "Defect"], right_on=["Example", "Defect Axiom"], how="left", suffixes=("_steps", "_cost"))
    df = df[["Example", "Defect", "option1_steps", "option1_cost", "option2_steps", "option2_cost", "option3_steps", "option3_cost", "mix_steps", "mix_cost", "user_steps", "user_cost"]]
    
    df.to_csv(outputFile, index=False, sep=";")

def get_repairable_count(decisionsFile):
    with open(decisionsFile, encoding="utf-8") as jsonFile:
        decisionsLog = json.load(jsonFile)
    counter = 0
    for example, logs in decisionsLog.items():
        for log in logs:
            evaluations = log["Evaluation"]
            for eval in evaluations:
                if eval["answersMap"]["Status"] != "No selection!":
                    counter+=1
                    break;
    print(counter)

# for each example, defect, option, count the number of steps taken to reach a repair (_steps) and the number of attempts taken by the user to reach a repair (_attempts)
def steps_with_attempts(decisionsFile, costFile, outputFile):
    df = pd.DataFrame(columns=["Example", "Defect", "option1", "option2", "option3", "mix", "user"])
    df_cost = pd.read_csv(costFile, sep=";")
    with open(decisionsFile, encoding="utf-8") as f:
        decisionsLog = json.load(f)

    for example, decisions in decisionsLog.items():
        for decision in decisions:  
            defect = decision["Defect"]
            evaluations = decision["Evaluation"]
            decisions_dict = {"Example": example, "Defect": defect}
            for evaluation in evaluations:
                option = evaluation["optionName"]
                answers = evaluation["answersMap"]
                count_answers = len(answers)-1 # -1 to exclude the status
                decisions_dict[option] = count_answers
                if option == "user":
                    decisions_dict["user_attempts"] = evaluation["attempts"]

                if evaluation["cost"] == 0: #when status of out_of_memory (could be during cost evaluation), save  the steps as 0, so that it can be filtered out later
                    decisions_dict[count_answers] = 0 
            df_dictionary = pd.DataFrame(decisions_dict, index=[0])
            df = pd.concat([df, df_dictionary], ignore_index=True)
    df = df.merge(df_cost, left_on=["Example", "Defect"], right_on=["Example", "Defect Axiom"], how="left", suffixes=("_steps", "_cost"))
    df = df[["Example", "Defect", "option1_steps", "option1_cost", "option2_steps", "option2_cost", "option3_steps", "option3_cost", "mix_steps", "mix_cost", "user_steps", "user_cost", "user_attempts"]]
    
    df.to_csv(outputFile, index=False, sep=";")

def group_by_user_attempts(inputFile, outputFile):
    df = pd.read_csv(inputFile, sep=";")
    groups = df.groupby("user_attempts")
    for user_attempts, group in groups:
        group.to_csv(f"{outputFile.split('.')[0]}_{user_attempts}.csv", index=False, sep=";")

def pairwise_group_by_user_attempts(inputFile, outputFile):
    df = pd.read_csv(inputFile, sep=";")
    groups = df.groupby("user_attempts")
    for user_attempts, group in groups:
        if user_attempts == 0:
            continue
        pairwise_result_comparison(group, f"{outputFile}_attempt{user_attempts}")

def pairwise_steps_ungrouped(inputFile, outputFile):
    df = pd.read_csv(inputFile, sep=";")
    pairwise_result_comparison(df, outputFile)

def pairwise_result_comparison(inputDF, outputFile):
    options = ["option1", "option2", "option3", "mix", "user"]
    for i in range(len(options)-1):
        for j in range(i+1, len(options)):
            col1 = options[i]
            col2 = options[j]
            # df_clean = inputDF[~((inputDF[f"{col1}_steps"].isna()) | (inputDF[f"{col2}_steps"].isna()))]
            df_clean = inputDF[~((inputDF[f"{col1}_steps"] == 0.0) | (inputDF[f"{col2}_steps"] == 0.0) | (inputDF[f"{col1}_cost"].isna()) | (inputDF[f"{col2}_cost"].isna()))]
            df_clean = df_clean[["Example", "Defect", f"{col1}_steps",  f"{col1}_cost", f"{col2}_steps", f"{col2}_cost"]]
            df_clean[col1+"_better"] = df_clean.apply(lambda x: 1 if x[f"{col1}_steps"] < x[f"{col2}_steps"] else 0, axis=1)
            df_clean[col2+"_better"] = df_clean.apply(lambda x: 1 if x[f"{col2}_steps"] < x[f"{col1}_steps"] else 0, axis=1)
            df_clean.to_csv(outputFile+f"_{col1}_{col2}.csv", index=False, sep=";")
            print(f"Pairwise comparison for {col1} and {col2} saved to: {outputFile}_{col1}_{col2}.csv")

if __name__ == "__main__":
    decisionsFile = "plotExamples\\data\\decisions_unnormalized.json"
    outputFile = "plotExamples\\data\\decision_steps_unnormalized.csv"
    costsFile = "plotExamples\\processed_unnormalized\\rel_scaled_unnormalized.csv"
    steps_with_attempts(decisionsFile, costsFile, outputFile)
    pairwise_group_by_user_attempts(outputFile, "plotExamples\\processed_unnormalized\\steps_grouped\\steps_unnormalized")
    pairwise_steps_ungrouped(outputFile, "plotExamples\\processed_unnormalized\\steps_ungrouped\\steps_unnormalized")