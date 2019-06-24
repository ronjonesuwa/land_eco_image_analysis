import io
import os
import argparse
import shutil

from google.cloud import vision

def animal_found(objects):
    for object_ in objects:
        if object_.name == "Animal":
           return True
    return False

def construct_arg_parser():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image-directory", required=True, help="image source directory")
	ap.add_argument("-a", "--animal-directory", required=True, help="animal image destination directory")
	ap.add_argument("-b", "--blank-directory", required=True, help="blank/no animal image destination directory")
	return ap

def get_image_paths(directory):
	out = []
	images = os.listdir(directory)
	for image in images:
		out.append(os.path.join(directory, image))
	return out

def move_image(image_path, target_directory):
    image_file_name = os.path.basename(image_path)
    full_target_path = os.path.join(target_directory, image_file_name)
    shutil.move(image_path, full_target_path)

def process_image(image_path, animal_directory, no_animal_directory):
    print("Processing image {}".format(image_path), end="")
    # Loads the image into memory
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations


    if animal_found(objects):
        print("\tFound animal")
        move_image(image_path, animal_directory)
    else:
        print("\tNo animal found")
        move_image(image_path, no_animal_directory)

# def get_bound_box_information(objects):
    # print('Number of objects found: {}'.format(len(objects)))
    # for object_ in objects:
    #     print('\n{} (confidence: {})'.format(object_.name, object_.score))
    #     print('Normalized bounding polygon vertices: ')
    #     for vertex in object_.bounding_poly.normalized_vertices:
    #         print(' - ({}, {})'.format(vertex.x, vertex.y))

###### main script 
ap = construct_arg_parser()
args = vars(ap.parse_args())
# Instantiates a client
client = vision.ImageAnnotatorClient()

image_paths = get_image_paths(args["image_directory"])
for image_path in image_paths:
    process_image(image_path, args["animal_directory"], args["blank_directory"])