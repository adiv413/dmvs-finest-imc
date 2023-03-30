import pandas as pd
import matplotlib.pyplot as plt

#make a horizontally long plot
plt.rcParams["figure.figsize"] = (10, 5)

# plt.rcParams["figure.figsize"] = (20, 10)
# #read price1, price2, and price3.csv
# price1 = pd.read_csv('price1.csv', sep = ';')
# price2 = pd.read_csv('price2.csv', sep = ';')
# price3 = pd.read_csv('price3.csv', sep = ';')
price1 = pd.read_csv("Round 5/Data Analysis/Market Traders/price1.csv", sep = ';')
price2 = pd.read_csv("Round 5/Data Analysis/Market Traders/price2.csv", sep = ';')
price3 = pd.read_csv("Round 5/Data Analysis/Market Traders/price3.csv", sep = ';')

price2['timestamp'] = price2['timestamp'] + price1['timestamp'].max() + 100
price3['timestamp'] = price3['timestamp'] + price2['timestamp'].max() + 100

combined = pd.concat([price1, price2, price3])

trades1 = pd.read_csv("Round 5/Data Analysis/Market Traders/trades1.csv", sep = ';')
trades2 = pd.read_csv("Round 5/Data Analysis/Market Traders/trades2.csv", sep = ';')
trades3 = pd.read_csv("Round 5/Data Analysis/Market Traders/trades3.csv", sep = ';')

trades2['timestamp'] = trades2['timestamp'] + price1['timestamp'].max() + 100
trades3['timestamp'] = trades3['timestamp'] + price2['timestamp'].max() + 100

combinedTrades = pd.concat([trades1, trades2, trades3])

#make combinedTrades and combined into only timestamps 1300000 to 1500000
combined = combined[combined['timestamp'] >= 1300000]
combined = combined[combined['timestamp'] <= 1500000]
combinedTrades = combinedTrades[combinedTrades['timestamp'] >= 1300000]
combinedTrades = combinedTrades[combinedTrades['timestamp'] <= 1500000]


productCharts = {item:combined[combined['product'] == item] for item in combined['product'].unique() if item != 'DOLPHIN_SIGHTINGS'}
buyOrders = {buyer:combinedTrades[combinedTrades['buyer'] == buyer] for buyer in combinedTrades['buyer'].unique()}
sellOrders = {seller:combinedTrades[combinedTrades['seller'] == seller] for seller in combinedTrades['seller'].unique()}

traders = traders = ['Paris', 'Charlie', 'Caesar', 'Penelope', 'Camilla', 'Pablo', 'Gina', 'Gary', 'Peter', 'Olivia']
products = ['PINA_COLADAS', 'DIP', 'BAGUETTE', 'PICNIC_BASKET', 'BERRIES', 'DIVING_GEAR', 'BANANAS', 'COCONUTS', 'PEARLS', 'UKULELE']

def show_plots_for_product(product):
    productTraders = [trader for trader in traders if product in buyOrders[trader]['symbol'].unique() or product in sellOrders[trader]['symbol'].unique()]
    plotType = "loop"
    if plotType == 'all':
        fig, axs = plt.subplots(len(productTraders), 1, sharex = True)
        for i in range(len(productTraders)):
            axs[i].plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            axs[i].set_title(productTraders[i])
            buyTrades = buyOrders[productTraders[i]]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[productTraders[i]]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs[i].axvline(buyTrades.iloc[j]['timestamp'], color='g')
            for j in range(len(sellTrades)):
                axs[i].axvline(sellTrades.iloc[j]['timestamp'], color='r')
        plt.show()
    elif plotType == 'spec':
        print('Available traders: ', productTraders)
        trader = input('Enter trader name: ')
        if trader in traders:
            fig, axs = plt.subplots(1, 1, sharex = True)
            axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            axs.set_title(f'{trader} trading {product}')
            buyTrades = buyOrders[trader]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[trader]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs.axvline(buyTrades.iloc[j]['timestamp'], color='g')
            for j in range(len(sellTrades)):
                axs.axvline(sellTrades.iloc[j]['timestamp'], color='r')
            plt.show()
    elif plotType == 'loop':
        for trader in productTraders:
            fig, axs = plt.subplots(1, 1, sharex = True)
            axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            axs.set_title(f'{trader} trading {product}')
            buyTrades = buyOrders[trader]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[trader]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs.axvline(buyTrades.iloc[j]['timestamp'], color='g')
            for j in range(len(sellTrades)):
                axs.axvline(sellTrades.iloc[j]['timestamp'], color='r')
            plt.show()

def show_points_for_product(product): #same thing as above but with points instead of lines
    productTraders = [trader for trader in traders if product in buyOrders[trader]['symbol'].unique() or product in sellOrders[trader]['symbol'].unique()]
    plotType = "loop"
    if plotType == 'all':
        fig, axs = plt.subplots(len(productTraders), 1, sharex = True)
        for i in range(len(productTraders)):
            # axs[i].plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            #plot with transparent color of grey
            axs[i].scatter(productCharts[product]['timestamp'], productCharts[product]['mid_price'], color = 'grey', alpha = 0.5)
            axs[i].set_title(f'{productTraders[i]} trading {product}')
            buyTrades = buyOrders[productTraders[i]]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[productTraders[i]]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs[i].scatter(buyTrades.iloc[j]['timestamp'], buyTrades.iloc[j]['price'], color = 'g')
            for j in range(len(sellTrades)):
                axs[i].scatter(sellTrades.iloc[j]['timestamp'], sellTrades.iloc[j]['price'], color = 'r')
        plt.show()
    elif plotType == 'spec':
        print('Available traders: ', traders)
        trader = "Paris"
        if trader in traders:
            fig, axs = plt.subplots(1, 1, sharex = True)
            # axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            # plot with transparent color of grey
            axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'], color = 'grey', alpha = 0.5)
            # axs.set_title(trader)
            axs.set_title(f'{trader} trading {product}')
            buyTrades = buyOrders[trader]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[trader]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs.scatter(buyTrades.iloc[j]['timestamp'], buyTrades.iloc[j]['price'], color = 'g')
                print(f'BUY: {buyTrades.iloc[j]["quantity"]} x {buyTrades.iloc[j]["price"]}')
            for j in range(len(sellTrades)):
                axs.scatter(sellTrades.iloc[j]['timestamp'], sellTrades.iloc[j]['price'], color = 'r')
                print(f'SELL: {sellTrades.iloc[j]["quantity"]} x {sellTrades.iloc[j]["price"]}')

            plt.show()
    elif plotType == 'loop':
        for trader in productTraders:
            fig, axs = plt.subplots(1, 1, sharex = True)
            # axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'])
            # plot with transparent color of grey
            # axs.plot(productCharts[product]['timestamp'], productCharts[product]['mid_price'], color = 'grey', alpha = 0.5)
            #plot the bid and ask prices instead of mid price
            axs.plot(productCharts[product]['timestamp'], productCharts[product]['bid_price_1'], color = 'blue', alpha = 0.5)
            axs.plot(productCharts[product]['timestamp'], productCharts[product]['ask_price_1'], color = 'purple', alpha = 0.5)
            # axs.set_title(trader)
            axs.set_title(f'{trader} trading {product}')
            buyTrades = buyOrders[trader]
            buyTrades = buyTrades[buyTrades['symbol'] == product]
            sellTrades = sellOrders[trader]
            sellTrades = sellTrades[sellTrades['symbol'] == product]
            for j in range(len(buyTrades)):
                axs.scatter(buyTrades.iloc[j]['timestamp'], buyTrades.iloc[j]['price'], color = 'g')
            for j in range(len(sellTrades)):
                axs.scatter(sellTrades.iloc[j]['timestamp'], sellTrades.iloc[j]['price'], color = 'r')
            plt.show()

while True:
    user_spec = input('Enter product name: ')
    # show_plots_for_product(user_spec)
    show_points_for_product(user_spec)

# print(productCharts["BANANAS"].head())
