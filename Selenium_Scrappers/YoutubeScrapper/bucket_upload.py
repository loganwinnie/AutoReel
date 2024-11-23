from google.cloud import storage
from google.api_core.retry import Retry
import os

def upload_downloaded_files():
    files = os.listdir("./video_downloads")
    for file in files:
        upload_file_to_bucket(file=file,bucket="yt-videos-bucket")


def upload_file_to_bucket(file, bucket):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(f"videos/{file}")

    retry = Retry(deadline=300) 
    timeout = 300 
    file_path = f"./video_downloads/{file}"
    try:
        blob.upload_from_filename(file_path, retry=retry, timeout=timeout)
        os.remove(file_path)
    except Exception as err:
        print("Error uploading file to GCP")
        if "message" in err:
            print(err.message)


