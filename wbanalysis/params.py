from google.oauth2.service_account import Credentials
import os

# Folder params
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

### GCP Storage - - - - - - - - - - - - - - - - - - - - - -
BUCKET_NAME = 'wb-analysis'

# Model.joblib file trained for pipeline
STORAGE_LOCATION = 'models'

DESTINATION_MODEL = f"{BASE_DIR}"

# credentials file
CREDENTIAL_FILE = f"{BASE_DIR}/credentials.json"
CREDENTIAL = Credentials.from_service_account_file(CREDENTIAL_FILE)

if __name__ == '__main__':

    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"BASE_DIR: {BASE_DIR}")
