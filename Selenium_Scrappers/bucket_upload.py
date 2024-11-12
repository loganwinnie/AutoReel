from google.cloud import storage


def upload_file_to_bucket(file, bucket):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob("/")

    blob.upload_from_filename(file)