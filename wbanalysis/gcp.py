from google.cloud import storage
from google.cloud.storage import bucket
from google.resumable_media.requests import upload
from termcolor import colored
import pandas as pd
import joblib
import os

BUCKET_NAME = "wb-analysis"  # BUCKET NAME
MODEL_NAME = "warren_buffett" #MODEL NAME
STORAGE_LOCATION = 'model/warren_buffet/versions/' # STORAGE LOCATION

#upload our model.joblib to the GCP
def upload_model_to_gcp(model_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(STORAGE_LOCATION)
    blob.upload_from_filename(model_name)
    print('Success!')
if __name__ == '__main__':
    upload_model_to_gcp('model.joblib')
