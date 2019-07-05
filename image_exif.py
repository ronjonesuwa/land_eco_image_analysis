import io
import os
import argparse
import shutil
import PIL.Image
import PIL.ExifTags

# number of byte in a single field
PC900_wordsize = 2
# fields indices as defined at http://owl.phy.queensu.ca/~phil/exiftool/TagNames/Reconyx.html
PC900_tags = {"MakerNoteVersion":(0,1),
              "FirmwareVersion":(1,4),
              "FirmwareDate":(4,6),
              "TriggerMode":(6,7),
              "Sequence":(7,9),
              "EventNumber":(9,11),
              "DataTimeOriginal":(11,18),
              "MoonPhase":(18,19),
              "AmbientTermperatureFahrenheit":(19,20),
              "AmbientTermperature":(20,21),
              "SerialNumber":(21,36),
              "Contrast":(36,37),
              "Brightness":(37,38),
              "Sharpness":(38,39),
              "Saturation":(39,40),
              "InfraredIlluminator":(40,41),
              "MotionSensitivity":(41,42),
              "BatteryVoltage":(42,43),
              "UserLabel":(43,64)
             }

def construct_arg_parser():
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required=True, help="image to process")
	return ap

###### main script 
ap = construct_arg_parser()
args = vars(ap.parse_args())
# Instantiates a client

img = PIL.Image.open(args["image"])
# map the Exif tags to field names
exif = {
    PIL.ExifTags.TAGS[k]: k
    for k, v in img._getexif().items()
    if k in PIL.ExifTags.TAGS
}
print(exif)
# mnotes = exif['MakerNote']
# for tag in PC900_tags:
#     field_bounds = PC900_tags[tag]
#     slice_bounds = (field_bounds[0]*PC900_wordsize, field_bounds[1]*PC900_wordsize)
#     field = mnotes[slice_bounds[0]:slice_bounds[1]]
#     print(tag, field)
