import argparse
import csv

def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--reference-data-csv", required=True, help="csv file with reference data")
    ap.add_argument("-t", "--test-data-csv", required=True, help="csv file with test data")
    return ap

def read_csv(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        out = {}
        for row in reader:
            out[row["image"]] = row["label"]
    return out

def read_csv_session(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        out = {}
        for row in reader:
            if row["label"] == "animal":
                if row["session"] not in out.keys():
                    out[row["session"]] = []
                out[row["session"]].append(row["image"])
    return out

def read_csv_animals_only(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        out = []
        for row in reader:
            if row["label"] == "animal":
                out.append(row["image"])
    return out

def determine_confusion_matrix(ref_data, test_data):
    # go through keys in test set and compare categories with other set
    confusion_matrix_data = {}
    confusion_matrix_data['animal'] = {}
    confusion_matrix_data['animal']["animal"] = 0
    confusion_matrix_data['animal']["blank"] = 0
    confusion_matrix_data['blank'] = {}
    confusion_matrix_data['blank']["animal"] = 0
    confusion_matrix_data['blank']["blank"] = 0

    for key in test_data.keys():
        #print(test_data[key], ref_data[key])
        confusion_matrix_data[ref_data[key]][test_data[key]]+=1
    
    return confusion_matrix_data

def determine_session_matching(session_data, animals_data):
    out = {}
    found = False
    for key in session_data.keys():
        # check that at least one image in that category was detected as animal
        for image in session_data[key]:
            if image in detected_animals_data:
                found = True
                break
        out[key] = found
    return out


if __name__ == "__main__":
    ap = construct_arg_parser()
    args = vars(ap.parse_args())

    test_data = read_csv(args["test_data_csv"])
    ref_data = read_csv(args["reference_data_csv"])

    session_data = read_csv_session(args["reference_data_csv"])
    detected_animals_data = read_csv_animals_only(args["test_data_csv"])

    if len(test_data) != len(ref_data):
        print("Datasets are not the same")
        exit()

    confusion_matrix_data = determine_confusion_matrix(ref_data, test_data)
    print(confusion_matrix_data)

    session_match = determine_session_matching(session_data, detected_animals_data)
    print(session_match)