
import pandas as pd
import json
import matplotlib.pyplot as plt

def pullData():

    with open('imc-2024/Data Analysis/logs/run.log') as f:
        content = f.read()
    
    split_content = content.split('}\n{')
    split_content[0] = split_content[0][split_content[0].index('\n')+2:]
    split_content = ['{' + x + '}' for x in split_content]
    split_content[-1] = split_content[-1][:-1]

    data = []
    for i in split_content:
        data.append(json.loads(i).get('lambdaLog'))
    data = [x.split('\n') for x in data]
    data = [[y.split(',') for y in x] for x in data]
    lengths = [len(x) for x in data]
    index = lengths.index(1)
    data.pop(index)
    num_products = len(data[0])
    productData = {}
    for n in range(num_products):
        df = pd.DataFrame([x[n] for x in data])
        df.columns = ['timestamp', 'product', 'best_ask', 'best_ask_volume', 'best_bid', 'best_bid_volume', 'spread']
        #set the types of the columns, they are all int except for product
        df['timestamp'] = df['timestamp'].astype(int)
        df['best_ask'] = df['best_ask'].astype(int)
        df['best_ask_volume'] = df['best_ask_volume'].astype(int)
        df['best_bid'] = df['best_bid'].astype(int)
        df['best_bid_volume'] = df['best_bid_volume'].astype(int)
        df['spread'] = df['spread'].astype(int)

        df['price'] = (df['best_ask'] + df['best_bid'])/2
        productData[df['product'][0][1:]] = df

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


products = pullData()
amethysts = products['AMETHYSTS']
starfruit = products['STARFRUIT']
plot_prices(products)