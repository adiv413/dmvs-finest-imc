#THERE MUST BE A LOG.TXT FILE WHICH COMES FROM PUTTING THE DATAPULLER.PY INTO THE CODE TESTER
import pandas as pd
import matplotlib.pyplot as plt

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

def plot_product(product):
    #plot the average price of each product
    plt.plot(product['average_price'])
    plt.title(product['product'][0.0])
    # set the y axis from 0 to the max*1.1
    plt.ylim(product['average_price'].min()*0.99, product['average_price'].max()*1.01)
    plt.xlabel('time')
    plt.ylabel('price')
    plt.show()

if __name__ == '__main__':
    products = processLog('log.txt')