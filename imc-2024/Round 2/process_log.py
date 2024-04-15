import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import stdev, linear_regression, correlation
from collections import deque

f = open("test2.log").readlines()
lines = [i for i in f if "orchids" in i]
orchid_bids = []
orchid_asks = []
conversions_bids = []
conversions_asks = []
timestamps = []
count = 0
for i in lines:
    x = i.split("\\n")
    orchids_raw = x[0].split(":")[1].replace("orchids ", "")[2:].strip()
    conversions_raw = x[1].replace("conversions ", "").strip()
    transport = x[2].replace("transport ", "").strip()
    export = x[3].replace("export ", "").strip()
    imp = x[4].replace("import ", "")[:-3].strip()

    orchids = orchids_raw.split(" ")
    conversions = conversions_raw.split(" ")

    print(orchids)
    print(conversions)
    print(transport)
    print(export)
    print(imp)

    orchid_bids.append(float(orchids[1]))
    orchid_asks.append(float(orchids[0]))

    conversions_bids.append(float(conversions[1]))
    conversions_asks.append(float(conversions[0]))
    timestamps.append(count)

    count += 1

plt.plot(timestamps, orchid_bids, label='orchid_bids')
plt.plot(timestamps, orchid_asks, label='orchid_asks')
plt.plot(timestamps, conversions_bids, label='conversions_bids')
plt.plot(timestamps, conversions_asks, label='conversions_asks')



plt.xlabel('timestamp')
plt.ylabel('price')
plt.legend()
plt.show()
