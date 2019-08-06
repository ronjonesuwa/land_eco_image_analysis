# Identify camera trap images with no animals (blanks)

The instructions below describe: 
* How to set up the standalone package
* How to run the script


## Build the standalone package

Use pyinstaller to create the standalone package. 

1. Install pyinstaller using pip
    * `pip install pyinstaller`

1. Set the location of the missing files in the `build.bat` file
    * pyinstaller misses the `roots.pem` file in the grpc module and that files must be included manually
    * `roots.pem` is in the `grpc` module in the python `site-packages` directory
    * The first line in the `build.bat` file specifies the location of `roots.pem` file

1. Run the pyinstaller packager
    * Run the `build.bat` file
    * The output executable will be in the `dist` directory

## Run the executable
1. Select the json key
    * This key is generated previously from the cloud dashboard or via the cloud api

1. Select the directory with images in it
1. Press ok
1. The images will be categorised
