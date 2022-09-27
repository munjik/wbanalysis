from readline import get_current_history_length
from webbrowser import get
from google.cloud import storage
from google.cloud.storage import bucket
from google.resumable_media.requests import upload
from termcolor import colored
import pandas as pd
import joblib
import os
from .params import CREDENTIAL, DESTINATION_MODEL

BUCKET_NAME = "wb-analysis"  # BUCKET NAME
BUCKET_TRAIN_DATA_PATH = 'data/CompanyData.csv' #PATH


PROJECT_ID = "crypto-lodge-342802"
JOB_LOCATION = "us-west3"

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

def get_joblib():
    client = storage.Client(credentials=CREDENTIAL)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"models/model.joblib")
    blob.download_to_filename(f"{DESTINATION_MODEL}/model.joblib")
    print(colored("Model downloaded succesfully", "green"))
    model = joblib.load(f"{DESTINATION_MODEL}/model.joblib")
    return model

def upload_to_bq(df):
    print()
    print('To be uploaded')
    print(df.head())
    target_table = 'results.api'
    schema = [{
        'name': 'results',
        'type': 'float64'
    }, {
        'name': 'symbol',
        'type': 'STRING'
    }, {
        'name': 'GPM',
        'type': 'FLOAT64'
    }, {
        'name': 'A_SGA',
        'type': 'FLOAT64'
    }, {
        'name': 'B_RD',
        'type': 'FLOAT64'
    }, {
        'name': 'C_PPE',
        'type': 'FLOAT64'
    }, {
        'name': 'D_DEPR',
        'type': 'FLOAT64'
    }, {
        'name': 'E_CAPEX',
        'type': 'FLOAT64'
    }, {
        'name': 'F_NI_TR',
        'type': 'FLOAT64'
    }, {
        'name': 'G_NR_NI',
        'type': 'FLOAT64'
    }, {
        'name': 'H_currentRatio',
        'type': 'FLOAT64'
    }, {
        'name': 'I_ROA',
        'type': 'FLOAT64'
    }, {
        'name': 'J_LD_GP',
        'type': 'FLOAT64'
    }, {
        'name': 'K_debtToEquity',
        'type': 'FLOAT64'
    }, {
        'name': 'L_SD_LD',
        'type': 'FLOAT64'
    }, {
        'name': 'M_IN_OI',
        'type': 'FLOAT64'
    }, {
        'name': 'N_NetIssuance',
        'type': 'int64'
    }]
    if_exists_param = 'append'
    # Save df to GBQ,
    #  https://pandas-gbq.readthedocs.io/en/latest/writing.html
    # change to if_exists=append when in production
    df.to_gbq(target_table,
              project_id=PROJECT_ID,
              location=JOB_LOCATION,
              progress_bar=True,
              credentials=CREDENTIAL,
              table_schema=schema,
              if_exists=if_exists_param)

    print("Upload to BQ successful")
    return True


if __name__ == '__main__':
    # df = get_data_from_gcp()
    # print(df)
    #get_joblib()
    pass
