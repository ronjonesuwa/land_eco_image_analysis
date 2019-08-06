The bulk analysis of images iswas used to provide the data for comparision of different algorithms for distinguishing beteen images with and without animals. 

The steps to doing the bulk analysis are: 
1. Upload the images to process to a google bucket. 
    * The fastest way to do this is with the `gsutil` command
    * `gsutil -m cp <file-glob> <destination_directory>`
1. Batch process the images using the `animal_recognition_bulk.py` script
    * The command line paramaters are
        * bucket name without the "gs://" prefix
        * source directory : the directory on the bucket with the images to process
        * out directory : the directory on the bucket to write the json output files
    * n.b the google storage api treats directory names as prefix strings. 
        * For example if the source directory is called "image" and the output directory is called "image_out". When the script scans for all images in "bucket_name/image" the api will return the directory "bucket_name/image_out" and all the files inside it
1. Download all the jsons and combine the results into a csv with `parse_animal_json to_csv.py`
    * The command line parameters are
        * bucket name without the "gs://" prefix
        * source directory : the directory on the bucket with the json files
        * json target directory : The local directory to write the json files
        * csv file : the path (directory + filename) of the csv file to write the combined results to. The file name should end in "-pred.csv"
        * location : the location code where the images were taken
1. Parse the curated images using `make_curated_csv.py`
    * The curated images are the a copy of the images above split into a blank directory where the image has no animal in it, and an animal directory for images with an animal. Each visit of an animal is in its own sub-directory.
    * The command line parameters are
        * image directory with the curated images in it (assumed to be a local directory)
        * csv file : the path (directory + filename) of the csv file to write the results to. The file name should end in "-ref.csv"
        * location : the location code where the images were taken
1. The output csv files from previous steps should be put into the same directory
1. Combine the curated and processed images together and analysis the data using `combine_analysis_data.py`
    * The command line parameters are
        * directory with the curated and process csv files
        * out directory to write the graphs
    * The analysis will write a set of graphs to the out directory and output to stdout