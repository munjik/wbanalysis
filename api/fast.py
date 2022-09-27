from cmath import nan
from pickle import TRUE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import http3
import yfinance as yf
import pandas as pd
import joblib
import json
from termcolor import colored
import numpy as np
from wbanalysis.bq_storage import up_bq
from wbanalysis.gcp import get_joblib
from pandas.io.json import json_normalize



app = FastAPI()
#client = http3.AsyncClient()


# For printing
DEBUG = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins
    allow_credentials=True,
    allow_methods=['*'],  # Allow all methods
    allow_headers=['*'],  # Allow all headers
)

@app.get("/predict/{symbol}")
def predict(symbol):

    # Using model from GCP
    pipeline = get_joblib()
    pipeline = joblib.load('model.joblib')

    # Getting data for symbol
    X = data_model_feed(symbol)
    #X = flatten_json(X)
    print(X.values)
    print(X.keys)
    print(X.head(3))
    print(type(X))

    # prediction
    results_pred = pipeline.predict(X.values)

    # all data return input and output
    res = pd.DataFrame({"input": X, "output":results_pred[0]}, index=[0])
    print(json.dumps(res))
    return json.dumps(res)

@app.get("/data_model_feed/{symbol}")
def data_model_feed(symbol):
    '''
    Currently the reported quarters are:
        quarterly_balance_sheet -> 2021-09-25
        quarterly_cashflow -> 2021-09-25
        quarterly_financials -> 2021-09-25

        # Profit and distribution
        GPM = GP / TR # Gross Profit Margin
        A = SGA / GP # Percentage of Gross Profit spent on Selling General
            and Administrative SG&A (think private jets and the like)
        B = RD / GP # Percentage of Gross Proft spent on both Research and Developement R&D
        C = PPE / GP # Percantage of gross profit on property plant and equipment PP&E.
            A bagger does not have to update the plant and equipment to keep pace with competition.
        D = CE / NI # Capex as a percentage of Net Income. 50% or less is good and 25% or less is bagger.
        E = DE / GP # Depreciation as a percentage of gross profit.
        F = NI / TR # Baggers will report a higher percentage of net earnings to revenue.
            KO 21% on total revenues. LUV has a 7% which shows high competition. >20% the company has a
                \Long term advantage.
        G = NR / NI # If a company has a lower percentage of net receivables to gross
            sales then similar companies the business has a competitive advantage.
        H = CA / CL # Current Ratio. The current ratio above 1 is good and below 1 is bad.
            However many baggers have a current ratio slightly below 1.
        I = NI / TA # Return on Assets. Net earnings divided by total assets.
            KO 12%. Really high returns suggests the industry could be competitive due to a lower
            cost to market entry.

        # Debt and Financing
        J = LD / GP # Number of years it would take company to pay off Long Term Debt
        ASE = TS + SE # The shareholder equity - financial engineering.
        K = (SD + LD) / ASE # Debt to shareholder Equity. Look for a DSE
            ratio for anything below .80. [exclude banks]
        L = SD / LD # [Banks] Banks are most profitable when they borrow long-term and loan long-term.
            Wells Fargo has 57c of short term for every 1 dollar long term.
        M = IE / OI # Interest expense to operating income [Banks]
            Exceptions for banks due to this being a part of their business.
            It also explains the level of economic danger a company is in.
            Bear Stearns had a ratio of .7 in 2006 but by 2007 it had jumped to 2.3.

        N = IS + RS # Net issuance of stock. Look for a steady repurchase.
    '''
    ticker = yf.Ticker(symbol)
    GPM = ((ticker.quarterly_financials['2022-06-25']["Gross Profit"])
            /(ticker.quarterly_financials['2022-06-25']["Total Revenue"]))
    A = ((ticker.quarterly_financials['2022-06-25']["Selling General Administrative"])
            /(ticker.quarterly_financials['2022-06-25']["Gross Profit"]))
    B = ((ticker.quarterly_financials['2022-06-25']["Research Development"])
            /(ticker.quarterly_financials['2022-06-25']["Gross Profit"]))
    C = ((ticker.quarterly_balance_sheet['2022-06-25']["Property Plant Equipment"])
            /(ticker.quarterly_financials['2022-06-25']["Gross Profit"]))
    D = ((ticker.quarterly_cashflow['2022-06-25']["Capital Expenditures"])
            /(ticker.quarterly_cashflow['2022-06-25']["Net Income"]))
    E = ((ticker.quarterly_cashflow['2022-06-25']["Depreciation"])
            /(ticker.quarterly_financials['2022-06-25']["Gross Profit"]))
    F = ((ticker.quarterly_cashflow['2022-06-25']["Net Income"])
            /(ticker.quarterly_financials['2022-06-25']["Total Revenue"]))
    G = ((ticker.quarterly_balance_sheet['2022-06-25']["Retained Earnings"])
            /(ticker.quarterly_cashflow['2022-06-25']["Net Income"]))
    H = ((ticker.quarterly_balance_sheet['2022-06-25']["Total Current Assets"])
            /(ticker.quarterly_balance_sheet['2022-06-25']["Total Current Liabilities"]))
    I = ((ticker.quarterly_cashflow['2022-06-25']["Net Income"])
            /(ticker.quarterly_balance_sheet['2022-06-25']["Total Assets"]))
    J = ((ticker.quarterly_balance_sheet['2022-06-25']["Long Term Debt"])
            /(ticker.quarterly_financials['2022-06-25']["Gross Profit"]))
    # FOR Other Stockholder Equity I am using for Treasury Stock also
    # Gains Losses Not Affecting Retained Earnings is the same as Other Stock. Equity
    K = (
        ((ticker.quarterly_balance_sheet['2022-06-25']["Short Long Term Debt"])
            +(ticker.quarterly_balance_sheet['2022-06-25']["Long Term Debt"]))
        /((ticker.quarterly_balance_sheet['2022-06-25']["Other Stockholder Equity"])
            +(ticker.quarterly_balance_sheet['2022-06-25']["Total Stockholder Equity"]))
        )
    L = ((ticker.quarterly_balance_sheet['2022-06-25']["Short Long Term Debt"])
            /(ticker.quarterly_balance_sheet['2022-06-25']["Long Term Debt"]))
    M = ((ticker.quarterly_financials['2022-06-25']["Interest Expense"])
            /(ticker.quarterly_financials['2022-06-25']["Operating Income"]))
    # Issuance of Stock can be nan, like AAPL
    N = ((ticker.quarterly_cashflow['2022-06-25']["Issuance Of Stock"])
            +(ticker.quarterly_cashflow['2022-06-25']["Repurchase Of Stock"]))


    df = pd.DataFrame(
        {   "symbol":symbol,
            "GPM": GPM,
            "A (SGA)": A,
            "B (RD)" : B,
            "C (PPE)" : C,
            "D (DEPR)" : D,
            "E (CAPEX)" : E,
            "F (NI/TR)": F,
            "G (NR/NI)": G,
            "H (currentRatio)" : H,
            "I (ROA)": I,
            "J (LD/GP)": J,
            "K (debtToEquity)" : K,
            "L (SD/LD)" : L,
            "M (IN/OI)": M,
            "N (Net Issuance)" : N
        },index=[0])
    df = df.fillna(0.0)

    if DEBUG: print(df)
    return df


#TODO: Specify quarter?
@app.get("/current_model_stats/{symbol}")
def current_model_stats(symbol):
    pass

@app.get("/raw_data_download")
def raw_data_download(* args):
    pass
