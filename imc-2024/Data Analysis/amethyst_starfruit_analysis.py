import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("amethyst_starfruit.csv", header = 0, sep=";")

x_amethysts = []
y_amethysts = []
x_starfruit = []
y_starfruit = []
for index, row in df.iterrows():
    if(row['product'] == "AMETHYSTS"):
        x_amethysts.append(row['timestamp'])
        y_amethysts.append(row['mid_price'])
    else:
        x_starfruit.append(row['timestamp'])
        y_starfruit.append(row['mid_price'])

plt.figure(figsize=(20, 6))
plt.plot(x_amethysts, y_amethysts, label='amethysts_price')
plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()
plt.plot(x_starfruit, y_starfruit, label='starfruit_price')
plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()