from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
from math import log
import json


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""


logger = Logger()

class Trader:

    stats = {
        "asks" : {}, 
        "askVolumes" : {},
        "bids" : {},
        "bidVolumes" : {},
        "avg_prices" : {},
        "count" : {}
    }

    WINDOW_SIZE = 200

    SCALING_DIVISOR = {"PINA_COLADAS": 1.875, "COCONUTS": 1}
    POSITION_LIMIT = {"PINA_COLADAS": 300, "COCONUTS": 300}
    MODE = "NEUTRAL"  # the three modes are NEUTRAL, LONG_PINA, and LONG_COCO

    def correlation(self, product_1, product_2):
        #calculate pearson correlation coefficiant given two lists of products
        #https://www.geeksforgeeks.org/program-for-pearson-correlation-coefficient/
        n = len(product_1)
        sum_x = sum(product_1)
        sum_y = sum(product_2)
        sum_xy = sum([product_1[i] * product_2[i] for i in range(n)])
        squareSum_x = sum([product_1[i] ** 2 for i in range(n)])
        squareSum_y = sum([product_2[i] ** 2 for i in range(n)])
        corr = (n * sum_xy - sum_x * sum_y) / ((n * squareSum_x - sum_x ** 2) * (n * squareSum_y - sum_y ** 2)) ** 0.5
        return corr
        # mean_1 = sum(product_1)/len(product_1)
        # mean_2 = sum(product_2)/len(product_2)

        # #calculate standard deviations
        # std_1 = (sum([(x - mean_1)**2 for x in product_1])/len(product_1))**0.5
        # std_2 = (sum([(x - mean_2)**2 for x in product_2])/len(product_2))**0.5

        # #calculate covariance
        # covariance = sum([(product_1[i] - mean_1)*(product_2[i] - mean_2)
        #                 for i in range(len(product_1))])/(len(product_1))

        # return covariance/(std_1 * std_2)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        order_depth: OrderDepth = state.order_depths


        for product in [key for key in state.order_depths.keys() if key in self.POSITION_LIMIT.keys()]:
            best_ask = min(order_depth[product].sell_orders.keys())
            best_ask_volume = order_depth[product].sell_orders[best_ask]
            best_bid = max(order_depth[product].buy_orders.keys())
            best_bid_volume = order_depth[product].buy_orders[best_bid]

            if product not in self.stats["asks"].keys():
                self.stats["asks"][product] = []
                self.stats["bids"][product] = []
                self.stats["avg_prices"][product] = []
                self.stats["count"][product] = 0
                self.stats["askVolumes"][product] = []
                self.stats["bidVolumes"][product] = []
            self.stats["asks"][product].append(best_ask)
            self.stats["bids"][product].append(best_bid)
            self.stats["avg_prices"][product].append((best_ask + best_bid)/2)
            self.stats["count"][product] += 1
            self.stats["askVolumes"][product].append(best_ask_volume)
            self.stats["bidVolumes"][product].append(best_bid_volume)
        
        #check if one of the counts is greater than the window size
        window = max(self.stats["count"]["PINA_COLADAS"], self.WINDOW_SIZE)
        min_window_size = 10 #minimum window size to trade
        if window > min_window_size:
            cocoPrices = self.stats["avg_prices"]["COCONUTS"][-self.WINDOW_SIZE:]
            cocoLastAsk = self.stats["asks"]["COCONUTS"][-1]
            cocoLastBid = self.stats["bids"]["COCONUTS"][-1]
            cocoLastAskVolume = self.stats["askVolumes"]["COCONUTS"][-1]
            cocoLastBidVolume = self.stats["bidVolumes"]["COCONUTS"][-1]

            pinaPrices = self.stats["avg_prices"]["PINA_COLADAS"][-self.WINDOW_SIZE:]
            pinaLastAsk = self.stats["asks"]["PINA_COLADAS"][-1]
            pinaLastBid = self.stats["bids"]["PINA_COLADAS"][-1]
            pinaLastAskVolume = self.stats["askVolumes"]["PINA_COLADAS"][-1]
            pinaLastBidVolume = self.stats["bidVolumes"]["PINA_COLADAS"][-1]

            try:
                cocoPosition = state.position["COCONUTS"]
            except:
                cocoPosition = 0
            try:
                pinaPosition = state.position["PINA_COLADAS"]
            except:
                pinaPosition = 0

            corr = self.correlation(cocoPrices, pinaPrices)


            #calculate the log average price of pinaPrics/cocoPrices
            logValues = [log(pinaPrices[i]/cocoPrices[i]) for i in range(len(pinaPrices))]
            logAvg = sum(logValues)/len(logValues)
            #calculate the standard deviation of logValues
            logStd = (sum([(logValues[i] - logAvg)**2 for i in range(len(logValues))])/len(logValues))**0.5
            currentLogVal = logValues[-1]
            #if current log val is 2*std above the average, sell pina and buy coco. If 2*std below, buy pina and sell coco
            cocoOrders: list[Order] = []
            pinaOrders: list[Order] = []
            if currentLogVal > 2*logStd + logAvg:
                pinaOrders.append(Order("PINA_COLADAS", pinaLastBid, -max(0,min(pinaLastBidVolume, self.POSITION_LIMIT[product] + pinaPosition))))
                cocoOrders.append(Order("COCONUTS", cocoLastAsk, max(0,min(-cocoLastBidVolume, self.POSITION_LIMIT[product] - cocoPosition))))
                #logger.print(f'Buy order for coconut at {cocoLastBid}, current coconut price is {cocoPrices[-1]}')
                self.MODE = "LONG_COCO"
            elif currentLogVal < -2*logStd + logAvg:
                pinaOrders.append(Order("PINA_COLADAS", pinaLastAsk, max(0,min(-pinaLastAskVolume, self.POSITION_LIMIT[product] - pinaPosition))))
                cocoOrders.append(Order("COCONUTS", cocoLastBid, -max(0,min(cocoLastBidVolume, self.POSITION_LIMIT[product] + cocoPosition))))
                #logger.print(f'Sell order for coconut at {cocoLastAsk}, current coconut price is {cocoPrices[-1]}')
                self.MODE = "LONG_PINA"
            elif currentLogVal >= logAvg-1*logStd and self.MODE == "LONG_PINA":
                #exit position
                pinaOrders.append(Order("PINA_COLADAS", pinaLastBid, -pinaPosition))
                cocoOrders.append(Order("COCONUTS", cocoLastAsk, cocoPosition))
                self.MODE = "NEUTRAL"
            elif currentLogVal <= logAvg+1*logStd and self.MODE == "LONG_COCO":
                #exit position
                pinaOrders.append(Order("PINA_COLADAS", pinaLastAsk, pinaPosition))
                cocoOrders.append(Order("COCONUTS", cocoLastBid, -cocoPosition))
                self.MODE = "NEUTRAL"
            elif self.MODE == "NEUTRAL":
                #continue closing positions
                if pinaPosition > 0:
                    pinaOrders.append(Order("PINA_COLADAS", pinaLastAsk, -pinaPosition))
                elif pinaPosition < 0:
                    pinaOrders.append(Order("PINA_COLADAS", pinaLastBid, -pinaPosition))
                if cocoPosition > 0:
                    cocoOrders.append(Order("COCONUTS", cocoLastAsk, -cocoPosition))
                elif cocoPosition < 0:
                    cocoOrders.append(Order("COCONUTS", cocoLastBid, -cocoPosition))
            result["COCONUTS"] = cocoOrders
            result["PINA_COLADAS"] = pinaOrders
            # print("COCONUT POSITION: ", cocoPosition)
            # print("PINA POSITION: ", pinaPosition)
        logger.flush(state, result)
        return result
