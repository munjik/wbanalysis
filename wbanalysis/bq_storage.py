from dataclasses import replace

from wbanalysis.params import CREDENTIAL

PROJECT_ID ="crypto-lodge-342802"
JOB_LOCATION = "us-west3"

# Passed res from fast.py
def up_bq(df):
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
    if_exists_param = 'replace'
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
