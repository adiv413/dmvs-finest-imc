
import pandas as pd
import json
import matplotlib.pyplot as plt

def pullData(path):

    with open(path) as f:
        content = f.read()
    product = "ORCHIDS"
    split_content = content.split('\n')
    #remove the last line, which is empty
    split_content = split_content[:-1]
    #day;timestamp;product;bid_price_1;bid_volume_1;bid_price_2;bid_volume_2;bid_price_3;bid_volume_3;ask_price_1;ask_volume_1;ask_price_2;ask_volume_2;ask_price_3;ask_volume_3;mid_price;profit_and_loss
    productData = {}
    productData[product] = []
    productData[product].append(split_content[0].split(';'))

    for line in split_content[1:]:
        line = line.split(';')
        productData[product].append(line)

    productData[product] = pd.DataFrame(productData[product][1:], columns=productData[product][0])
    productData[product]['timestamp'] = productData[product]['timestamp'].astype(int)
    productData[product] = productData[product].set_index('timestamp')

    for column in productData[product].columns:
        if column != 'product':
            #some of these columns have empty values in some of the rows, so we need to make those NaN, and the rest ints
            productData[product][column] = pd.to_numeric(productData[product][column], errors='coerce')

    # productData[product]['spread'] = productData[product]['ask_price_1'] - productData[product]['bid_price_1']
    # productData[product]['price'] = (productData[product]['ask_price_1'] + productData[product]['bid_price_1'])/2

    return productData

def custom_plot(productData, graph_orchid: bool = True, graph_transport_fees: bool = False, graph_export_tariff: bool = False, graph_import_tariff: bool = False, graph_sunlight: bool = False, graph_humidity: bool = False):
    #create a graph with all of the curves. the column names are timestamp;ORCHIDS;TRANSPORT_FEES;EXPORT_TARIFF;IMPORT_TARIFF;SUNLIGHT;HUMIDITY;DAY
    #overlay them on the same graph, they will have different y axes

    fig, ax1 = plt.subplots()
    # if graph_orchid:
    #     ax1.plot(productData['ORCHIDS'], color='black')
    # if graph_transport_fees:
    #     ax1.plot(productData['TRANSPORT_FEES'], color='blue')
    # if graph_export_tariff:
    #     ax1.plot(productData['EXPORT_TARIFF'], color='green')
    # if graph_import_tariff:
    #     ax1.plot(productData['IMPORT_TARIFF'], color='red')
    # if graph_sunlight:
    #     ax1.plot(productData['SUNLIGHT'], color='purple')
    # if graph_humidity:
    #     ax1.plot(productData['HUMIDITY'], color='orange')
    #the above doesn't work, they're all in different scales
    #make it so that there are several y axes, one for each of the columns
    if graph_orchid:
        ax1.plot(productData['ORCHIDS'], color='black')
        ax1.legend(['ORCHIDS'])
    if graph_transport_fees:
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.plot(productData['TRANSPORT_FEES'], color='blue')
        ax3.legend(['TRANSPORT_FEES'])
    if graph_export_tariff:
        ax4 = ax1.twinx()
        ax4.spines['right'].set_position(('outward', 120))
        ax4.plot(productData['EXPORT_TARIFF'], color='green')
        ax4.legend(['EXPORT_TARIFF'])
    if graph_import_tariff:
        ax5 = ax1.twinx()
        ax5.spines['right'].set_position(('outward', 180))
        ax5.plot(productData['IMPORT_TARIFF'], color='red')
        ax5.legend(['IMPORT_TARIFF'])
    if graph_sunlight:
        ax6 = ax1.twinx()
        ax6.spines['right'].set_position(('outward', 240))
        ax6.plot(productData['SUNLIGHT'], color='purple')
        ax6.legend(['SUNLIGHT'])
    if graph_humidity:
        ax7 = ax1.twinx()
        ax7.spines['right'].set_position(('outward', 300))
        ax7.plot(productData['HUMIDITY'], color='orange')
        ax7.legend(['HUMIDITY'])
    ax1.set_title('ORCHIDS')
    ax1.set_ylabel('Price')
    ax1.set_xlabel('Timestamp')
    plt.show()


paths = ["imc-2024\Round 2\historical_data\prices_round_2_day_-1.csv", "imc-2024\Round 2\historical_data\prices_round_2_day_0.csv", "imc-2024\Round 2\historical_data\prices_round_2_day_1.csv"]
#paths = ["imc-2024\Round 1\historical_data\91ba4cbd-c7ee-4fd6-b127-788638cb662f.csv"]
days = []
for path in paths:
    days.append(pullData(path))

custom_plot(days[0]["ORCHIDS"], graph_export_tariff = True, graph_import_tariff= True, graph_transport_fees=True)
