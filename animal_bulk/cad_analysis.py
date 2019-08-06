
import pandas as pd
from pandas_ml import ConfusionMatrix
import numpy as np

def visit_animals(df, visit):
    """return the number of animals correctly predciated in session"""
    df_visit = df[df.visit == visit]
    return len(df_visit[df_visit.animal_predicted == True].index)

def metrics(df):
    """generate a standard set of metrics
    Columns in dataframe required:
    - animal_reference
    - animal_predicted
    - session
    """

    out = {}

    # counts
    out["images"] = len(df.index)
    out["animals_ref"] = len(df[df.animal_reference == True].index)
    out["blank_ref"] = len(df[df.animal_reference == False].index)
    out["animals_pred"] = len(df[df.animal_predicted == True].index)
    out["blank_pred"] = len(df[df.animal_predicted == False].index)

    # accuracy and precision
    cm = ConfusionMatrix(df.animal_reference.values, df.animal_predicted.values)
    out["true_positive"] = cm.TP
    out["false_positive"] = cm.FP
    out["true_negative"] = cm.TN
    out["false_negative"] = cm.FN

    #missed sessions
    visits = list(df.visit.unique())
    visits.remove(np.nan)
    out["visits"] = visits
    out["visits_recognised"] = {}
    for visit in visits: 
        out["visits_recognised"][visit] = (visit_animals(df, visit) > 0)

    return out

def analyse_metrics(metrics):
    out = {}
    # calculate sessions missed
    missed_visits = 0
    missed_visits_list = []
    for visit in metrics["visits_recognised"]:
        if not metrics["visits_recognised"][visit]:
            missed_visits+=1
            missed_visits_list.append(visit)
    out["missed_visits_count"] = missed_visits
    out["missed_visits"] = missed_visits_list
    
    # blanks removed
    blanks_removed = metrics["true_negative"]
    out["blanks_removed"] = blanks_removed

    # false blank
    false_blanks = metrics["false_negative"]
    out["false_blanks"] = false_blanks

    return out

def threshold_night_vertical_is_always_animal(df):
    # animal_predict is only true is animal_predict is True and confidence >= 0.6

    # apply threshold
    threshold = 0.6
    df = df.rename(index=str, columns={"animal_predicted":"animal_predicted_raw"})
    threshold_comparitor_func = lambda row: row["animal_predicted_raw"] and (row["confidence"] >= threshold)
    df["animal_predicted_threshold"] = df.apply(threshold_comparitor_func, axis=1)

    # apply night and camera orientation
    combiner_func = lambda row: row["night"] or (row["animal_predicted_threshold"] or row['location'][0] == "Q")
    df["animal_predicted"] = df.apply(combiner_func, axis=1)

    #return analyse_metrics("night",metrics(df))
    return df


def assess_prediction(df):
    df_assessed = threshold_night_vertical_is_always_animal(df)
    m = metrics(df_assessed)
    a = analyse_metrics(m)
    for item in a:
        print("{}:{}".format(item, a[item]))