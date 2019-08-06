import pandas as pd
from pandas_ml import ConfusionMatrix
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

import cad_baseline as baseline
import cad_analysis as analysis

def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_directory", help="directory with the reference and prediction csv files")
    ap.add_argument("out_directory", help="directory to write the graphs")
    return ap


def global_visit_id(row):
    if pd.isnull(row["local_visit"]):
        return np.nan
    return "{}:{}:{}".format(row["session"], row["location"], row["local_visit"])

def build_reference_dataframe(reference_file, prediction_file):
    # predicated data
    #predicted_file = 'P3101-pred.csv'
    df_pred = pd.read_csv(prediction_file)
    df_pred.rename(index=str, columns={"animal":"animal_predicted"}, inplace=True)

    # reference data
    #reference_file = "P3101-ref.csv"
    df_ref = pd.read_csv(reference_file)
    df_ref.rename(index=str, columns={"label":"animal_reference"}, inplace=True)
    df_ref.loc[df_ref["animal_reference"] == "blank", "animal_reference"] = False
    df_ref.loc[df_ref["animal_reference"] == "animal", "animal_reference"] = True

    # merge the data frames
    df_merge = pd.merge(df_pred, df_ref)

    # create the reference id column
    combiner_func = lambda row: "{}:{}:{}".format(row["session"], row["location"], row["image"])
    df_merge["id"] = df_merge.apply(combiner_func, axis=1)

    # create the unique visit id
    df_merge.rename(index=str, columns={"visit":"local_visit"}, inplace=True)
    df_merge["visit"] = df_merge.apply(global_visit_id, axis=1)
    df_merge.drop(["local_visit"], axis=1, inplace=True)

    # remove locations and image columns
    # df_merge.drop(["location", "image"], axis=1, inplace=True)
    df_merge.drop(["image"], axis=1, inplace=True)

    return df_merge

def concat_dfs(dfs):
    df_all = pd.concat(dfs)
    # print(len(df_all.index))
    df_all.reset_index(drop=True, inplace=True)
    # print(len(df_all.index))
    return df_all

def get_locations_from_directory(directory):
    files = os.listdir(directory)
    locations = set()
    for f in files: 
        sess = f.split("-")[0]
        place = f.split("-")[1]
        location = "{}-{}".format(sess, place)
        locations.add(location)
    return locations

def build_location_dfs(locations):
    location_dfs = []
    for location in locations: 
        ref_csv = os.path.join(directory, location + "-ref.csv")
        pred_csv = os.path.join(directory, location + "-pred.csv")
        # print("reference file {}".format(ref_csv))
        # print("prediction file {}".format(pred_csv))

        # pull together all the data for this location
        location_dfs.append(build_reference_dataframe(ref_csv, pred_csv))
    return location_dfs

if __name__ == "__main__":
    # get locations from files in directory
    ap = construct_arg_parser()
    args = vars(ap.parse_args())
    directory = args["csv_directory"]
    out = args["out_directory"]

    locations = get_locations_from_directory(directory)
    location_dfs = build_location_dfs(locations)
    df_all = concat_dfs(location_dfs)

    baseline.baseline_info(df_all, out)
    analysis.assess_prediction(df_all)
