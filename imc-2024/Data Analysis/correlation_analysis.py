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
starfruit_bestbid = []
starfruit_bestask = []

for index, row in lag0.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag0.append(row['mid_price'])
    else:
        starfruit_lag0.append(row['mid_price'])
        starfruit_bestbid.append(max(row['bid_price_1'], row['bid_price_2'], row['bid_price_3']))
        starfruit_bestask.append(min(row['ask_price_1'], row['ask_price_2'], row['ask_price_3']))

for index, row in lag1.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag1.append(row['mid_price'])
    else:
        starfruit_lag0.append(row['mid_price'])
        starfruit_bestbid.append(max(row['bid_price_1'], row['bid_price_2'], row['bid_price_3']))
        starfruit_bestask.append(min(row['ask_price_1'], row['ask_price_2'], row['ask_price_3']))

for index, row in lag2.iterrows():
    if(row['product'] == "AMETHYSTS"):
        amethyst_lag2.append(row['mid_price'])
    else:
        starfruit_lag0.append(row['mid_price'])
        starfruit_bestbid.append(max(row['bid_price_1'], row['bid_price_2'], row['bid_price_3']))
        starfruit_bestask.append(min(row['ask_price_1'], row['ask_price_2'], row['ask_price_3']))

#starfruit_lag0 = starfruit_lag2 + starfruit_lag1 + starfruit_lag0

X = pd.DataFrame()
#X['lagged_8'] = starfruit_lag0[1:len(starfruit_lag0)-8]
#X['lagged_7'] = starfruit_lag0[2:len(starfruit_lag0)-7]
#X['lagged_6'] = starfruit_lag0[3:len(starfruit_lag0)-6]
#X['lagged_5'] = starfruit_lag0[4:len(starfruit_lag0)-5]
#X['lagged_4'] = starfruit_lag0[5:len(starfruit_lag0)-4]
X['lagged_3'] = starfruit_lag0[6:len(starfruit_lag0)-3]
X['lagged_2'] = starfruit_lag0[7:len(starfruit_lag0)-2]
X['lagged_1'] = starfruit_lag0[8:len(starfruit_lag0)-1]
X['pred'] = starfruit_lag0[9:]

predictors = X[['lagged_1', 'lagged_2', 'lagged_3']]
#predictors = X[['lagged_1', 'lagged_2']]
y = X['pred']

sreg = sm.OLS(y, predictors)
mod = sreg.fit()
print(mod.summary())
'''y_pred = []
x = []
for i in range(len(y)):
    y_pred.append(0.3470*X['lagged_1'][i] + 0.2635*X['lagged_2'][i] + 0.1965*X['lagged_3'][i] + 0.1929*X['lagged_4'][i] )
    x.append(i)
plt.scatter(x[:150], starfruit_bestask[:150], color = 'orange')
plt.scatter(x[:150], starfruit_bestbid[:150], color = 'green')
plt.scatter(x[:150], y_pred[:150], color = 'blue')
plt.show()'''