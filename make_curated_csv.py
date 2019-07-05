import argparse
import os
import csv
import sys
import PIL.Image
import PIL.ExifTags

def is_night(image_path):
    # constants 
    maker_note_exif_tag = 37500
    infrared_status_byte = 80

    img = PIL.Image.open(image_path)
    maker_note = img._getexif()[maker_note_exif_tag]
    infrared_on = maker_note[infrared_status_byte] 
    if infrared_on == 0: 
        return False
    return True

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
    # return get_image_names(blank_directory)
    out = []
    for image_name in get_image_names(blank_directory):
        full_path = os.path.join(blank_directory, image_name)
        out.append( (image_name, full_path) )
    return out

def get_animal_images(directory):
    animal_directory = os.path.join(directory, "animal")
    subfolders = [(f.path, f.name) for f in os.scandir(animal_directory) if f.is_dir() ] 
    out = []
    for subfolder_path, session in subfolders:
        for name in get_image_names(subfolder_path):
            full_path = os.path.join(subfolder_path, name)
            out.append( (name, full_path, session) )
    return out

def write_csv(csv_file, blank_images, animal_images):
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        headings = ["image", "label", "session", "night"]
        writer.writerow(headings)
        for blank_image_name, blank_image_path in blank_images: 
            writer.writerow([blank_image_name, "blank", "", is_night(blank_image_path)])
        for animal_image_name, animal_image_path, session in animal_images: 
            writer.writerow([animal_image_name, "animal", session, is_night(animal_image_path)])

# make csv for the blank images
if __name__ == "__main__":
    ap = construct_arg_parser()
    args = vars(ap.parse_args())

    blank_images = get_blank_images(args["image_directory"])
    animal_images = get_animal_images(args["image_directory"])
    write_csv(args["csv_file"], blank_images, animal_images)

