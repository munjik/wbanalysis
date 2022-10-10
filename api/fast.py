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
#from wbanalysis.bq_storage import up_bq
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
    pipeline = joblib.load('model_1.joblib')

    # Getting data for symbol
    x_feed = data_model_feed(symbol)
    X = pd.DataFrame(x_feed.copy())
    print(X.values)
    print(X.keys)
    print(X.head(3))
    print(type(X))
    print("******************** BEFORE LINE 47")
    # Dropping dividend yield and symbol before feeding into model for pred
    X.drop(columns=['symbol'], inplace=True)

    # prediction
    results_pred = pipeline.predict(X)
    #print(pipeline.score)
    print("******************** PRED")
    # all data return input and output
    print(results_pred[:])
    res = pd.DataFrame({results_pred[0]})
    print(res)
    print(json.dumps(results_pred[0]))
    return json.dumps(results_pred[0])

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
    # df = pd.DataFrame({
    #     "symbol":symbol,
    #     "GPM": ,
    #     "A (SGA)": ,
    #     "B (RD)" : ,
    #     "C (PPE)" : ,
    #     "D (DEPR)" : ,
    #     "E (CAPEX)" : ,
    #     "F (NI/TR)": ,
    #     "G (NR/NI)": ,
    #     "H (currentRatio)":
    #     "I (ROA)": ,
    #     "J (LD/GP)": ,
    #     "K (debtToEquity)"
    #     "L (SD/LD)" : ,
    #     "M (IN/OI)": ,
    #     "N (Net Issuance)"})
    # met_df = pd.DataFrame()
    # metrics = ["GPM" ,"A", "B" , "C", "D" , "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]
    # qf_keys = ["Gross Profit", "Total Revenue", "Selling General Administrative",
    #             "Research Development","Total Revenue","Interest Expense","Operating Income"]
    # qcf_keys = ["Capital Expenditures","Net Income","Depreciation","Issuance Of Stock","Repurchase Of Stock"]
    # qbs_keys = ["Property Plant Equipment","Retained Earnings","Total Current Assets",
    #             "Total Current Liabilities", "Total Assets", "Long Term Debt",
    #             "Short Long Term Debt","Other Stockholder Equity","Total Stockholder Equity"]
    # ticker = yf.Ticker(symbol)
    # for i in metrics:
    #     met_df[i] =
    ticker = yf.Ticker(symbol)
    GPM = ((ticker.quarterly_financials.iloc[:, :1].T[["Gross Profit"
                                                       ]].values[0][0]) /
           (ticker.quarterly_financials.iloc[:, :1].T[["Total Revenue"
                                                       ]].values[0][0]))
    A = ((ticker.quarterly_financials.iloc[:, :1].T[[
        "Selling General Administrative"
    ]].values[0][0]) / (ticker.quarterly_financials.iloc[:, :1].T[[
        "Gross Profit"
    ]].values[0][0]))
    try:
        B = ((ticker.quarterly_financials.iloc[:, :1].T[["Research Development"
                                                     ]].values[0][0]) /
         (ticker.quarterly_financials.iloc[:, :1].T[["Gross Profit"
                                                     ]].values[0][0]))
    except:
        B = 0
    C = ((ticker.quarterly_balance_sheet.iloc[:, :1].T[[
        "Property Plant Equipment"
        ]].values[0][0]) /
         (ticker.quarterly_financials.iloc[:, :1].T[["Gross Profit"
                                                     ]].values[0][0]))
    D = (
        (ticker.quarterly_cashflow.iloc[:, :1].T[["Capital Expenditures"
                                                  ]].values[0][0]) /
        (ticker.quarterly_cashflow.iloc[:, :1].T[["Net Income"]].values[0][0]))

    E = ((ticker.quarterly_cashflow.iloc[:, :1].T[["Depreciation"
                                                   ]].values[0][0]) /
         (ticker.quarterly_financials.iloc[:, :1].T[["Gross Profit"
                                                     ]].values[0][0]))
    F = ((ticker.quarterly_cashflow.iloc[:, :1].T[["Net Income"]].values[0][0])
         / (ticker.quarterly_financials.iloc[:, :1].T[["Total Revenue"
                                                       ]].values[0][0]))
    G = (
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Retained Earnings"
                                                       ]].values[0][0]) /
        (ticker.quarterly_cashflow.iloc[:, :1].T[["Net Income"]].values[0][0]))
    H = (
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Total Current Assets"
                                                       ]].values[0][0]) /
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[[
            "Total Current Liabilities"
        ]].values[0][0]))
    I = ((ticker.quarterly_cashflow.iloc[:, :1].T[["Net Income"]].values[0][0])
         / (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Total Assets"
                                                          ]].values[0][0]))
    J = ((ticker.quarterly_balance_sheet.iloc[:, :1].T[["Long Term Debt"
                                                        ]].values[0][0]) /
         (ticker.quarterly_financials.iloc[:, :1].T[["Gross Profit"
                                                     ]].values[0][0]))
    # FOR Other Stockholder Equity I am using for Treasury Stock also
    # Gains Losses Not Affecting Retained Earnings is the same as Other Stock. Equity
    K = ((
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Short Long Term Debt"
                                                       ]].values[0][0]) +
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Long Term Debt"
                                                       ]].values[0][0])) /
         ((ticker.quarterly_balance_sheet.iloc[:, :1].T[
             ["Other Stockholder Equity"]].values[0][0]) +
          (ticker.quarterly_balance_sheet.iloc[:, :1].T[
              ["Total Stockholder Equity"]].values[0][0])))
    L = (
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Short Long Term Debt"
                                                       ]].values[0][0]) /
        (ticker.quarterly_balance_sheet.iloc[:, :1].T[["Long Term Debt"
                                                       ]].values[0][0]))
    M = ((ticker.quarterly_financials.iloc[:, :1].T[["Interest Expense"
                                                     ]].values[0][0]) /
         (ticker.quarterly_financials.iloc[:, :1].T[["Operating Income"
                                                     ]].values[0][0]))
    # Issuance of Stock can be nan, like AAPL
    N = ((ticker.quarterly_cashflow.iloc[:, :1].T[["Issuance Of Stock"
                                                   ]].values[0][0]) +
         (ticker.quarterly_cashflow.iloc[:, :1].T[["Repurchase Of Stock"
                                                   ]].values[0][0]))

    print("Before df###################")
    print(symbol)
    print(A)
    print(B)
    print(C)
    print(D)
    print(E)
    print(F)
    print(G)
    print(H)
    print(I)
    print(J)
    print(K)
    print(L)
    print(M)
    print(N)

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
        }, index=[0])
    df = df.fillna(0.0)
    print("After df###################")

    if DEBUG: print(df)
    return df


#TODO: Specify quarter?
@app.get("/current_model_stats/{symbol}")
def current_model_stats(symbol):
    pass

@app.get("/raw_data_download")
def raw_data_download(* args):
    pass
