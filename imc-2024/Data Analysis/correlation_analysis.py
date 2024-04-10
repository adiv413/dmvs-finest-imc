import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy
import statsmodels.api as sm
import pickle as pkl
import math
from sklearn.linear_model import LinearRegression

lag0 = pd.read_csv("round-1-island-data-bottle/prices_round_1_day_0.csv", header = 0, sep=";")
lag1 = pd.read_csv("round-1-island-data-bottle/prices_round_1_day_-1.csv", header = 0, sep=";")
lag2 = pd.read_csv("round-1-island-data-bottle/prices_round_1_day_-2.csv", header = 0, sep=";")

amethyst_lag0 = []
amethyst_lag1 = []
amethyst_lag2 = []

starfruit_lag0 = []
starfruit_lag1 = []
starfruit_lag2 = []

for index, row in lag0.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag0.append(row['mid_price'])
    else:
        starfruit_lag0.append(row['mid_price'])

for index, row in lag1.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag1.append(row['mid_price'])
    else:
        starfruit_lag1.append(row['mid_price'])

for index, row in lag2.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag2.append(row['mid_price'])
    else:
        starfruit_lag2.append(row['mid_price'])


X = pd.DataFrame()
X['lagged_1'] = starfruit_lag1
X['lagged_2'] = starfruit_lag2
X['pred'] = starfruit_lag0

predictors = X[['lagged_1', 'lagged_2']]
#predictors = X[['lagged_1', 'lagged_2']]
y = X['pred']

sreg = sm.OLS(y, predictors)
mod = sreg.fit()
print(mod.summary())