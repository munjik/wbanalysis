from webbrowser import get
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import http3
import pandas as pd
import yahoo_fin.stock_info as yf

app = FastAPI()
client = http3.AsyncClient()
base_url = 'https://yfapi.net/v11/finance/quoteSummary/'
# api_key = 'apikey=CmVlEza5Un9eIBTyvq7zea5Yk6wcPszN9UEYsUvF'
headers = {
    'x-api-key': "CmVlEza5Un9eIBTyvq7zea5Yk6wcPszN9UEYsUvF"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # Allow all origins
    allow_credentials=True,
    allow_methods=['*'], # Allow all methods
    allow_headers=['*'], # Allow all headers
)

async def call_api(url: str):

    r = await client.get(url,headers=headers)
    return r.json()

# define a root '/' endpoint
@app.get("/")
def api_root():
    return {"Please provide a query"}

@app.get("/predict/{symbol}")
async def predict(symbol):
    # balance sheet statement
    params_bs = f'{symbol}?lang=en&region=US&modules=balanceSheetHistory'
    # income sheet statement
    params_income = f'{symbol}?lang=en&region=US&modules=incomeStatementHistory'
    # cash flow statement
    params_cash = f'{symbol}?lang=en&region=US&modules=cashflowStatementHistory'

    # grab our 3 API's with business info needed for model
    balance_sheet = await call_api(base_url + params_bs)
    income_statement = await call_api(base_url + params_income)
    cashflow_statement = await call_api(base_url + params_cash)

    """ Procedure:
        ***KEEP IN MIND:FINANCIAL MODELING GROUP IS FOR HISTORICAL DATA TO TRAIN OUR MODEL WITH.
        YAHOO FINANCE STOCK API IS FOR THE USERS TO PICK A STOCK AND FEED IT INTO OUR MODEL
        ***
        1.) Grab our values from the .JSON store it in variables
        2.) Create another variable with the list of column names
        3.) Zip these two to form a Dict, then assign the dict as a DataFrame -> dict(zip(a, b))
        4.) Feed the joblib file with the newly dataframe
        5.) Create a prediction
        """

    # BALANCE SHEET API


    # INCOME STATEMENT API

    # CASHFLOW STATEMENT API


    return cashflow_statement
