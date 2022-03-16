from google.cloud import storage
from google.cloud.storage import bucket
from google.resumable_media.requests import upload
from termcolor import colored
import pandas as pd
import joblib
import os

BUCKET_NAME = "wb-analysis"  # BUCKET NAME
BUCKET_TRAIN_DATA_PATH = 'data/CompanyData-Data.csv' #PATH

# Load our data
def get_data_from_gcp(nrows=10000):
    path = f"gs://{BUCKET_NAME}/{BUCKET_TRAIN_DATA_PATH}"
    df = pd.read_csv(path, nrows=nrows)
    return df

#upload our model.joblib to the GCP
def storage_upload(bucket=BUCKET_NAME, rm=False):
    client = storage.Client().bucket(bucket)

    storage_location = '{}/{}'.format(
        'models',
        'model.joblib')
    blob = client.blob(storage_location)
    blob.upload_from_filename('model.joblib')
    print(colored("=> model.joblib uploaded to bucket {} inside {}".format(BUCKET_NAME, storage_location),
                  "green"))
    if rm:
        os.remove('model.joblib')

if __name__ == '__main__':
    # df = get_data_from_gcp()
    # print(df)
    pass
