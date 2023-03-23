from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import log

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

    MODE = "NEUTRAL" #the three modes are NEUTRAL, LONG_PINA, and LONG_COCO

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
        if self.stats["count"]["COCONUTS"] > self.WINDOW_SIZE:
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

            #calculate the log average price of pinaPrics/cocoPrices
            logValues = [log(pinaPrices[i]/cocoPrices[i]) for i in range(len(pinaPrices))]
            logAvg = sum(logValues)/len(logValues)
            #calculate the standard deviation of logValues
            logStd = (sum([(logValues[i] - logAvg)**2 for i in range(len(logValues))])/len(logValues))**0.5
            currentLogVal = logValues[-1]
            #if current log val is 2*std above the average, buy pina and sell coco. If 2*std below, sell pina and buy coco
            cocoOrders: list[Order] = []
            pinaOrders: list[Order] = []
            if currentLogVal > 2*logStd + logAvg:
                pinaOrders.append(Order("PINA_COLADAS", pinaLastAsk, max(0,min(-pinaLastAskVolume, self.POSITION_LIMIT[product] - pinaPosition))))
                cocoOrders.append(Order("COCONUTS", cocoLastBid, -max(0,min(cocoLastBidVolume, self.POSITION_LIMIT[product] + cocoPosition))))
                print(f'Sell order for coconut at {cocoLastAsk}, current coconut price is {cocoPrices[-1]}')
                self.MODE = "LONG_PINA"
            elif currentLogVal < -2*logStd + logAvg:
                pinaOrders.append(Order("PINA_COLADAS", pinaLastBid, -max(0,min(pinaLastBidVolume, self.POSITION_LIMIT[product] + pinaPosition))))
                cocoOrders.append(Order("COCONUTS", cocoLastAsk, max(0,min(-cocoLastBidVolume, self.POSITION_LIMIT[product] - cocoPosition))))
                print(f'Buy order for coconut at {cocoLastBid}, current coconut price is {cocoPrices[-1]}')
                self.MODE = "LONG_COCO"
            elif currentLogVal <= logAvg+1*logStd and self.MODE == "LONG_PINA":
                #exit position
                pinaOrders.append(Order("PINA_COLADAS", pinaLastAsk, -pinaPosition))
                cocoOrders.append(Order("COCONUTS", cocoLastBid, cocoPosition))
                self.MODE = "NEUTRAL"
            elif currentLogVal >= logAvg-1*logStd and self.MODE == "LONG_COCO":
                #exit position
                pinaOrders.append(Order("PINA_COLADAS", pinaLastBid, pinaPosition))
                cocoOrders.append(Order("COCONUTS", cocoLastAsk, -cocoPosition))
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

        return result