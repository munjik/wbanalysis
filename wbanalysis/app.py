from distutils.command.clean import clean
from typing import final
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
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

# Load our data
df = pd.read_csv('/Users/munjismac/code/munjik/wbanalysis/raw_data/Company Data - Data.csv')

# impute our missing values to have no missing values
def imputer(df):
    imputer = SimpleImputer(strategy="mean") # Instanciate a SimpleImputer object with strategy of choice
    imputer.fit(df[['currentRatio']]) # Call the "fit" method on the object
    df['currentRatio'] = imputer.transform(df[['currentRatio']]) # Call the "transform" method on the object
    print(imputer.statistics_ )# The mean is stored in the transformer's memory
    return df

def onehotencode(df):
    encoder = OneHotEncoder()
    final_ohe = encoder.fit_transform(df.symbol.values.reshape(-1,1)).toarray()
    final_dfOneHot = pd.DataFrame(final_ohe, columns=['Stock_'+str(encoder.categories_[0][i]) for i in range(len(encoder.categories_[0]))])
    # concat the dataframe of our stock holders (lenders)
    final_df = pd.concat([df, final_dfOneHot], axis=1)
    # lets drop symbol from our dataframe (don't see much use in it)
    final_df = final_df.drop(columns='symbol')
    return final_df

if __name__ == '__main__':
    # print the dataframe head to see if it worked
    dataframe = imputer(df)
    one_hot_encoded_df = onehotencode(dataframe)
    print(one_hot_encoded_df)
