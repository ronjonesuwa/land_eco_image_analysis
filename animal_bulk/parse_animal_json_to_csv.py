import json
import sys
import csv
import os
import argparse
from google.cloud import storage

def list_blobs_with_prefix(bucket_name, prefix, delimiter=""):
    """Lists all the blobs in the bucket that begin with the prefix."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

    out = []
    for blob in blobs:
        #uri_string = "gs://{}/{}".format(bucket_name, blob.name)
        out.append([bucket_name, blob.name])

    # the first element is the directory name, not a file
    # so exclude it from the file output

    return out[1:]

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

def extract_image_info(image_data):
    image_info = []
    image_name = os.path.basename(image_data["context"]["uri"])
    image_info.append(image_name)

    object_info = ["False","0"]
    if "localizedObjectAnnotations" in image_data.keys():
        for object_ in image_data["localizedObjectAnnotations"]:
            if object_["name"] == "Animal":
                object_info = ["True",object_["score"]]
    image_info.extend(object_info)

    return image_info

def write_new_csv(csv_file, headings):
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headings)

def append_csv(csv_file, data, location):
    with open(csv_file, "a", newline='') as f:
        writer = csv.writer(f)
        for datum in data:
            writer.writerow([location] + datum)

def parse_json_file(json_input):
    with open(json_input) as json_file:  
        data = json.load(json_file)

    # per image information
    images_info = []
    for datum in data['responses']:
        images_info.append(extract_image_info(datum))

    return images_info

def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket", help="bucket name without the gs:// prefix")
    ap.add_argument("source_directory", help="source directory on the bucket")
    ap.add_argument("json_target_directory", help="local target directory to write the json files")
    ap.add_argument("csv_file", help="csv file to write the data")
    ap.add_argument("location", help="location code")
    return ap

if __name__ == "__main__":
    ap = construct_arg_parser()
    args = vars(ap.parse_args())

    csv_file = args["csv_file"]
    target_dir = args["json_target_directory"]
    bucket = args["bucket"]
    src_dir = args["source_directory"]
    location = args["location"]

    # if csv doesn't exists create it
    if not os.path.exists(csv_file):
        write_new_csv(csv_file, ["location", "image", "animal", "confidence"])

    files = list_blobs_with_prefix(bucket, src_dir)
    for f in files:
        bucket = f[0]
        blob_name = f[1]
        file_name = os.path.basename(blob_name)
        dest_file = os.path.join(target_dir, file_name)

        print("Downloading and processing {}".format(file_name))
        download_blob(bucket, blob_name, dest_file)

        images_info = parse_json_file(dest_file)
        append_csv(csv_file, images_info, location)
 

  
