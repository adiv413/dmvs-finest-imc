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


# Simple Moving Average (SMA)

products = ["banana", "pearl"]

for curr_product in products:
    prices["avg"][curr_product] = 0
    prices["count"][curr_product] = 0
    prices["avg_prices"][curr_product] = []

    for i in range(len(prices["asks"][curr_product])): # bid and ask should be same length arrays
        if prices["avg"][curr_product] == 0:
            prices["avg"][curr_product] = (prices["asks"][curr_product][i] + prices["bids"][curr_product][i]) / 2
            prices["count"][curr_product] = 1

        else:
            total = prices["avg"][curr_product] * prices["count"][curr_product] + (prices["asks"][curr_product][i] + prices["bids"][curr_product][i]) / 2
            prices["count"][curr_product] += 1
            prices["avg"][curr_product] = total / prices["count"][curr_product]
        
        prices["avg_prices"][curr_product].append(prices["avg"][curr_product])

    plt.plot(prices["asks"][curr_product])
    plt.plot(prices["bids"][curr_product])
    plt.plot(prices["avg_prices"][curr_product])
    plt.show()


# Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

n = 10
get_avg_price = lambda x : (prices["asks"][curr_product][x] + prices["bids"][curr_product][x]) / 2 # gets average price at index

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