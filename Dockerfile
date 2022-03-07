FROM python:3.8.6-buster

# Copying data we want in the docker
COPY wbanalysis /wbanalysis
COPY api /api
COPY requirements.txt /requirements.txt
COPY credentials.json /credentials.json

# Installing the required libraries and requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Creating the RESTful service
CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
