#from time import pthread_getcpuclockid
import asyncio
from webbrowser import get
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import http3
import pandas as pd
import yahoo_fin.stock_info as yf
import joblib
import json
from termcolor import colored
import yfinance as yf

from wbanalysis.bq_storage import up_bq
from wbanalysis.gcp import get_joblib

app = FastAPI()
client = http3.AsyncClient()
base_url = 'https://yfapi.net/v11/finance/quoteSummary/'
# api_key = 'apikey=CmVlEza5Un9eIBTyvq7zea5Yk6wcPszN9UEYsUvF'

# TODO: Check docs on update of key
headers = {'x-api-key': "CPjDHUB4H33fEzQX2J8sd9yiX73PPdXRamsaQfd4"}

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
async def predict(*, args):
    """
    Here we may need to refactor the code to take in a list of symbol's
    """
    res_complete = pd.DataFrame()
    for str in args:
        # balance sheet statement
        params_bs = f'{str}?lang=en&region=US&modules=balanceSheetHistory'
        # income sheet statement
        params_income = f'{str}?lang=en&region=US&modules=incomeStatementHistory'
        # cash flow statement
        params_cash = f'{str}?lang=en&region=US&modules=cashflowStatementHistory'

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
            f"symbol": [str],
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

        # Saving df to csv for evaluation
        X.to_csv(index=False)

        # ⚠️ TODO: get model from GCP
        print(X.head())
        pipeline = get_joblib()
        pipeline = joblib.load('model.joblib')

        # # make prediction
        results = pipeline.predict(X)

        print(results[0])
        print(type(results))
        # return results for viz
        res = {
            "results": results,
            f"symbol": str,
            "GPM": GPM,
            "A_SGA": A,
            "B_RD": B,
            "C_PPE": C,
            "D_DEPR": D,
            "E_CAPEX": E,
            "F_NI_TR": F,
            "G_NR_NI": G,
            "H_currentRatio": H,
            "I_ROA": I,
            "J_LD_GP": J,
            "K_debtToEquity": K,
            "L_SD_LD": L,
            "M_IN_OI": M,
            "N_NetIssuance": N
        }
        pd.concat([res_complete, pd.DataFrame(res)])


    #TODO: Upload res_complete to bq
    print("Uploading to BQ")
    print(type(res_complete))
    print(res_complete.info())
    up_bq(res_complete)

    app_json = json.dumps(results[0])
    return app_json

@app.get("/data_update")
async def raw_data_update(*args):

    pass

if __name__ == '__main__':

    """
    Automatically run a set of ticker symbols for storage in BQ for
    front-end dev
    """
    # ticker = [
    #     'A', 'AA', 'AAC', 'AACG', 'AACI', 'AACIU', 'AACIW', 'AADI', 'AAIC'
    #     # 'AAIC^B', 'AAIC^C', 'AAIN', 'AAL', 'AAM^A', 'AAM^B', 'AAMC', 'AAME',
    #     # 'AAN', 'AAOI', 'AAON', 'AAP', 'AAPL', 'AAQC', 'AAT', 'AATC', 'AAU',
    #     # 'AAWW', 'AB', 'ABB', 'ABBV', 'ABC', 'ABCB', 'ABCL', 'ABCM', 'ABEO',
    #     # 'ABEV', 'ABG', 'ABGI', 'ABIO', 'ABM', 'ABMD', 'ABNB', 'ABOS', 'ABR',
    #     # 'ABR^D', 'ABR^E', 'ABR^F', 'ABSI', 'ABST', 'ABT', 'ABTX', 'ABUS',
    #     # 'ABVC', 'AC', 'ACA', 'ACAB', 'ACABU', 'ACABW', 'ACACU', 'ACAD', 'ACAH',
    #     # 'ACAHU', 'ACAQ', 'ACAX', 'ACAXR', 'ACAXU', 'ACAXW', 'ACB', 'ACBA',
    #     # 'ACBAU', 'ACBAW', 'ACC', 'ACCD', 'ACCO', 'ACDI', 'ACEL', 'ACER',
    #     # 'ACET', 'ACEV', 'ACEVW', 'ACGL', 'ACGLN', 'ACGLO', 'ACH', 'ACHC',
    #     # 'ACHL', 'ACHR', 'ACHV', 'ACI', 'ACII', 'ACIU', 'ACIW', 'ACKIT',
    #     # 'ACKIU', 'ACKIW', 'ACLS', 'ACLX', 'ACM', 'ACMR', 'ACN', 'ACNB', 'ACON',
    #     # 'ACOR', 'ACP', 'ACP^A', 'ACQR', 'ACQRU', 'ACQRW', 'ACR', 'ACR^C',
    #     # 'ACR^D', 'ACRE', 'ACRO', 'ACRS', 'ACRX', 'ACST', 'ACT', 'ACTD',
    #     # 'ACTDU', 'ACTDW', 'ACTG', 'ACU', 'ACV', 'ACVA', 'ACXP', 'ADAG', 'ADAL',
    #     # 'ADALU', 'ADALW', 'ADAP', 'ADBE', 'ADC', 'ADC^A', 'ADCT', 'ADER',
    #     # 'ADES', 'ADEX', 'ADGI', 'ADI', 'ADIL', 'ADILW', 'ADM', 'ADMA', 'ADMP',
    #     # 'ADN', 'ADNT', 'ADNWW', 'ADOC', 'ADOCR', 'ADOCW', 'ADP', 'ADPT',
    #     # 'ADRA', 'ADRT', 'ADSE', 'ADSEW', 'ADSK', 'ADT', 'ADTH', 'ADTHW',
    #     # 'ADTN', 'ADTX', 'ADUS', 'ADV', 'ADVM', 'ADVWW', 'ADX', 'ADXN', 'AE',
    #     # 'AEACU', 'AEACW', 'AEAE', 'AEAEU', 'AEAEW', 'AEE', 'AEF', 'AEFC',
    #     # 'AEG', 'AEHAW', 'AEHL', 'AEHR', 'AEI', 'AEIS', 'AEL', 'AEL^A', 'AEL^B',
    #     # 'AEM', 'AEMD', 'AENZ', 'AEO', 'AEP', 'AEPPZ', 'AER', 'AERC', 'AERI',
    #     # 'AES', 'AESC', 'AESE', 'AEVA', 'AEY', 'AEYE', 'AEZS', 'AFACU', 'AFAQ',
    #     # 'AFAQU', 'AFAQW', 'AFAR', 'AFARU', 'AFARW', 'AFB', 'AFBI', 'AFCG',
    #     # 'AFG', 'AFGB', 'AFGC', 'AFGD', 'AFGE', 'AFIB', 'AFL', 'AFMD', 'AFRI',
    #     # 'AFRIW', 'AFRM', 'AFT', 'AFTR', 'AFYA', 'AG', 'AGAC', 'AGBA', 'AGBAR',
    #     # 'AGBAW', 'AGCB', 'AGCO', 'AGD', 'AGE', 'AGEN', 'AGFS', 'AGFY', 'AGGR',
    #     # 'AGGRU', 'AGGRW', 'AGI', 'AGIL', 'AGILW', 'AGIO', 'AGL', 'AGLE', 'AGM',
    #     # 'AGM^C', 'AGM^D', 'AGM^E', 'AGM^F', 'AGM^G', 'AGMH', 'AGNC', 'AGNCM',
    #     # 'AGNCN', 'AGNCO', 'AGNCP', 'AGO', 'AGR', 'AGRI', 'AGRIW', 'AGRO',
    #     # 'AGRX', 'AGS', 'AGTC', 'AGTI', 'AGX', 'AGYS', 'AHCO', 'AHG', 'AHH',
    #     # 'AHH^A', 'AHI', 'AHL^C', 'AHL^D', 'AHL^E', 'AHPA', 'AHPAU', 'AHPAW',
    #     # 'AHPI', 'AHRN', 'AHRNU', 'AHRNW', 'AHT', 'AHT^D', 'AHT^F', 'AHT^G',
    #     # 'AHT^H', 'AI', 'AIBBU', 'AIC', 'AIF', 'AIG', 'AIG^A', 'AIH', 'AIHS',
    #     # 'AIKI', 'AIM', 'AIMAU', 'AIMAW', 'AIMBU', 'AIMC', 'AIN', 'AINC',
    #     # 'AINV', 'AIO', 'AIP', 'AIR', 'AIRC', 'AIRG', 'AIRI', 'AIRS', 'AIRT',
    #     # 'AIRTP', 'AIT', 'AIU', 'AIV', 'AIZ', 'AIZN', 'AJG', 'AJRD', 'AJX',
    #     # 'AJXA', 'AKA', 'AKAM', 'AKAN', 'AKBA', 'AKIC', 'AKICU', 'AKICW',
    #     # 'AKO/A', 'AKO/B', 'AKR', 'AKRO', 'AKTS', 'AKTX', 'AKU', 'AKUS', 'AKYA',
    #     # 'AL', 'AL^A', 'ALB', 'ALBO', 'ALC', 'ALCC', 'ALCO', 'ALDX', 'ALE',
    #     # 'ALEC', 'ALEX', 'ALF', 'ALFIW', 'ALG', 'ALGM', 'ALGN', 'ALGS', 'ALGT',
    #     # 'ALHC', 'ALIM', 'ALIN^A', 'ALIN^B', 'ALIN^E', 'ALIT', 'ALJJ', 'ALK',
    #     # 'ALKS', 'ALKT', 'ALL', 'ALL^B', 'ALL^G', 'ALL^H', 'ALL^I', 'ALLE',
    #     # 'ALLG', 'ALLK', 'ALLO', 'ALLR', 'ALLT', 'ALLY', 'ALNA', 'ALNY', 'ALOR',
    #     # 'ALORU', 'ALORW', 'ALOT', 'ALP^Q', 'ALPA', 'ALPAW', 'ALPN', 'ALPP',
    #     # 'ALR', 'ALRM', 'ALRN', 'ALRS', 'ALSA', 'ALSAU', 'ALSAW', 'ALSN', 'ALT',
    #     # 'ALTG', 'ALTG^A', 'ALTO', 'ALTR', 'ALTU', 'ALTUU', 'ALTUW', 'ALV',
    #     # 'ALVO', 'ALVOW', 'ALVR', 'ALX', 'ALXO', 'ALYA', 'ALZN', 'AM', 'AMAL',
    #     # 'AMAM', 'AMAO', 'AMAOW', 'AMAT', 'AMBA', 'AMBC', 'AMBO', 'AMBP', 'AMC',
    #     # 'AMCI', 'AMCIU', 'AMCIW', 'AMCR', 'AMCX', 'AMD', 'AME', 'AMED', 'AMEH',
    #     # 'AMG', 'AMGN', 'AMH', 'AMH^G', 'AMH^H', 'AMK', 'AMKR', 'AMLX', 'AMN',
    #     # 'AMNB', 'AMOT', 'AMOV', 'AMP', 'AMPE', 'AMPG', 'AMPH', 'AMPI', 'AMPL',
    #     # 'AMPS', 'AMPY', 'AMR', 'AMRC', 'AMRK', 'AMRN', 'AMRS', 'AMRX', 'AMS',
    #     # 'AMSC', 'AMSF', 'AMST', 'AMSWA', 'AMT', 'AMTB', 'AMTD', 'AMTI', 'AMTX',
    #     # 'AMWD', 'AMWL', 'AMX', 'AMYT', 'AMZN', 'AN', 'ANAB', 'ANAC', 'ANDE',
    #     # 'ANEB', 'ANET', 'ANF', 'ANGH', 'ANGHW', 'ANGI', 'ANGN', 'ANGO', 'ANIK',
    #     # 'ANIP', 'ANIX', 'ANNX', 'ANPC', 'ANSS', 'ANTE', 'ANTX', 'ANVS', 'ANY',
    #     # 'ANZU', 'ANZUU', 'ANZUW', 'AOD', 'AOGO', 'AOGOU', 'AOGOW', 'AOMR',
    #     # 'AON', 'AORT', 'AOS', 'AOSL', 'AOUT', 'AP', 'APA', 'APAC', 'APACU',
    #     # 'APAM', 'APCA', 'APCX', 'APCXW', 'APD', 'APDN', 'APEI', 'APEN', 'APG',
    #     # 'APGB', 'APH', 'API', 'APLD', 'APLE', 'APLS', 'APLT', 'APM', 'APMI',
    #     # 'APMIW', 'APO', 'APOG', 'APP', 'APPF', 'APPH', 'APPHW', 'APPN', 'APPS',
    #     # 'APRE', 'APRN', 'APT', 'APTM', 'APTMU', 'APTO', 'APTV', 'APTV^A',
    #     # 'APTX', 'APVO', 'APWC', 'APXI', 'APXIU', 'APYX', 'AQB', 'AQMS', 'AQN',
    #     # 'AQNA', 'AQNB', 'AQNU', 'AQST', 'AQUA', 'AR', 'ARAV', 'ARAY', 'ARBE',
    #     # 'ARBEW', 'ARBG', 'ARBGW', 'ARBK', 'ARBKL', 'ARC', 'ARCB', 'ARCC',
    #     # 'ARCE', 'ARCH', 'ARCK', 'ARCKU', 'ARCKW', 'ARCO', 'ARCT', 'ARDC',
    #     # 'ARDS', 'ARDX', 'ARE', 'AREB', 'AREBW', 'AREC', 'AREN', 'ARES', 'ARGD',
    #     # 'ARGO', 'ARGO^A', 'ARGU', 'ARGX', 'ARHS', 'ARI', 'ARIS', 'ARIZ',
    #     # 'ARKO', 'ARKOW', 'ARKR', 'ARL', 'ARLO', 'ARLP', 'ARMK', 'ARMP', 'ARNC',
    #     # 'AROC', 'AROW', 'ARQQ', 'ARQQW', 'ARQT', 'ARR', 'ARR^C', 'ARRW',
    #     # 'ARRWU', 'ARRWW', 'ARRY', 'ARTE', 'ARTEU', 'ARTEW', 'ARTL', 'ARTLW',
    #     # 'ARTNA', 'ARTW', 'ARVL', 'ARVN', 'ARW', 'ARWR', 'ARYD', 'ARYE', 'ASA',
    #     # 'ASAI', 'ASAN', 'ASAQ', 'ASAX', 'ASAXU', 'ASB', 'ASB^E', 'ASB^F',
    #     # 'ASC', 'ASCA', 'ASCAU', 'ASCAW', 'ASCB', 'ASCBR', 'ASCBU', 'ASCBW',
    #     # 'ASG', 'ASGI', 'ASGN', 'ASH', 'ASIX', 'ASLE', 'ASLN', 'ASM', 'ASMB',
    #     # 'ASML', 'ASND', 'ASNS', 'ASO', 'ASPA', 'ASPAU', 'ASPC', 'ASPCU',
    #     # 'ASPCW', 'ASPN', 'ASPS', 'ASPU', 'ASR', 'ASRT', 'ASRV', 'ASTC', 'ASTE',
    #     # 'ASTL', 'ASTLW', 'ASTR', 'ASTS', 'ASTSW', 'ASUR', 'ASX', 'ASXC',
    #     # 'ASYS', 'ASZ', 'ATA', 'ATAI', 'ATAK', 'ATAKU', 'ATAKW', 'ATAQ', 'ATAX',
    #     # 'ATC', 'ATCO', 'ATCO^D', 'ATCO^H', 'ATCO^I', 'ATCOL', 'ATCX', 'ATEC',
    #     # 'ATEN', 'ATER', 'ATEX', 'ATGE', 'ATH^A', 'ATH^B', 'ATH^C', 'ATH^D',
    #     # 'ATHA', 'ATHE', 'ATHM', 'ATHX', 'ATI', 'ATIF', 'ATIP', 'ATKR', 'ATLC',
    #     # 'ATLCL', 'ATLCP', 'ATLO', 'ATNF', 'ATNFW', 'ATNI', 'ATNM', 'ATNX',
    #     # 'ATO', 'ATOM', 'ATOS', 'ATR', 'ATRA', 'ATRC', 'ATRI', 'ATRO', 'ATSG',
    #     # 'ATTO', 'ATUS', 'ATVC', 'ATVCU', 'ATVCW', 'ATVI', 'ATXI', 'ATXS',
    #     # 'ATY', 'AU', 'AUB', 'AUBAP', 'AUBN', 'AUD', 'AUDC', 'AUGX', 'AUID',
    #     # 'AUMN', 'AUPH', 'AUR', 'AURA', 'AURC', 'AURCW', 'AUROW', 'AUS', 'AUST',
    #     # 'AUTL', 'AUTO', 'AUUD', 'AUVI', 'AUVIP', 'AUY', 'AVA', 'AVAC', 'AVACW',
    #     # 'AVAH', 'AVAL', 'AVAN', 'AVAV', 'AVB', 'AVCO', 'AVCT', 'AVCTW', 'AVD',
    #     # 'AVDL', 'AVDX', 'AVEO', 'AVGO', 'AVGOP', 'AVGR', 'AVHI', 'AVID',
    #     # 'AVIR', 'AVK', 'AVLR', 'AVNS', 'AVNT', 'AVNW', 'AVO', 'AVPT', 'AVPTW',
    #     # 'AVRO', 'AVT', 'AVTE', 'AVTR', 'AVTX', 'AVXL', 'AVY', 'AVYA', 'AWF',
    #     # 'AWH', 'AWI', 'AWK', 'AWP', 'AWR', 'AWRE', 'AWX', 'AX', 'AXAC', 'AXDX',
    #     # 'AXGN', 'AXH', 'AXL', 'AXLA', 'AXNX', 'AXON', 'AXP', 'AXR', 'AXS',
    #     # 'AXS^E', 'AXSM', 'AXTA', 'AXTI', 'AXU', 'AY', 'AYI', 'AYLA', 'AYRO',
    #     # 'AYTU', 'AYX', 'AZ', 'AZEK', 'AZN', 'AZO', 'AZPN', 'AZRE', 'AZTA',
    #     # 'AZUL', 'AZYO', 'AZZ', 'B', 'BA', 'BABA', 'BAC', 'BAC^B', 'BAC^E',
    #     # 'BAC^K', 'BAC^L', 'BAC^M', 'BAC^N', 'BAC^O', 'BAC^P', 'BAC^Q', 'BAC^S',
    #     # 'BACA', 'BAFN', 'BAH', 'BAK', 'BALL', 'BALY', 'BAM', 'BAMH', 'BAMI',
    #     # 'BAMR', 'BANC', 'BAND', 'BANF', 'BANFP', 'BANR', 'BANX', 'BAOS', 'BAP',
    #     # 'BARK', 'BASE', 'BATL', 'BATRA', 'BATRK', 'BAX', 'BB', 'BBAI', 'BBAR',
    #     # 'BBBY', 'BBCP', 'BBD', 'BBDC', 'BBDO', 'BBGI', 'BBI', 'BBIG', 'BBIO',
    #     # 'BBLG', 'BBLGW', 'BBLN', 'BBN', 'BBQ', 'BBSI', 'BBU', 'BBUC', 'BBVA',
    #     # 'BBW', 'BBWI', 'BBY', 'BC', 'BC^A', 'BC^B', 'BC^C', 'BCAB', 'BCAC',
    #     # 'BCACU', 'BCACW', 'BCAN', 'BCAT', 'BCBP', 'BCC', 'BCDA', 'BCDAW',
    #     # 'BCE', 'BCEL', 'BCH', 'BCLI', 'BCML', 'BCO', 'BCOR', 'BCOV', 'BCOW',
    #     # 'BCPC', 'BCRX', 'BCS', 'BCSA', 'BCSAU', 'BCSF', 'BCTX', 'BCTXW', 'BCV',
    #     # 'BCV^A', 'BCX', 'BCYC', 'BDC', 'BDJ', 'BDL', 'BDN', 'BDSX', 'BDTX',
    #     # 'BDX', 'BDXB', 'BE', 'BEAM', 'BEAT', 'BECN', 'BEDU', 'BEEM', 'BEKE',
    #     # 'BELFA', 'BELFB', 'BEN', 'BENE', 'BENER', 'BENEW', 'BEP', 'BEP^A',
    #     # 'BEPC', 'BEPH', 'BEPI', 'BERY', 'BEST', 'BF/A', 'BF/B', 'BFAC', 'BFAM',
    #     # 'BFC', 'BFH', 'BFI', 'BFIIW', 'BFIN', 'BFK', 'BFLY', 'BFRI', 'BFRIW',
    #     # 'BFS', 'BFS^D', 'BFS^E', 'BFST', 'BFZ', 'BG', 'BGB', 'BGCP', 'BGFV',
    #     # 'BGH', 'BGI', 'BGNE', 'BGR', 'BGRY', 'BGRYW'
    # ]
    # for t in ticker:
    #     asyncio.run(predict(t))
    #     print(f"Finished for {t}")
    # print("All done")
    pass
