from google.cloud import vision_v1
from google.cloud.vision_v1 import enums
from google.cloud import storage
import argparse

def construct_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket", help="bucket name without the gs:// prefix")
    ap.add_argument("source_directory", help="directory with the source images")
    ap.add_argument("out_directory", help="directory to write the output json files")
    return ap

def list_blobs_with_prefix(bucket_name, prefix, delimiter=""):
    """Lists all the blobs in the bucket that begin with the prefix."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)

    out = []
    for blob in blobs:
        uri_string = "gs://{}/{}".format(bucket_name, blob.name)
        out.append(uri_string)

    # the first element is the directory name, not a file
    # so exclude it from the file output

    return out[1:]

def sample_async_batch_annotate_images(input_image_uris, output_uri):
    """Perform async batch image annotation"""
    client = vision_v1.ImageAnnotatorClient()

    # set up output configuration
    gcs_destination = {'uri': output_uri}
    # The max number of responses to output in each JSON file
    batch_size = min(len(input_image_uris),100)
    output_config = {'gcs_destination': gcs_destination, 'batch_size': batch_size}

    # set up input configuration
    type_ = enums.Feature.Type.OBJECT_LOCALIZATION
    features_element = {'type': type_}
    features = [features_element]

    requests = []
    for input_image_uri in input_image_uris:
        source = {'image_uri': input_image_uri}
        image = {'source': source}
        requests.append({"image": image, "features": features})

    operation = client.async_batch_annotate_images(requests, output_config)

    print("Operation submitted with output file prefix", output_uri)

if __name__ == "__main__":
    ap = construct_arg_parser()
    args = vars(ap.parse_args())

    source_uris = list_blobs_with_prefix(args["bucket"], args["source_directory"])
    # chunk up the image paths into buffer sized chunks
    buffer_size = 1900
    source_uris_chunked = [source_uris[i:i + buffer_size] for i in range(0, len(source_uris), buffer_size)]

    target_uri_base = "gs://{}/{}/".format(args['bucket'], args['out_directory'])

    for count, chunk in enumerate(source_uris_chunked):
        target_uri = target_uri_base + str(count) + "-"
        sample_async_batch_annotate_images(chunk, target_uri)