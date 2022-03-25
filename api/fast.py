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
    params_bs = f'/api/v3/balance-sheet-statement/{symbol}?limit=120&'
    # income sheet statement
    params_income = f'/api/v3/income-statement/{symbol}?limit=120&'
    # cash flow statement
    params_cash = f'/api/v3/cash-flow-statement/{symbol}?limit=120&'

    # try:
    #     balance_sheet = await call_api(base_url + params_bs + api_key)
    #     # return {"res": res1}
    # except:
    #     return {"error"}

    # grab our 3 API's with business info needed for model
    balance_sheet = await call_api(base_url + params_bs + api_key)
    income_statement = await call_api(base_url + params_income + api_key )
    cashflow_statement = await call_api(base_url + params_cash + api_key )

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
    NR = balance_sheet[0]['retainedEarnings']
    CA = balance_sheet[0]["totalCurrentAssets"]
    CL = balance_sheet[0]["totalCurrentLiabilities"]
    TA = balance_sheet[0]["totalAssets"]
    SE = balance_sheet[0]["totalStockholdersEquity"]
    PPE =balance_sheet[0]["propertyPlantEquipmentNet"]
    SD = balance_sheet[0]["shortTermDebt"]
    LD = balance_sheet[0]["longTermDebt"]
    # TS = balance_sheet[0]["treasuryStock"]
    # CS = balance_sheet[0]["cash"]
    # X = {balance_sheet[0]['calendarYear'],
    #      balance_sheet[0]['longTermInvestments']
    #      }

    # INCOME STATEMENT API
    NI = income_statement[0]["netIncome"]
    GP = income_statement[0]["grossProfit"]
    SGA = income_statement[0]["sellingGeneralAndAdministrativeExpenses"]
    RD = income_statement[0]["researchAndDevelopmentExpenses"]
    TR = income_statement[0]["revenue"]
    IE = income_statement[0]["interestExpense"]
    OE = income_statement[0]["operatingExpenses"]
    OI = GP - OE # Operating Income = Gross Profit - Operating Expense

    # CASHFLOW STATEMENT API
    CE = abs(cashflow_statement[0]["capitalExpenditures"])
    DE = cashflow_statement[0]["depreciation"]
    IS = cashflow_statement[0]["issuanceOfStock"] # (+)
    RS = cashflow_statement[0]["repurchaseOfStock"] # (-)

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
    return cashflow_statement
