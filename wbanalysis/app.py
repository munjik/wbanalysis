from distutils.command.clean import clean
import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from matplotlib import pylab
from pylab import *
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer

# Load our data
df = pd.read_csv('/Users/munjismac/code/munjik/wbanalysis/raw_data/Company Data - Data.csv')

# impute our missing values to have no missing values

def clean_data(df):
    imputer = SimpleImputer(strategy="mean") # Instanciate a SimpleImputer object with strategy of choice
    imputer.fit(df[['currentRatio']]) # Call the "fit" method on the object
    df['currentRatio'] = imputer.transform(df[['currentRatio']]) # Call the "transform" method on the object
    print(imputer.statistics_ )# The mean is stored in the transformer's memory
    return df


if __name__ == '__main__':
    # print the dataframe head to see if it worked
    imputed_data = clean_data(df)
    print(imputed_data)
    print(imputed_data.isnull().sum())
