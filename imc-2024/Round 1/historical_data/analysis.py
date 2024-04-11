import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import stdev, linear_regression, correlation
from collections import deque

df2 = pd.read_csv("prices_round_1_day_0.csv", header = 0, sep=";")
df1 = pd.read_csv("prices_round_1_day_-1.csv", header = 0, sep=";")
df0 = pd.read_csv("prices_round_1_day_-2.csv", header = 0, sep=";")

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

amethyst_spreads = []
starfruit_spreads = []

indicators = []
lookback = 12

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
            y_starfruit.append(row['mid_price'])
            starfruit_spreads.append(row['ask_price_1'] - row['bid_price_1'])

            if len(prev_starfruit) < lookback + 1:
                prev_starfruit.append(row['mid_price'])
                prev_time.append(row['timestamp'])
                pred_starfruit.append(row['mid_price'])
                indicators.append(0)
            else:
                prev_starfruit_percentages = [(prev_starfruit[i + 1] - prev_starfruit[i])/prev_starfruit[i] + 1 for i in range(len(prev_starfruit) - 1)]
                # print(prev_starfruit_percentages)
                m, b = linear_regression(list(prev_time)[1:], prev_starfruit_percentages)
                try:
                    corr = correlation(list(prev_time)[1:], prev_starfruit_percentages) ** 2
                except:
                    corr = 1
                corrs.append(corr)
                pred = (m * row['timestamp'] + b) * prev_starfruit[-1]
                # print(m * row['timestamp'] + b, pred)
                pred_starfruit.append(pred)
                error = abs(pred - row['mid_price'])
                errors.append(error)

                if error == 0:
                    indicators.append(row['mid_price'] + 30)
                else:
                    indicators.append(0)



                # print(pred, row['mid_price'], error, corr)

                prev_starfruit.popleft()
                prev_time.popleft()
                prev_starfruit.append(row['mid_price'])
                prev_time.append(row['timestamp'])

                
            

    adj += 1000000




print("lookback:", lookback)
print("avg corr:", str(sum(corrs)/len(corrs)))
print("avg error:", str(sum(errors)/len(errors)))
z = [i for i in errors if i < 0.3]
print("accuracy:", str(len(z)/len(errors)))
print()


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
plt.scatter(x_starfruit, bid_starfruit, label='starfruit_bid')
plt.scatter(x_starfruit, ask_starfruit, label='starfruit_ask')
# plt.plot(x_starfruit, y_starfruit, label='starfruit_mid')
plt.scatter(x_starfruit, pred_starfruit, label='starfruit_pred')



plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()
