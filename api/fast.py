from webbrowser import get
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import stock
import requests
from api import test
import time
import http3

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
    #time.sleep(10)
    try:
        res1 = await call_api(base_url + params + api_key)
        return {"res": res1}
    except:
        return {"error"}
