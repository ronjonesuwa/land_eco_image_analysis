import io
import os
import argparse
import shutil

from google.cloud import vision
from google.cloud import storage

def single_keywords(labels):
    keywords = ["coral", "reef"]
    for keyword in keywords:
        for label in labels:
            if (str.lower(label.description).find(keyword) != -1):
                return True
    return False

def multiple_keywords_2(labels):
    # look for combination of keywords
    target_label_sets = ["Organism", "Pattern"]
    # get the label descriptions in a list
    desc = []
    for label in labels:
        desc.append(label.description)
    # if the target_label isn't in the list return false
    for target_label in target_labels:
        if target_label not in desc:
            return False
    return True


def multiple_keywords_1(labels):
    # look for combination of keywords
    target_label_sets = ["Organism", "Colorfulness"]
    # get the label descriptions in a list
    desc = []
    for label in labels:
        desc.append(label.description)
    # if the target_label isn't in the list return false
    for target_label in target_labels:
        if target_label not in desc:
            return False
    return True

def coral_found(labels):
    if single_keywords(labels):
        return True
    # here if single keywords have not been found
    if multiple_keywords_1(labels):
        return True
    if multiple_keywords_1(labels):
        return True
    return False


def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--image-bucket", required=True, help="bucket with images")
    ap.add_argument("-s", "--source-directory", required=True, help="directory with source images")
    ap.add_argument("-o", "--organism-directory", required=True, help="organism image destination directory")
    ap.add_argument("-n", "--no-organism-directory", required=True, help="no organism image destination directory")
    return ap


def list_blobs_with_prefix(bucket_name, prefix, delimiter=""):
    """Lists all the blobs in the bucket that begin with the prefix."""

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

    out = []
    for blob in blobs:
        uri_string = "gs://{}/{}".format(bucket_name, blob.name)
        out.append([uri_string, bucket_name, blob.name])

    # the first element is the directory name, not a file
    # so exclude it from the file output

    return out[1:]


def move_image(bucket_name, blob_name, target_directory):
    filename = blob_name.split("/")[-1]
    target_path = target_directory + "/" + filename

#    image_file_name = os.path.basename(image_path)
#    full_target_path = os.path.join(target_directory, image_file_name)
#    shutil.move(image_path, full_target_path)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    new_blob = bucket.rename_blob(blob, target_path)


def process_image(image_details, organism_directory, no_organism_directory):
    print("Processing image {}".format(image_details[0]), end="")
    # Loads the image into memory
    # with io.open(image_path, 'rb') as image_file:
    #    content = image_file.read()

    # image = vision.types.Image(content=content)
    image = vision.types.Image()
    image_uri = image_details[0]
    image.source.image_uri = image_uri

    labels = client.label_detection(image=image).label_annotations

    if coral_found(labels):
        print("\tFound organism")
        move_image(image_details[1], image_details[2], organism_directory)
    else:
        print("\tNo organism found")
        move_image(image_details[1], image_details[2], no_organism_directory)

    output = []
    for label in labels:
        output.append(label.description)
    print(",".join(output))


# main script 
ap = construct_arg_parser()
args = vars(ap.parse_args())
# Instantiates a client
client = vision.ImageAnnotatorClient()

image_paths = list_blobs_with_prefix(args["image_bucket"], args["source_directory"])
for image_path in image_paths:
    process_image(image_path, args["organism_directory"], args["no_organism_directory"])