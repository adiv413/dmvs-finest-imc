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
    ORDER_SIZING = 50
    POSITION_LIMIT = {"PINA_COLADAS": 300, "COCONUTS": 600}

    MODE = "NEUTRAL" #the three modes are NEUTRAL, LONG_PINA, and LONG_COCO
    STANDARD_DEVIATIONS = 2

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
            cocoPrice = cocoPrices[-1]
            pinaPrices = self.stats["avg_prices"]["PINA_COLADAS"][-self.WINDOW_SIZE:]
            pinaPrice = pinaPrices[-1]

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

            pinaOrders: List[Order] = []
            cocoOrders: List[Order] = []
            
            if currentLogVal > logAvg + self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_COCO"
            elif currentLogVal < logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_PINA"
            elif mode == "LONG_PINA" and currentLogVal > logAvg or mode == "LONG_COCO" and currentLogVal < logAvg:
                self.MODE = "NEUTRAL"
            elif mode == "LONG_PINA" and currentLogVal < logAvg + self.STANDARD_DEVIATIONS*logStd or mode == "LONG_COCO" and currentLogVal > logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "HOLD"
            print(self.MODE)
            print("--------------------")
            position_deficit = pinaPosition*pinaPrices[-1] + cocoPosition*cocoPrices[-1]


            if mode == "LONG_PINA": #long pina, short coco
                pina_ask = self.stats["asks"]["PINA_COLADAS"][-1]
                pina_ask_volume = self.stats["askVolumes"]["PINA_COLADAS"][-1]
                coco_bid = self.stats["bids"]["COCONUTS"][-1]
                coco_bid_volume = self.stats["bidVolumes"]["COCONUTS"][-1]

                pina_market_order_size = min(pina_ask_volume, self.POSITION_LIMIT["PINA_COLADAS"] - pinaPosition) * pinaPrice
                coco_market_order_size = min(coco_bid_volume, self.POSITION_LIMIT["COCONUTS"] + cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)
                
                pinaOrders.append(Order("PINA_COLADAS", pina_ask, pina_adj_order))
                print(f'Pina colada BUY order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                cocoOrders.append(Order("COCONUTS", coco_bid, -coco_adj_order))
                print(f'Coconut SELL order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')

            elif mode == "LONG_COCO": #long coco, short pina
                pina_bid = self.stats["bids"]["PINA_COLADAS"][-1]
                pina_bid_volume = self.stats["bidVolumes"]["PINA_COLADAS"][-1]
                coco_ask = self.stats["asks"]["COCONUTS"][-1]
                coco_ask_volume = self.stats["askVolumes"]["COCONUTS"][-1]

                pina_market_order_size = min(pina_bid_volume, self.POSITION_LIMIT["PINA_COLADAS"] + pinaPosition) * pinaPrice
                coco_market_order_size = min(coco_ask_volume, self.POSITION_LIMIT["COCONUTS"] - cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)

                pinaOrders.append(Order("PINA_COLADAS", pina_bid, -pina_adj_order))
                print(f'Pina colada SELL order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                cocoOrders.append(Order("COCONUTS", coco_ask, coco_adj_order))
                print(f'Coconut BUY order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')

            elif mode == "NEUTRAL": #sell everything to 0
                if pinaPosition > 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["asks"]["PINA_COLADAS"][-1], -pinaPosition))
                    print(f'Pina colada SELL order placed at quantity {pinaPosition}, seashell amount {pinaPosition*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                elif pinaPosition < 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["bids"]["PINA_COLADAS"][-1], -pinaPosition))
                    print(f'Pina colada BUY order placed at quantity {pinaPosition}, seashell amount {pinaPosition*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                if cocoPosition > 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["asks"]["COCONUTS"][-1], -cocoPosition))
                    print(f'Coconut SELL order placed at quantity {cocoPosition}, seashell amount {cocoPosition*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')
                elif cocoPosition < 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["bids"]["COCONUTS"][-1], -cocoPosition))
                    print(f'Coconut BUY order placed at quantity {cocoPosition}, seashell amount {cocoPosition*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')
            
            result["PINA_COLADAS"] = pinaOrders
            result["COCONUTS"] = cocoOrders        








        return result