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
    income_statement = await call_api(base_url + params_income)
    balance_sheet = await call_api(base_url + params_bs)
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
    # INCOME STATEMENT API
    NI = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]['netIncome']['raw']
    GP = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["grossProfit"]['raw']
    SGA = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["sellingGeneralAdministrative"]['raw']
    RD = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["researchDevelopment"]['raw']
    TR = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["totalRevenue"]['raw']
    IE = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["interestExpense"]['raw']
    OE = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["totalOperatingExpenses"]['raw']
    OI = GP - OE # Operating Income = Gross Profit - Operating Expense

    # BALANCE SHEET API
    NR = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["retainedEarnings"]['raw']
    CA = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalCurrentAssets"]['raw']
    CL = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalCurrentLiabilities"]['raw']
    TA = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalAssets"]['raw']
    SE = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalStockholderEquity"]['raw']
    PPE = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["propertyPlantEquipment"]['raw']
    SD = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["shortLongTermDebt"]['raw']
    LD = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["longTermDebt"]['raw']
    TS = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["treasuryStock"]['raw']
    CS = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][2]["cash"]['raw']

    # CASHFLOW STATEMENT API
    CE = abs(cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["capitalExpenditures"]['raw'])
    DE = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["depreciation"]['raw']
    IS = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["issuanceOfStock"]['raw']
    RS = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["repurchaseOfStock"]['raw']

    # Profit and distribution
    GPM = GP / TR # Gross Profit Margin
    A = SGA / GP # Percentage of Gross Profit spent on Selling General and Administrative SG&A (think private jets and the like)
    B = RD / GP # Percentage of Gross Proft spent on both Research and Developement R&D
    C = PPE / GP # Percantage of gross profit on property plant and equipment PP&E. A bagger does not have to update the plant and equipment to keep pace with competition.
    D = CE / NI # Capex as a percentage of Net Income. 50% or less is good and 25% or less is bagger.
    E = DE / GP # Depreciation as a percentage of gross profit.
    F = NI / TR # Baggers will report a higher percentage of net earnings to revenue. KO 21% on total revenues. LUV has a 7% which shows high competition. >20% the company has a Long term advantage.
    G = NR / NI # If a company has a lower percentage of net receivables to gross sales then similar companies the business has a competitive advantage.
    H = CA / CL # Current Ratio. The current ratio above 1 is good and below 1 is bad. However many baggers have a current ratio slightly below 1.
    I = NI / TA # Return on Assets. Net earnings divided by total assets. KO 12%. Really high returns suggests the industry could be competitive due to a lower cost to market entry.

    # Debt and Financing
    J = LD / GP # Number of years it would take company to pay off Long Term Debt
    ASE = TS + SE # The shareholder equity - financial engineering.
    K = (SD + LD) / ASE # Debt to shareholder Equity. Look for a DSE ratio for anything below .80. [exclude banks]
    L = SD / LD # [Banks] Banks are most profitable when they borrow long-term and loan long-term. Wells Fargo has 57c of short term for every 1 dollar long term.
    M = IE / OI # Interest expense to operating income [Banks] Exceptions for banks due to this being a part of their business. It also explains the level of economic danger a company is in. Bear Stearns had a ratio of .7 in 2006 but by 2007 it had jumped to 2.3.

    N = IS + RS # Net issuance of stock. Look for a steady repurchase.

    return RS



# # build X ⚠️ beware to the order of the parameters ⚠️
#     X = pd.DataFrame(dict(
#         key=[key],
#         pickup_datetime=[formatted_pickup_datetime],
#         pickup_longitude=[float(pickup_longitude)],
#         pickup_latitude=[float(pickup_latitude)],
#         dropoff_longitude=[float(dropoff_longitude)],
#         dropoff_latitude=[float(dropoff_latitude)],
#         passenger_count=[int(passenger_count)]))

#     # ⚠️ TODO: get model from GCP

#     # pipeline = get_model_from_gcp()
#     pipeline = joblib.load('model.joblib')

#     # make prediction
#     results = pipeline.predict(X)
