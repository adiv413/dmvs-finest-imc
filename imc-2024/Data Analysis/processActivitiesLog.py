
import pandas as pd
import json
import matplotlib.pyplot as plt

def pullData():

    with open('imc-2024/Data Analysis/logs/log2.log') as f:
        content = f.read()
    content = content[content.index('Activities log:')+15:]
    products = ["AMETHYSTS", "STARFRUIT"]


    split_content = content.split('\n')[1:]
    for i in range(len(split_content)):
        if split_content[i] == '':
            split_content = split_content[:i]
            break
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
        plt.plot(products[product]['bid_price_1'])
        plt.plot(products[product]['bid_price_2'])
        plt.plot(products[product]['ask_price_1'])
        plt.plot(products[product]['ask_price_2'])
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


products = pullData()
amethysts = products['AMETHYSTS']
starfruit = products['STARFRUIT']
# plot_spreads(products)
plot_secondary_spread(products)