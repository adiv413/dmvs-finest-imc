import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("mm_mcginley_4_7.csv", header = 0, sep=";")

x_amethysts = []
y_amethysts = []
x_starfruit = []
y_starfruit = []
for index, row in df.iterrows():
    if(row['product'] == "AMETHYSTS"):
        x_amethysts.append(row['timestamp'])
        y_amethysts.append(row['profit_and_loss'])
    else:
        x_starfruit.append(row['timestamp'])
        y_starfruit.append(row['profit_and_loss'])

plt.plot(x_amethysts, y_amethysts, label='amethysts_pnl')
plt.plot(x_amethysts, y_starfruit, label='starfruit_pnl')
plt.figure(figsize=(20, 6))
plt.xlabel('timestamp')
plt.ylabel('pnl')
plt.legend()
plt.show()
