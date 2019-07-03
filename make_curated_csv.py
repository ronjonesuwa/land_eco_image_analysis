import argparse
import os
import csv
import sys

def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image-directory", required=True, help="image source directory")
    ap.add_argument("-c", "--csv-file", required=True, help="csv file to write to")
    return ap

def get_image_names(directory):
    images = os.listdir(directory)
    return sorted(images)

def get_blank_images(directory):
    blank_directory = os.path.join(directory, "blank")
    return get_image_names(blank_directory)

def get_animal_images(directory):
    animal_directory = os.path.join(directory, "animal")
    subfolders = [(f.path, f.name) for f in os.scandir(animal_directory) if f.is_dir() ] 
    out = []
    for subfolder_path, session in subfolders:
        for name in get_image_names(subfolder_path):
            out.append( (name, session) )
    return out

def write_csv(csv_file, blank_images, animal_images):
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        headings = ["image", "label", "session"]
        writer.writerow(headings)
        for blank_image in blank_images: 
            writer.writerow([blank_image, "blank", ""])
        for animal_image, session in animal_images: 
            writer.writerow([animal_image, "animal", session])


# make csv for the blank images
if __name__ == "__main__":
    ap = construct_arg_parser()
    args = vars(ap.parse_args())

    #print(get_animal_images(args["image_directory"]))
    blank_images = get_blank_images(args["image_directory"])
    animal_images = get_animal_images(args["image_directory"])
    write_csv(args["csv_file"], blank_images, animal_images)

