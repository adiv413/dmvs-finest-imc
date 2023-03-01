#THERE MUST BE A LOG.TXT FILE WHICH COMES FROM PUTTING THE DATAPULLER.PY INTO THE CODE TESTER
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#create a function called processLog that takes a string as its argument to read the file. Make sure that the parameters explicity state it is a string
def processLog(filename: str):
    #read the log file
    with open(filename, 'r') as f:
        lines = f.readlines()
    #split every line by comma
    lines = [line.strip().split(',') for line in lines]
    #find the most common length of the lines
    lengths = [len(line) for line in lines]
    length = max(set(lengths), key=lengths.count)
    #remove the lines that are not the most common length
    lines = [line for line in lines if len(line) == length]
    #strip the \n from the end of the last item in each line
    # turn lines into a dataframe
    df = pd.DataFrame(lines)    

    #rename the columns to timestamp, product, best_ask, best_ask_volume, best_bid, best_bid_volume, spread
    df.columns = ['timestamp', 'product', 'best_ask', 'best_ask_volume', 'best_bid', 'best_bid_volume', 'spread']
    #change the time of timestamp, best_ask, best_ask_volume, best_bid, best_bid_volume, spread to a float.
    df['timestamp'] = df['timestamp'].astype(float)
    df['best_ask'] = df['best_ask'].astype(float)
    df['best_ask_volume'] = df['best_ask_volume'].astype(float)
    df['best_bid'] = df['best_bid'].astype(float)
    df['best_bid_volume'] = df['best_bid_volume'].astype(float)
    df['spread'] = df['spread'].astype(float)
    #get a list of the individual products

    #add a column called average_price that is the average of best_ask and best_bid
    df['average_price'] = (df['best_ask'] + df['best_bid'])/2
    #make the timestamp the index
    df.set_index('timestamp', inplace=True)


    prodnames = df['product'].unique()
    #make a new df for each product
    products = []
    for ptype in prodnames:
        products.append(df[df['product'] == ptype])
    #save each df as a csv file
    return products

def calcSMA(product, period):
    #calculate the simple moving average for each product
    return product['average_price'].rolling(period).mean()

def plot_product(product): #return ax
    ax = plt.figure()
    #plot the average price of each product
    plt.plot(product['average_price'])
    plt.title(product['product'][0.0])
    # set the y axis from 0 to the max*1.1
    plt.ylim(product['average_price'].min()*0.99, product['average_price'].max()*1.01)
    plt.xlabel('time')
    plt.ylabel('price')
    #plt.show()
    return ax

def overlay_sma(ax, period, product):
    #plot the sma on top of the average price
    sma = calcSMA(product, period)
    plt.plot(sma, color='red')
    return ax
def calc_volatility(product):
    s = 0
    print(product)
    l = product['average_price'].tolist()
    mean = sum(l) / len(l)
    for i in range(0, len(product)):
        s += abs(l[i] - mean) ** 2
    return s / (len(product) - 1)
    volatility = sum([abs(product['average_price'][j] - product['average_price'][j - 1]) ** 2 for j in range(len(product), 1, -1)])

def calc_RSI(product):
    #calculate the relative strength index for each product
    #calculate the change in price from one time step to the next
    delta = product['average_price'].diff()
    #calculate the up and down moves
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    #calculate the average gain and average loss
    avg_gain = up.rolling(14).mean()
    avg_loss = down.abs().rolling(14).mean()
    #calculate the relative strength
    relative_strength = avg_gain / avg_loss
    #calculate the relative strength index
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))

    #calculate the buy and sell signals
    buy = []
    sell = []
    signal = 0
    for i in range(len(rsi)):
        if rsi[i] > 70:
            sell.append(rsi[i])
            buy.append(np.nan)
            signal = 0
        elif rsi[i] < 30:
            buy.append(rsi[i])
            sell.append(np.nan)
            signal = 1
        else:
            buy.append(np.nan)
            sell.append(np.nan)

def plot_spread(product):
    #plot the spread of each product
    plt.plot(product['spread'])
    plt.title(product['product'][0.0])
    # set the y axis from 0 to the max*1.1
    plt.ylim(product['spread'].min()*0.90, product['spread'].max()*1.10)
    plt.xlabel('time')
    plt.ylabel('price')
    #plt.show()

if __name__ == '__main__':
    products = processLog('log.txt')
    ax = plot_product(products[0])
    # ax = overlay_sma(ax, 500, products[0])
    # ax = overlay_sma(ax, 200, products[0])
    ax = plot_spread(products[0])
    # ax2 = plot_spread(products[1])
    # ax2 = plot_product(products[1])
    print(calc_volatility(products[0]), calc_volatility(products[1]))
    
    #show both
    plt.show()

