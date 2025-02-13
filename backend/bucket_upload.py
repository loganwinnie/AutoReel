import os
import logging
from google.cloud import storage
from google.api_core.retry import Retry


def upload_downloaded_files(
    download_dir: str = "./video_downloads", 
    bucket_name: str = "yt-videos-bucket"
) -> list[str]:
    """
    Finds all files in `download_dir` and uploads them to the specified
    Google Cloud Storage bucket under the "videos/" prefix.

    :param download_dir: Path to the local directory containing files to upload.
    :param bucket_name: Name of the GCS bucket.
    :return: A list of file paths (GCS) that were successfully uploaded.
    """
    files = os.listdir(download_dir)
    uploads = []

    for file_name in files:
        try:
            uploaded_path = upload_file_to_bucket(
                file_name=file_name,
                bucket_name=bucket_name,
                local_dir=download_dir
            )
            uploads.append(uploaded_path)
        except Exception as ex:
            logging.error("Error uploading file '%s' to GCP: %s", file_name, ex)

    return uploads

def upload_file_to_bucket(
    file_name: str, 
    bucket_name: str, 
    local_dir: str = "./video_downloads",
    gcs_subdir: str = "videos",
    retry: Retry = Retry(deadline=300),
    timeout: int = 300
) -> str:
    """
    Upload a single file to the specified GCS bucket.

    :param file_name: Name of the local file.
    :param bucket_name: Name of the GCS bucket.
    :param local_dir: Path to the local directory containing the file.
    :param gcs_subdir: Subdirectory within GCS to store the file.
    :param retry: Optional Retry object.
    :param timeout: Timeout for the upload.
    :return: The full GCS path to the uploaded file.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_path = f"{gcs_subdir}/{file_name}"
    blob = bucket.blob(blob_path)

    local_path = os.path.join(local_dir, file_name)

    try:
        blob.upload_from_filename(local_path, retry=retry, timeout=timeout)
        os.remove(local_path)  # remove local file after successful upload
        gcs_path = f"gs://{bucket_name}/{blob_path}"
        return gcs_path
    except Exception as err:
        logging.error("Failed to upload file '%s': %s", local_path, err)
        raise