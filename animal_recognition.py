import io
import os
import argparse
import shutil
from PIL import Image

# Imports the Google Cloud client library
from google.cloud import vision

def make_directory(directory):
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

def animal_found(objects, threshold):
    confidence_threshold = float(threshold) / 100
    for object_ in objects:
        print("\tObject:",object_.name)
        print("\tScore:",(float(object_.score)))
        if (object_.name == "Animal") and (float(object_.score) >= confidence_threshold):
           return True
    return False

def construct_arg_parser():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image-directory", required=True, help="image source directory")
	#ap.add_argument("-a", "--animal-directory", required=True, help="animal image destination directory")
	#ap.add_argument("-b", "--blank-directory", required=True, help="blank/no animal image destination directory")
	ap.add_argument("-g", "--greyscale", action="store_true", help="Flag to process it as greyscale")
	ap.add_argument("-t", "--threshold", help="Percentage threshold", type=int)
	return ap

def get_image_paths(directory):
    out = []
    images = os.listdir(directory)
    for image in images:
        image_path = os.path.join(directory, image)
        if os.path.isfile(image_path):
            out.append(image_path)
    return out

def move_image(image_path, target_directory):
    image_file_name = os.path.basename(image_path)
    full_target_path = os.path.join(target_directory, image_file_name)
    shutil.move(image_path, full_target_path)

def get_greyscale_image(image_path):
    img = Image.open(image_path).convert('L')
    temp_store = io.BytesIO()
    img.save(temp_store, format="JPEG")
    temp_store.seek(0)
    content=temp_store.read()
    return content

def get_standard_image(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    return content

def process_image(image_path, animal_directory, no_animal_directory, greyscale, threshold):
    print("Processing image {}".format(image_path))
    # Loads the image into memory
    # with io.open(image_path, 'rb') as image_file:
    #     content = image_file.read()

    if greyscale: 
        content = get_greyscale_image(image_path)
    else:
        content = get_standard_image(image_path)

    image = vision.types.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations

    # print('Number of objects found: {}'.format(len(objects)))
    # for object_ in objects:
    #     print('\n{} (confidence: {})'.format(object_.name, object_.score))
    #     print('Normalized bounding polygon vertices: ')
    #     for vertex in object_.bounding_poly.normalized_vertices:
    #         print(' - ({}, {})'.format(vertex.x, vertex.y))

    if animal_found(objects, threshold):
        print("\tFound animal")
        move_image(image_path, animal_directory)
    else:
        print("\tNo animal found")
        move_image(image_path, no_animal_directory)


###### main script 
ap = construct_arg_parser()
args = vars(ap.parse_args())
# Instantiates a client
client = vision.ImageAnnotatorClient()

image_paths = get_image_paths(args["image_directory"])
# make destination directories
blank_directory = (os.path.join(args["image_directory"],"blank"))
make_directory(blank_directory)
animal_directory = (os.path.join(args["image_directory"],"animal"))
make_directory(animal_directory)

# process images
for image_path in image_paths:
    process_image(image_path, animal_directory, blank_directory, args["greyscale"], args["threshold"])


# # The name of the image file to annotate
# file_name = os.path.join(
#     os.path.dirname(__file__), 'images/test2.JPG')
# process_image(file_name)