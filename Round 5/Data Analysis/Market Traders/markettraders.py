import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20, 10)
#read price1, price2, and price3.csv
price1 = pd.read_csv('Round 5/Data Analysis/Market Traders/price1.csv', sep = ';')
price2 = pd.read_csv('Round 5/Data Analysis/Market Traders/price2.csv', sep = ';')
price3 = pd.read_csv('Round 5/Data Analysis/Market Traders/price3.csv', sep = ';')

price2['timestamp'] = price2['timestamp'] + price1['timestamp'].max() + 100
price3['timestamp'] = price3['timestamp'] + price2['timestamp'].max() + 100
combined = pd.concat([price1, price2, price3])
trades1 = pd.read_csv('Round 5/Data Analysis/Market Traders/trades1.csv', sep = ';')
trades2 = pd.read_csv('Round 5/Data Analysis/Market Traders/trades2.csv', sep = ';')
trades3 = pd.read_csv('Round 5/Data Analysis/Market Traders/trades3.csv', sep = ';')

trades2['timestamp'] = trades2['timestamp'] + price1['timestamp'].max() + 100
trades3['timestamp'] = trades3['timestamp'] + price2['timestamp'].max() + 100
combinedTrades = pd.concat([trades1, trades2, trades3])
productCharts = {item:combined[combined['product'] == item] for item in combined['product'].unique() if item != 'DOLPHIN_SIGHTINGS'}
buyOrders = {buyer:combinedTrades[combinedTrades['buyer'] == buyer] for buyer in combinedTrades['buyer'].unique()}
sellOrders = {seller:combinedTrades[combinedTrades['seller'] == seller] for seller in combinedTrades['seller'].unique()}
traders = ["Peter", "Mitch", "Gary", "Penelope", "Omar", "Camilla", "Caesar", "Giulia", "Mabel", "Charlie", "Pablo", "Olivia", "Orson", "Casey", "George", "Mya", "Max", "Paris", "Gina", "Olga"]
products = ['PINA_COLADAS', 'DIP', 'BAGUETTE', 'PICNIC_BASKET', 'BERRIES', 'DIVING_GEAR', 'BANANAS', 'COCONUTS', 'PEARLS', 'UKULELE']
#PEARLS
#plot the mid_price of pearls n times if n is the number of traders
#for each chart, place a green line when a buyer makes a trade and a red line when a seller makes a trade. Loop through each trader

products_olivia = ["BANANAS", "UKULELE", "BERRIES"]

# raw_traders = ["Peter", "Mitch", "Gary", "Penelope", "Omar", "Camilla", "Caesar", "Giulia", "Mabel", "Charlie", "Pablo", "Olivia", "Orson", "Casey", "George", "Mya", "Max", "Paris", "Gina", "Olga"]
# traders = {}
# for i in raw_traders:
#     traders[i] = {"products" : [], "product_count" : 0}

# for product in products:
#     product_traders = [trader for trader in traders if trader in buyOrders and product in buyOrders[trader]['symbol'].unique() or trader in sellOrders and product in sellOrders[trader]['symbol'].unique()]
#     print(product, "traders:", product_traders)
#     for t in product_traders:
#         traders[t]["products"].append(product)
#         traders[t]["product_count"] += 1

# from pprint import pprint
# pprint(traders)
for product in products_olivia:
    product_traders = [trader for trader in traders if trader in buyOrders and product in buyOrders[trader]['symbol'].unique() or trader in sellOrders and product in sellOrders[trader]['symbol'].unique()]

    print(product_traders)
    for i in [product_traders.index("Olivia")]:
        plt.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
        plt.title(product_traders[i])
        buyTrades = buyOrders[product_traders[i]]
        buyTrades = buyTrades[buyTrades['symbol'] == product]
        for j in range(len(buyTrades)):
            plt.axvline(x=buyTrades['timestamp'].iloc[j], color='green')
        sellTrades = sellOrders[product_traders[i]]
        sellTrades = sellTrades[sellTrades['symbol'] == product]
        for j in range(len(sellTrades)):
            plt.axvline(x=sellTrades['timestamp'].iloc[j], color='red')
        plt.show()


    
