from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

@app.get("/hello")
def hello():
    return {"Hello": "World"}
