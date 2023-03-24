from matplotlib import pyplot as plt
from scipy.stats import pearsonr
import statsmodels.tsa.stattools as ts

lines = open("Data Analysis/logs/day2.log").readlines()
lines = [i for i in lines if ";" in i][1:]
print(lines[0], lines[-1])
products = {}
for i in lines:
    x = i.split(";")
    x = [j.strip() for j in x if j != '']
    if x[2] not in products:
        products[x[2]] = []
    products[x[2]].append(float(x[-1]))

for i in products.keys():
    plt.plot(products[i])
    plt.title(i)
    plt.show()

# print(pearsonr(products["PINA_COLADAS"], products["COCONUTS"]))
# result = ts.coint(products["PINA_COLADAS"], products["COCONUTS"])
# print(result[1])
