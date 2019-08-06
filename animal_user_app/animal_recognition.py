import io
import sys
import os
import argparse
import shutil
import PIL.Image
import PIL.ExifTags
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import _thread

class Window(tk.Frame):
    def __init__(self, action_do_analysis, action_get_key, master=None):
        tk.Frame.__init__(self, master)               
        self.master = master
        self.action_do_analysis = action_do_analysis
        self.action_get_key = action_get_key
        self.init_window()
    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget      
        self.master.title("Camera Trap Blank Remover")

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # create do analysis button instance
        get_key_button = tk.Button(self, text="Select google json key", command=self.action_get_key)

        # create do analysis button instance
        self.do_analysis_button = tk.Button(self, 
                                       text="Select folder with camera trap images",
                                       state=tk.DISABLED,
                                       command=self.action_do_analysis
                                      )
        #actionButton.place(x=0, y=0)
        
        quitButton = tk.Button(self, text="Quit",command=self.client_exit)

        self.text_box = tk.Text(root, height=2, width=30)
        self.update_text_box("Not processing")

        # placing the button on my window
        #quitButton.place(x=1, y=0)
        self.text_box.pack(side=tk.TOP)
        get_key_button.pack(side=tk.TOP)
        self.do_analysis_button.pack(side=tk.TOP)
        quitButton.pack(side=tk.TOP)

    def client_exit(self):
        sys.exit()

    def update_text_box(self, text):
        self.text_box.configure(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, text)
        self.text_box.configure(state=tk.DISABLED)

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

def make_directory(directory):
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

def animal_found(objects, threshold):
    confidence_threshold = float(threshold) / 100
    for object_ in objects:
        #print("\tObject:",object_.name)
        #print("\tScore:",(float(object_.score)))
        if (object_.name == "Animal") and (float(object_.score) >= confidence_threshold):
           return True
    return False

def construct_arg_parser():
	ap = argparse.ArgumentParser()
	ap.add_argument("image-directory", help="image source directory")
	#ap.add_argument("threshold", help="Percentage threshold", type=int)
	#ap.add_argument("-g", "--greyscale", action="store_true", help="Convert all images to greyscale before processing")
	#ap.add_argument("-n", "--night-auto-animal", action="store_true", help="Automatically categorise night images as animal")
	return ap

def get_image_paths(directory):
    out = []
    images = os.listdir(directory)
    for image in images:
        image_path = os.path.join(directory, image)
        if os.path.isfile(image_path):
            f_name, ext = os.path.splitext(image_path)
            if ext.lower() == ".jpg":
                out.append(image_path)
    return out

def move_image(image_path, target_directory):
    image_file_name = os.path.basename(image_path)
    full_target_path = os.path.join(target_directory, image_file_name)
    shutil.move(image_path, full_target_path)

def get_greyscale_image(image_path):
    img = PIL.Image.open(image_path).convert('L')
    temp_store = io.BytesIO()
    img.save(temp_store, format="JPEG")
    temp_store.seek(0)
    content=temp_store.read()
    return content

def get_standard_image(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    return content

def process_image(vision, client, image_path, animal_directory, no_animal_directory, greyscale, threshold, night_auto_animal):
    print("Processing image {}".format(image_path))

    if night_auto_animal:
        if is_night(image_path):
            move_image(image_path, animal_directory)
            return

    if greyscale: 
        content = get_greyscale_image(image_path)
    else:
        content = get_standard_image(image_path)

    image = vision.types.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations

    if animal_found(objects, threshold):
        move_image(image_path, animal_directory)
    else:
        move_image(image_path, no_animal_directory)
    return

def walk_directories(vision, client, top):
    for root, dirs, files in os.walk(top):
        # if in animal or blank directory don't process
        dir_name = os.path.basename(root)
        if (dir_name == "animal") or (dir_name == "blank"):
            continue

        # if in Q directory - don't process
        if dir_name[0] == "Q":
            continue

        image_paths = get_image_paths(root)
        if image_paths:
            blank_directory = (os.path.join(root,"blank"))
            make_directory(blank_directory)
            animal_directory = (os.path.join(root,"animal"))
            make_directory(animal_directory)

            # process images
            for image_path in image_paths:
                process_image(vision, client, image_path, animal_directory, blank_directory, False, 60, True)
    
    app.update_text_box("Not processing")
    messagebox.showinfo("Processing complete", "Processing of images is completed") 

def analyse_images():
    # Imports the Google Cloud client library
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    f = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select directory with images")
    if len(f) == 0:
        return
    res = messagebox.askokcancel("Prefilter images","Prefilter images in directory {}?".format(f))

    if res:
        app.update_text_box("Processing")
        _thread.start_new_thread(walk_directories, (vision, client, f))

def get_key():
    filename =  filedialog.askopenfilename(initialdir = "/",title = "Select google key file",filetypes = (("json files","*.json"),))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = filename
    app.do_analysis_button.configure(state=tk.NORMAL)

root = tk.Tk()
root.geometry("350x100")
app = Window(analyse_images, get_key, root)
root.mainloop()
