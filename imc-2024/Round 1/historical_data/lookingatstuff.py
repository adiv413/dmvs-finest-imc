
import pandas as pd
import json
import matplotlib.pyplot as plt

def pullData(path):

    with open(path) as f:
        content = f.read()
    products = ["AMETHYSTS", "STARFRUIT"]


    split_content = content.split('\n')
    #remove the last line, which is empty
    split_content = split_content[:-1]
    #day;timestamp;product;bid_price_1;bid_volume_1;bid_price_2;bid_volume_2;bid_price_3;bid_volume_3;ask_price_1;ask_volume_1;ask_price_2;ask_volume_2;ask_price_3;ask_volume_3;mid_price;profit_and_loss
    productData = {}
    for product in products:
        productData[product] = []
        productData[product].append(split_content[0].split(';'))

    for line in split_content[1:]:
        line = line.split(';')
        product = line[2]
        productData[product].append(line)

    for product in products:
        productData[product] = pd.DataFrame(productData[product][1:], columns=productData[product][0])

    for product in products:
        productData[product]['timestamp'] = productData[product]['timestamp'].astype(int)
        productData[product] = productData[product].set_index('timestamp')

    for product in products:
        for column in productData[product].columns:
            if column != 'product':
                #some of these columns have empty values in some of the rows, so we need to make those NaN, and the rest ints
                productData[product][column] = pd.to_numeric(productData[product][column], errors='coerce')
    for product in products:
        productData[product]['spread'] = productData[product]['ask_price_1'] - productData[product]['bid_price_1']
        productData[product]['price'] = (productData[product]['ask_price_1'] + productData[product]['bid_price_1'])/2

    return productData


def plot_spreads(products): #should plot on different graphs
    for product in products:
        plt.plot(products[product]['spread'])
        plt.title(f'{product} Spread')
        plt.show()

def plot_prices(products): #should plot on different graphs, price should be actual, not 1e^something
    for product in products:
        plt.plot(products[product]['price'])
        plt.title(f'{product} Price')
        plt.show()

def plot_bid1_bid2_ask1_ask2(products):
    for product in products:
        plt.plot(products[product]['price'], color='black')
        plt.plot(products[product]['bid_price_1'], color='blue')
        plt.plot(products[product]['bid_price_2'], color='lightblue')
        plt.plot(products[product]['ask_price_1'], color='red')
        plt.plot(products[product]['ask_price_2'], color='lightcoral')
        plt.title(f'{product} Bid1, Bid2, Ask1, Ask2')
        plt.show()

def plot_secondary_spread(products):
    #if the volume of bid1 is less than 20, use the price of bid2 as the reference for the spread.
    #do the same for ask1 and ask2
    #you need to also check to see if bid2 and ask2 are not empty, which should be a NaN value
    for product in products:
        spread = []
        
        spread = []
        for timestamp in products[product].index:
            effective_bid = -1
            effective_ask = -1
            if products[product]['bid_volume_1'][timestamp] < 20 and not pd.isnull(products[product]['bid_price_2'][timestamp]):
                effective_bid = products[product]['bid_price_2'][timestamp]
            else:
                effective_bid = products[product]['bid_price_1'][timestamp]
            if products[product]['ask_volume_1'][timestamp] < 20 and not pd.isnull(products[product]['ask_price_2'][timestamp]):
                effective_ask = products[product]['ask_price_2'][timestamp]
            else:
                effective_ask = products[product]['ask_price_1'][timestamp]
            
            spread.append(effective_ask - effective_bid)
        plt.plot(spread)
        plt.title(f'{product} Effective Spread')
        plt.show()

def RSI(product_df, period=14):
    #copy just the price column into a new df called RSI_DF
    RSI_DF = product_df[['price']].copy()
    #add a column to RSI_DF called delta, which is the difference between the current price and the previous price
    RSI_DF['delta'] = RSI_DF['price'].diff()
    RSI_DF['gains'] = RSI_DF['delta'].apply(lambda x: x if x > 0 else 0)
    RSI_DF['losses'] = RSI_DF['delta'].apply(lambda x: -x if x < 0 else 0)
    RSI_DF['avg_gain'] = RSI_DF['gains'].rolling(window=period).mean()
    RSI_DF['avg_loss'] = RSI_DF['losses'].rolling(window=period).mean()
    RSI_DF['RS'] = RSI_DF['avg_gain'] / RSI_DF['avg_loss']
    RSI_DF['RSI'] = 100 - (100 / (1 + RSI_DF['RS']))
    print(RSI_DF.head())
    #put it into a plot with price above and RSI below. Make RSI red when it's above 70 and green when it's below 30
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(RSI_DF['price'])
    ax[1].plot(RSI_DF['RSI'])
    ax[1].axhline(y=70, color='r', linestyle='--')
    ax[1].axhline(y=30, color='g', linestyle='--')
    plt.show()
    #instead of doing the above, divide it into 20 intervals of equal size and do that for each interval

def plot_price_bid1_ask1(products):
    for product in products:
        # plt.plot(products[product]['price'], color='black')
        plt.plot(products[product]['bid_price_1'])
        plt.plot(products[product]['ask_price_1'])
        plt.title(f'{product} Price, Bid1, Ask1')
        plt.show()

def SMA(product_df, period=5):
    #graph the price and the SMA
    SMA_DF = product_df[['price']].copy()
    SMA_DF['SMA'] = SMA_DF['price'].rolling(window=period).mean()
    print(SMA_DF.head())
    plt.plot(SMA_DF['price'])
    plt.plot(SMA_DF['SMA'])
    plt.show() 

def HMA(product_df, period = 20):
    #graph the price and the HMA
    HMA_DF = product_df[['price']].copy()
    HMA_DF['WMA'] = HMA_DF['price'].rolling(window=period).mean()
    HMA_DF['WMA2'] = HMA_DF['price'].rolling(window=period//2).mean()
    HMA_DF['HMA'] = 2*HMA_DF['WMA'] - HMA_DF['WMA2']
    print(HMA_DF.head())
    plt.plot(HMA_DF['price'])
    plt.plot(HMA_DF['HMA'])
    plt.show()

def SMMA(product_df, period = 20):
    #graph the price and the SMMA (Smoothed moving average)
    SMMA_DF = product_df[['price']].copy()
    SMMA_DF['SMMA'] = SMMA_DF['price'].ewm(span=period).mean()
    print(SMMA_DF.head())
    plt.plot(SMMA_DF['price'])
    plt.plot(SMMA_DF['SMMA'])
    plt.show()
def custom_MA(product_df, period1 = 10, period2 = 100):
    #copy the bid, ask, and price columns into a new df called MA_DF
    MA_DF = product_df[['price', 'bid_price_1', 'ask_price_1', 'spread']].copy()
    #calculate the moving average with length period, but only use the price if the spread is greater than 4
    rolling_window = []
    for row, timestamp in enumerate(MA_DF.index):
        if len(rolling_window) < period1 and MA_DF['spread'][timestamp] > 4:
            rolling_window.append(MA_DF['price'][timestamp])
        elif len(rolling_window) == period1 and MA_DF['spread'][timestamp] > 4:
            rolling_window.pop(0)
            rolling_window.append(MA_DF['price'][timestamp])
        if len(rolling_window) == period1:
            MA_DF.at[timestamp, 'MA'] = sum(rolling_window) / period1
    # now graph the price and the MA
    print(MA_DF.head())
    # plt.plot(MA_DF['price'])
    #plot bid and ask
    #make a longer EMA using the 50 period
    MA_DF['EMA1'] = MA_DF['price'].ewm(span=period2).mean()
    # plt.plot(MA_DF['bid_price_1'])
    # plt.plot(MA_DF['ask_price_1'])
    # plt.plot(MA_DF['MA'])
    # plt.plot(MA_DF['EMA'])
    # #make a column for the difference between MA and EMA
    MA_DF['diff'] = MA_DF['EMA1'] - MA_DF['MA']
    # make a vertically stacked graph, one with ask and bid and both moving averages, and one with the difference between the two
    #in the second graph, make horizontal lines at -1 and 1
    fig, ax = plt.subplots(2, 1)
    # ax[0].plot(MA_DF['price'])
    ax[0].plot(MA_DF['MA'])
    ax[0].plot(MA_DF['EMA1'])
    ax[0].plot(MA_DF['bid_price_1'])
    ax[0].plot(MA_DF['ask_price_1'])
    ax[1].plot(MA_DF['diff'])
    ax[1].axhline(y=1, color='r', linestyle='--')
    ax[1].axhline(y=-1, color='r', linestyle='--')
    plt.show()




paths = ["prices_round_1_day_-2.csv", "prices_round_1_day_-1.csv", "prices_round_1_day_0.csv"]
#paths = ["imc-2024\Round 1\historical_data\91ba4cbd-c7ee-4fd6-b127-788638cb662f.csv"]
days = []
for path in paths:
    days.append(pullData(path))

# plot prices of each day for just starfruit
# for day in days:
#     plot_price_bid1_ask1({"STARFRUIT": day["STARFRUIT"]})

# HMA(days[0]["STARFRUIT"], 50)
#graph the spread of starfruit
# plot_spreads({"STARFRUIT": days[0]["STARFRUIT"]})

#custom_MA(days[0]["STARFRUIT"])
#plot_spreads({"STARFRUIT": days[0]["STARFRUIT"]})
plot_prices({"STARFRUIT": days[0]["STARFRUIT"]})