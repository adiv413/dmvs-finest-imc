import matplotlib.pyplot as plt

prices = {
    "BANANAS": [],
    "PEARLS": [],
    "COCONUTS": [],
    "BERRIES": [],
    "PINA_COLADAS": [],
    "DIP": [],
    "UKULELE": [],
    "DIVING_GEAR": [],
    "BAGUETTE": [],
    "PICNIC_BASKET": [],
    "DOLPHIN_SIGHTINGS": []
}

with open("prices_round_4_day_1.csv", "r") as f:
    for l in f:
        line = l.split(";")
        key = line[2]
        price = line[15]
        prices[key].append[price]

#Ukulele Graph:

x = prices["UKULELE"]
y = [prices["UKULELE"][i] + prices["DIP"][i] + prices["BAGUETTE"][i] + prices["PICNIC_BASKET"][i] for i in range(len(prices["UKULELE"]))]

plt.scatter(x,y)