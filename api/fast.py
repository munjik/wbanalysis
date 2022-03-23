from webbrowser import get
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import http3
import pandas as pd

app = FastAPI()
client = http3.AsyncClient()
base_url = 'https://financialmodelingprep.com'
api_key = 'apikey=3845af5c988287d80bbe6a9e83d56c30'

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # Allow all origins
    allow_credentials=True,
    allow_methods=['*'], # Allow all methods
    allow_headers=['*'], # Allow all headers
)


async def call_api(url: str):
    r = await client.get(url)
    return r.json()

# define a root '/' endpoint
@app.get("/")
def api_root():
    return {"Please provide a query"}

@app.get("/predict/{symbol}")
async def predict(symbol):
    # balance sheet statement
    params = f'/api/v3/balance-sheet-statement/{symbol}?limit=120&'
    try:
        res1 = await call_api(base_url + params + api_key)
        # return {"res": res1}
    except:
        return {"error"}
    """ Procedure:
        1.) Grab our values from the .JSON store it in X variable
        2.) Create another variable with the list of column names
        3.) Zip these two to form a Dict, then assign the dict as a DataFrame -> dict(zip(a, b))
        4.) Feed the joblib file with the newly dataframe
        5.) Create a prediction
        """
    # Grab our values from the .JSON store it in X variable
    X = {res1[0]['calendarYear'],
         res1[0]['longTermInvestments']
         }
    # Create another variable with the list of column names
    colimn_names = ["calendarYear",
                "GPM",
                "A (SGA)",
                "B (RD)",
                "C (PPE)",
                "D (DEPR)",
                "E (CAPEX)",
                "F (NR)",
                "currentRatio",
                "G (ROA)",
                "H (LD/GP)",
                "debtToEquity",
                "Net Issuance",
                "Interest - income"]
    return colimn_names
