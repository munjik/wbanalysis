# Imports
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
from termcolor import colored
#from app import drop_columns
import pandas as pd
#from gcp import get_data_from_gcp
from wbanalysis.gcp import storage_upload


#TODO: upload data file to GCP. Have a function to do this!
#df = get_data_from_gcp()

class Trainer(object):
    def __init__(self, X, y):
        #  X: pandas DataFrame
        #  y: pandas Series
        self.X = X
        self.y = y
        self.knn_model = None

    def set_pipeline(self):
        scaler_pipe = Pipeline(steps=[
            ('scaler', RobustScaler())
        ])
        preproc_pipe = ColumnTransformer(transformers=[
            ('num', scaler_pipe, [
                "GPM", "A (SGA)", "B (RD)", "C (PPE)", "D (DEPR)", "E (CAPEX)",
                "F (NI/TR)", "G (NR/NI)", "H (currentRatio)", "I (ROA)",
                "J (LD/GP)", "K (debtToEquity)", "L (SD/LD)", "M (IN/OI)",
                "N (Net Issuance)"
            ]),
        ])
        self.knn_model = Pipeline(steps=[
            ('preproc', preproc_pipe),
            ('knn',  KNeighborsClassifier(n_neighbors=5, weights='distance'
                                            ,algorithm='brute'
                                            ,leaf_size=44, p=1))
        ])

    def run(self):
        self.set_pipeline()
        self.knn_model.fit(self.X, self.y)

    def build_model(self):
        """ defines our model as a class asttribute"""
        model =  KNeighborsClassifier(n_neighbors=5, weights='distance'
                                            ,algorithm='brute'
                                            ,leaf_size=44, p=1)
        return model


    def evaluate(self, X_test, y_test):
        r2_test = self.knn_model.score(X_test, y_test)
        y_pred = self.knn_model.predict(X_test)

        # Confusion Matrix
        print(confusion_matrix(y_test, y_pred))
        # Accuracy
        print(accuracy_score(y_test, y_pred))
        # Recall
        print(recall_score(y_test, y_pred, average=None))
        # Precision
        print(precision_score(y_test, y_pred, average=None))

        # Returning all metrics for display as a dictionary
        evs = {
            'r2_test': r2_test,
            'y_pred': y_pred,
            'Confusion Matrix': confusion_matrix(y_test, y_pred),
            'Accuracy': accuracy_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred, average=None),
            'Precision': precision_score(y_test, y_pred, average=None)
        }

        return evs

    def save_model(self):
        joblib.dump(self.knn_model, 'model_1.joblib')
        print(colored("model_1.joblib saved locally", "green"))

if __name__ == "__main__":

    # read our Dataframe until we load it into the GCP
    #df = pd.read_csv('/Users/munjismac/code/munjik/wbanalysis/raw_data/CompanyData-Data.csv')
    df = pd.read_csv('/Users/lpereda/code/munjik/wbanalysis/wbanalysis/raw_data/data_2.csv')
    df.dropna(inplace=True)
    df.rename(columns={'Buy =1 DontBuy = 0': 'Purchase'}, inplace=True)
    df.drop(columns=['symbol', 'Dividend Yeild'], inplace=True)
    #print('all things have dropped')
    #print(df.head(3))
    #print(f'Before X --> {df.keys}')
    # features of X and create target y
    X = df.drop(columns=['Purchase'])
    #print(f'After X --> {df.keys}')
    #print(X.shape)
    #print(X.keys())
    #print(df['Purchase'].keys)
    y = df['Purchase']
    #print(y.shape)
    #print(y)
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=.3,
                                                        random_state=472317128)
    trainer = Trainer(X=X_train, y=y_train)
    trainer.run()
    score = trainer.evaluate(X_test, y_test)
    print(f"score: {score}")
    saved_local = trainer.save_model()
    model_to_gcp = storage_upload()
