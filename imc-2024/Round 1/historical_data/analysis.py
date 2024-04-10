import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import stdev

df2 = pd.read_csv("prices_round_1_day_0.csv", header = 0, sep=";")
df1 = pd.read_csv("prices_round_1_day_-1.csv", header = 0, sep=";")
df0 = pd.read_csv("prices_round_1_day_-2.csv", header = 0, sep=";")

x_amethysts = []
bid_amethysts = []
x_starfruit = []
bid_starfruit = []

ask_amethysts = []

ask_starfruit = []


amethyst_spreads = []
starfruit_spreads = []

adj = 0

for d in [df0, df1, df2]:
    for index, row in d.iterrows():
        if(row['product'] == "AMETHYSTS"):
            x_amethysts.append(row['timestamp'] + adj)
            bid_amethysts.append(row['bid_price_1'])
            ask_amethysts.append(row['ask_price_1'])

            amethyst_spreads.append(row['ask_price_1'] - row['bid_price_1'])
        else:
            x_starfruit.append(row['timestamp'] + adj)
            bid_starfruit.append(row['bid_price_1'])
            ask_starfruit.append(row['ask_price_1'])
            starfruit_spreads.append(row['ask_price_1'] - row['bid_price_1'])

    adj += 1000000



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
plt.plot(x_starfruit, bid_starfruit, label='starfruit_bid')
plt.plot(x_starfruit, ask_starfruit, label='starfruit_ask')

plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()