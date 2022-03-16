from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()
base_url = 'https://financialmodelingprep.com'
api_key = 'apikey=3845af5c988287d80bbe6a9e83d56c30'

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # Allow all origins
    allow_credentials=True,
    allow_methods=['*'], # Allow all methods
    allow_headers=['*'], # Allow all headers
)

# define a root '/' endpoint
@app.get("/")
def api_root():
    return {"Please provide a query"}

@app.get("/predict")
def predict():
    # balance sheet statement
    stock = 'NVDA'
    params = f'/api/v3/balance-sheet-statement/{stock}?limit=120'
    response = requests.get(base_url + params + api_key).json()
    print(response)
    # return {response}
    # return response[0]
