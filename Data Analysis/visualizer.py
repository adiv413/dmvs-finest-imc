from matplotlib import pyplot as plt
from scipy.stats import pearsonr, spearmanr
import statsmodels.tsa.stattools as ts

lines = open("Round 4/data/round5pnl.log").readlines()
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

# assert(len(products["BAGUETTE"]) == len(products["DIP"]) == len(products["UKULELE"]))
# productsum = [products["BAGUETTE"][i] * 2 + products["DIP"][i] * 4 + products["UKULELE"][i] for i in range(len(products["UKULELE"]))]
# productdiff = [products["PICNIC_BASKET"][i] - productsum[i] for i in range(len(products["PICNIC_BASKET"]))]
# plt.plot(productdiff, label="diff")
# # plt.plot(products["PICNIC_BASKET"], label="real basket value")
# plt.legend()
# plt.show()

# print("picnic basket + estimation sum pearson", pearsonr(productsum, products["PICNIC_BASKET"]))
# print("picnic basket + estimation sum spearman", spearmanr(productsum, products["PICNIC_BASKET"]))

# print("dip + baguette pearson", pearsonr(products["DIP"], products["BAGUETTE"]))
# print("dip + baguette spearman", spearmanr(products["DIP"], products["BAGUETTE"]))
