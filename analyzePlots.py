import pandas as pd
#from the plots, get the data that have very similar scores and evaluate the steps taken by the users for those examples.

def getStepsForSimilarScores(csvFile, scoreThreshold):
    #scores greater than 9 all converge to the diagonal
    df = pd.read_csv(csvFile, sep=";")
    df_steps = pd.read_csv("plotExamples\\data\\Evaluation_Steps_Norm.csv", sep=";")
    #filter the df to get the examples where the scores are similar
    df.rename(columns={"Defect Axiom": "Defect"}, inplace=True)
    print(df.head())
    df_similar = df[(df["option1"] >= scoreThreshold) & (df["option2"] >= scoreThreshold) & (df["option3"] >= scoreThreshold) & (df["mix"] >= scoreThreshold) & (df["user"] >= scoreThreshold+1)]

    #merge the similar examples with the steps data
    df_result = pd.merge(df_similar, df_steps, on=["Example", "Defect"], how="inner", suffixes=('_score', '_steps'))
    df_result.to_csv("plotExamples\\data\\Similar_Scores_Steps.csv", index=False, sep=";")
    return None

if __name__ == "__main__":
    csvFile = "plotExamples\\data\\Results_Multiple_Defects_Full_LogScaled.csv"
    scoreThreshold = 9
    getStepsForSimilarScores(csvFile, scoreThreshold)