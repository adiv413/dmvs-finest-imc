import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import stdev, linear_regression, correlation
from collections import deque

df2 = pd.read_csv("temp.csv", header = 0, sep=";")

# df0 = pd.read_csv("lr.csv", header = 0, sep=";")


x_amethysts = []
bid_amethysts = []
x_starfruit = []
bid_starfruit = []
y_starfruit = []
pred_starfruit = []
prev_starfruit = deque()
prev_time = deque()
ask_amethysts = []


ask_starfruit = []
corrs = []
errors = []
profits = []
amethyst_spreads = []
starfruit_spreads = []

indicators = []
lookback = 12

adj = 0
for d in [df2]:
    for index, row in d.iterrows():
        if(row['product'] == "ORCHIDS"):
            x_amethysts.append(row['timestamp'] + adj)

            profits.append(row['profit_and_loss'])
        

    adj += 1000000


# try lookback 10

# print("avg am spread: ", str(sum(amethyst_spreads)/len(amethyst_spreads)))
# print("stddev am spread: ", str(stdev(amethyst_spreads)))

# print("avg st spread: ", str(sum(starfruit_spreads)/len(starfruit_spreads)))
# print("stddev st spread: ", str(stdev(starfruit_spreads)))



# plt.figure(figsize=(20, 6))
# plt.plot(x_amethysts, amethyst_spreads, label='amethysts_price')
# plt.xlabel('timestamp')
# plt.ylabel('price')
# plt.legend()
# plt.show()
plt.plot(x_amethysts, profits, label='profit')
# plt.scatter(x_starfruit, ask_starfruit, label='starfruit_ask')
# # plt.plot(x_starfruit, y_starfruit, label='starfruit_mid')
# plt.scatter(x_starfruit, pred_starfruit, label='starfruit_pred')



plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()
