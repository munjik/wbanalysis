from webbrowser import get
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import http3
import pandas as pd
import yahoo_fin.stock_info as yf
import joblib
from termcolor import colored


from wbanalysis.gcp import get_joblib

app = FastAPI()
client = http3.AsyncClient()
base_url = 'https://yfapi.net/v11/finance/quoteSummary/'
# api_key = 'apikey=CmVlEza5Un9eIBTyvq7zea5Yk6wcPszN9UEYsUvF'

# TODO: Check docs on update of key
headers = {'x-api-key': "XAzuJdkSZa5W9Jy26Yasp28s8yJoP91xaSmaaXaS"}

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

    print(income_statement)
    # INCOME STATEMENT API
    try:
        NI = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]['netIncome']['raw']
    except:
        NI = 0
        print(colored("NI=0", "red"))

    try:
        GP = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["grossProfit"]['raw']
    except:
        GP = 0
        print(colored("GP=0", "red"))

    try:
        SGA = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["sellingGeneralAdministrative"]['raw']
    except:
        SGA = 0
        print(colored("SGA=0", "red"))

    # API returns 0 NIKE does not report
    try:
        RD = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["researchDevelopment"]['raw']
    except:
        RD = 0
        print(colored("RD=0", "red"))

    try:
        TR = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["totalRevenue"]['raw']
    except:
        TR = 0
        print(colored("TR=0", "red"))

    try:
        IE = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["interestExpense"]['raw']
    except:
        IE = 0
        print(colored("IE=0", "red"))

    try:
        OE = income_statement["quoteSummary"]['result'][0]['incomeStatementHistory']['incomeStatementHistory'][0]["totalOperatingExpenses"]['raw']
    except:
        OE = 0
        print(colored("OE=0", "red"))

    try:
        OI = GP - OE # Operating Income = Gross Profit - Operating Expense
    except:
        OI = 0
        print(colored("OI=0", "red"))

    # BALANCE SHEET API
    try:
        NR = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["retainedEarnings"]['raw']
    except:
        NR = 0
    try:
        CA = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalCurrentAssets"]['raw']
    except:
        CA = 0
    try:
        CL = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalCurrentLiabilities"]['raw']
    except:
        CL = 0
    try:
        TA = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalAssets"]['raw']
    except:
        TA = 0
    try:
        SE = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["totalStockholderEquity"]['raw']
    except:
        SE = 0
    try:
        PPE = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][0]["propertyPlantEquipment"]['raw']
    except:
        PPE = 0
    try:
        SD = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["shortLongTermDebt"]['raw']
    except:
        SD = 0
    try:
        LD = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["longTermDebt"]['raw']
    except:
        LD = 0
    try:
        TS = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][1]["treasuryStock"]['raw']
    except:
        TS = 0
    try:
        CS = balance_sheet["quoteSummary"]['result'][0]['balanceSheetHistory']['balanceSheetStatements'][2]["cash"]['raw']
    except:
        CS = 0

    # CASHFLOW STATEMENT API
    try:
        CE = abs(cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["capitalExpenditures"]['raw'])
    except:
        CE = 0

    try:
        DE = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["depreciation"]['raw']
    except:
        DE = 0

    try:
        IS = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["issuanceOfStock"]['raw']
    except:
        IS = 0

    try:
        RS = cashflow_statement["quoteSummary"]['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]["repurchaseOfStock"]['raw']
    except:
        RS = 0

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

    # New variable alignment according to training
    # GPM = GP / TR
    # A (SGA) = SGA / GP
    # B (RD) = RD / GP
    # C (PPE) = PPE / GP
    # D (DEPR) = DE / GP
    # E (CAPEX) = CE / NI
    # F (NI) = NI / TR
    # G (NR) = NR / NI
    # H (currentRatio) = CA / CL
    # I (ROA) = NI / TA
    # J (LD) = LD / GP
    # K (debtToEquity) =  (SD + LD) / ASE
    # L (SD) = SD / LD
    # M (IN) = IE / OI
    # N (Net Issuance)  = IS + RS

    # below is our raw data columns must match this!
    data_x = {
        f"{symbol}": [symbol],
        "GPM": [GPM],
        "A (SGA)": [A],
        "B (RD)" : [B],
        "C (PPE)" : [C],
        "D (DEPR)" : [D],
        "E (CAPEX)" : [E],
        "F (NI/TR)": [F],
        "G (NR/NI)": [G],
        "H (currentRatio)" : [H],
        "I (ROA)": [I],
        "J (LD/GP)": [J],
        "K (debtToEquity)" : [K],
        "L (SD/LD)" : [L],
        "M (IN/OI)": [M],
        "N (Net Issuance)" : [N]
    }
    X = pd.DataFrame.from_dict(data_x)
    # ⚠️ TODO: get model from GCP
    print(X.head())
    pipeline = get_joblib()
    pipeline = joblib.load('model.joblib')

    # # make prediction
    results = pipeline.predict(X)

    print(results[0])
    print(type(results))
    # return results
    res = {"results": [results]}
    return list(results)
