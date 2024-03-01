import pandas as pd
import matplotlib.pyplot as plt
from math import log

plt.rcParams["figure.figsize"] = (20,10)

price1 = pd.read_csv("Round 3\diving\price1.csv", sep=";")
price2 = pd.read_csv("Round 3\diving\price2.csv", sep=";")
price3 = pd.read_csv("Round 3\diving\price3.csv", sep=";")
price2.index = price2.index + price1.index[-1] + 100
price3.index = price3.index + price2.index[-1] + 100
combined = pd.concat([price1, price2, price3])
combined = combined.fillna(0)
diving = combined[combined["product"] == "DIVING_GEAR"]
dolphins = combined[combined["product"] == "DOLPHIN_SIGHTINGS"]
diving["total_bid_volume"] = diving["bid_volume_1"] + diving["bid_volume_2"] + diving["bid_volume_3"]
diving["total_ask_volume"] = diving["ask_volume_1"] + diving["ask_volume_2"] + diving["ask_volume_3"]
diving["spread"] = diving["ask_price_1"] - diving["bid_price_1"]
#for dolphin sightings, remove everything except timestamp, product, and mid_pirce
dolphins = dolphins[["product", "mid_price"]]

#make timestamp no longer the index, but a column
diving = diving.reset_index()
dolphins = dolphins.reset_index()

#in vertically stacked plots, show dolphins mid price, diving mid price, diving total volume, and diving spread
# fig, ax = plt.subplots(4, 1, sharex=True)
# ax[0].plot(dolphins["timestamp"], dolphins["mid_price"])
# ax[0].set_title("Dolphin Sightings")
# ax[1].plot(diving["timestamp"], diving["mid_price"])
# ax[1].set_title("Diving Gear")
# ax[2].plot(diving["timestamp"], diving["total_bid_volume"] + diving["total_ask_volume"])
# ax[2].set_title("Total Volume")
# ax[3].plot(diving["timestamp"], diving["spread"])
# ax[3].set_title("Spread")

dolphins["Delta"] = dolphins["mid_price"].diff()
dolphins["DeltaAbs"] = dolphins["Delta"].abs()

dolphinsSorted = dolphins.copy()
#sort by absolute value of delta
dolphinsSorted = dolphinsSorted.sort_values(by="DeltaAbs", ascending=False)
dolphinsSorted = dolphinsSorted[0:4]


WINDOW1 = 100
WINDOW2 = 200

#MAKE THE INDEX COUNT FROM 0, BUT MAKE THE X AXIS SHOW THE ACTUAL TIMESTAMP


#make a two columns with moving averages of the diving gear mid price
diving["MA1"] = diving["mid_price"].rolling(WINDOW1).mean()
diving["MA2"] = diving["mid_price"].rolling(WINDOW2).mean()
#graph the price of diving gears, with vertical lines at the timestamps of the top 5, red if delta is negative, green if positive
fig, ax = plt.subplots(1, 1)
ax.plot(diving.index, diving["mid_price"])
for index, row in dolphinsSorted.iterrows():
    if row["Delta"] < 0:
        ax.axvline(x=index, color="red")
    else:
        ax.axvline(x=index, color="green")
ax.plot(diving.index, diving["MA1"])
ax.plot(diving.index, diving["MA2"])

plt.show()

#trade 1 is good
#trade 2 is good
#trade 3 is good
#trade 4 is good
