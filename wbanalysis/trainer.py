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
from app import imputer, onehotencode
import pandas as pd
from gcp import get_data_from_gcp

# read our Dataframe until we load it into the GCP
# df = pd.read_csv('/Users/munjismac/code/munjik/wbanalysis/raw_data/CompanyData-Data.csv')
df = get_data_from_gcp()

class Trainer(object):
    def __init__(self, X, y):
        #  X: pandas DataFrame
        #  y: pandas Series
        self.X = X
        self.y = y
        self.knn_model = None

    def set_pipeline(self):
        scaler_pipe = Pipeline([
            ('scaler', RobustScaler())
        ])
        preproc_pipe = ColumnTransformer([
            ('num', scaler_pipe, [
                "calendarYear",
                "GPM",
                "A (SGA)",
                "B (RD)",
                "C (PPE)",
                "D (DEPR)",
                "E (CAPEX)",
                "F (NR)",
                "currentRatio",
                "G (ROA)",
                "H (LD/GP)",
                "debtToEquity",
                "Net Issuance",
                "Interest - income"
            ]),
        ])
        self.knn_model = Pipeline([
            ('preproc', preproc_pipe),
            ('knn',  KNeighborsClassifier(n_neighbors=10))
        ])

    def run(self):
        self.set_pipeline()
        self.knn_model.fit(self.X, self.y)

    # def build_model(self):
    #     """ defines our model as a class asttribute"""
    #     model =  KNeighborsClassifier(n_neighbors=10)
    #     return model

    # def run(self):
    #     self.knn_model = self.build_model()
    #     self.knn_model.fit(self.X,self.y)

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

    def save_model(self):
        joblib.dump(self.knn_model, 'model.joblib')
        print(colored("model.joblib saved locally", "green"))

if __name__ == "__main__":
    clean_data = imputer(df)
    final_df = onehotencode(clean_data)
    # features of X and create target y
    X = final_df.drop(columns=['Buy =1'])
    y = final_df['Buy =1']
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = .3, random_state=0)
    trainer = Trainer(X=X_train, y=y_train)
    trainer.run()
    score = trainer.evaluate(X_test, y_test)
    # print(f"score: {score}")
    trainer.save_model()
