import matplotlib.pyplot as plt

lines = open("sample.log").readlines()
banana_lines = [lines[i] for i in range(len(lines)) if i % 2 == 0]
pearl_lines = [lines[i] for i in range(len(lines)) if i % 2 == 1]

prices = {
    "asks" : {}, 
    "bids" : {},
    "avg" : {},
    "avg_prices" : {},
    "count" : {} 
}

# load data from log

for product in range(2):
    asks = []
    bids = []
    current_lines = []
    curr_product = ""

    if product % 2 == 0:
        current_lines = banana_lines
        curr_product = "banana"
    else:
        current_lines = pearl_lines
        curr_product = "pearl"

    for i in range(len(current_lines)):
        if product % 2 == 0:
            line = current_lines[i].split(" ")
        else:
            line = current_lines[i].split(" ")

        asks.append(int(line[3][:-1]))
        bids.append(int(line[5][:-1]))

    prices["asks"][curr_product] = asks
    prices["bids"][curr_product] = bids

get_avg_price = lambda x : (prices["asks"][curr_product][x] + prices["bids"][curr_product][x]) / 2 # gets average price at index

# Simple Moving Average (SMA) with window n = 7

products = ["banana", "pearl"]

n = 7

for curr_product in products:
    prices["avg_prices"][curr_product] = [get_avg_price(0)]
    prices["avg"][curr_product] = [get_avg_price(0)]

    for i in range(len(prices["asks"][curr_product])): # bid and ask should be same length arrays
        curr_spread = prices["asks"][curr_product][i] - prices["bids"][curr_product][i]
        
        if curr_spread >= 6:
            prices["avg"][curr_product].append(get_avg_price(i))
        else:
            prices["avg"][curr_product].append(prices["avg"][curr_product][-1])

        n_lookback_index = max(i - n, 0)

        window = prices["avg"][curr_product][n_lookback_index:]
        avg_price = sum(window) / len(window)
        prices["avg_prices"][curr_product].append(avg_price)

    plt.plot(prices["asks"][curr_product])
    plt.plot(prices["bids"][curr_product])
    plt.plot(prices["avg_prices"][curr_product])
    plt.show()


# Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

n = 10

for curr_product in products:
    prices["avg"][curr_product] = get_avg_price(0)
    prices["avg_prices"][curr_product] = [prices["avg"][curr_product]]

    for i in range(1, len(prices["asks"][curr_product])): # bid and ask should be same length arrays
        curr_price = get_avg_price(i)
        n_lookback_index = max(i - n, 0) # make sure we don't accidentally lookback into the negative indices

        direction = curr_price - get_avg_price(n_lookback_index) # today's price - price n bars back
        volatility = sum([abs(get_avg_price(j) - get_avg_price(j - 1)) for j in range(i, n_lookback_index, -1)])
        
        if volatility == 0:
            efficiency_ratio = 0
        else:
            efficiency_ratio = abs(direction / volatility)

        fast_ema_ratio = 2 / (2 + 1) # 2 / (k + 1) where k is small bucket (2 by default)
        slow_ema_ratio = 2 / (30 + 1) # 2 / (l + 1) where l is large bucket (30 by default)
        scaling_constant = (efficiency_ratio * (fast_ema_ratio - slow_ema_ratio) + slow_ema_ratio) ** 2

        prices["avg"][curr_product] = scaling_constant * (curr_price - prices["avg"][curr_product]) + prices["avg"][curr_product]
        prices["avg_prices"][curr_product].append(prices["avg"][curr_product])

    plt.plot(prices["asks"][curr_product])
    plt.plot(prices["bids"][curr_product])
    plt.plot(prices["avg_prices"][curr_product])
    plt.show()



upper_bounds = []
lower_bounds = []

for curr_product in products:
    prices["avg"][curr_product] = get_avg_price(0)
    prices["avg_prices"][curr_product] = [prices["avg"][curr_product]]

    for i in range(1, len(prices["asks"][curr_product])): # bid and ask should be same length arrays
        curr_price = get_avg_price(i)

        if product not in prices["avg_prices"]:
            prices["avg_prices"][product] = []

        prices["avg_prices"][product].append(curr_price)
        period = min(20, len(prices["avg_prices"][product]))
        factor = 1
        window = prices["avg_prices"][product][-period:]
        #calculate bbands bounds of past 20 prices
        avg_price = sum(window) / len(window)
        std_dev = 0
        for price in window:
            std_dev += (price - avg_price) ** 2
        std_dev = (std_dev / len(window)) ** 0.5
        upper_bound = avg_price + factor * std_dev
        lower_bound = avg_price - factor * std_dev

        upper_bounds.append(upper_bound)
        lower_bounds.append(lower_bound)
    
    plt.plot(prices["asks"][curr_product])
    plt.plot(prices["bids"][curr_product])
    plt.plot(upper_bounds)
    plt.plot(lower_bounds)
    plt.show()