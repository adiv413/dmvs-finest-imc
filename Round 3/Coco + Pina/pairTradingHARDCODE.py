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


    POSITION_LIMIT = {"PINA_COLADAS": 300, "COCONUTS": 600}
    POSITION_LIMIT = {"PINA_COLADAS": 300, "COCONUTS": 600}

    MODE = "NEUTRAL" #the three modes are NEUTRAL, LONG_PINA, and LONG_COCO, PINA_HOLD, and COCO_HOLD
    STANDARD_DEVIATIONS = 0.5

    WINDOW_SIZE = 10

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

        print("...")
        #check if one of the counts is greater than the window size
        if True:
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
            currentLogVal = log(pinaPrices[-1] / cocoPrices[-1])
            logAvg = 0.6288272247232621
            #calculate the standard deviation of logValues
            logStd =  0.002382788768726835

            pinaOrders: List[Order] = []
            cocoOrders: List[Order] = []
            
            if currentLogVal > logAvg + self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_COCO"
            elif currentLogVal < logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_PINA"
            elif self.MODE == "PINA_HOLD" and currentLogVal > logAvg or self.MODE == "LONG_COCO" and currentLogVal < logAvg:
                self.MODE = "NEUTRAL"
            elif self.MODE == "LONG_PINA" and currentLogVal < logAvg + self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "PINA_HOLD"
            elif self.MODE == "LONG_COCO" and currentLogVal > logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "COCO_HOLD"
            # print("--------------------")
            # print(self.MODE)

            position_deficit = pinaPosition*pinaPrices[-1] + cocoPosition*cocoPrices[-1]

            #print the coco ask volumes and the coco bid volumes

            if self.MODE == "LONG_PINA": #long pina, short coco
                pina_ask = self.stats["asks"]["PINA_COLADAS"][-1]
                pina_ask_volume = self.stats["askVolumes"]["PINA_COLADAS"][-1]
                coco_bid = self.stats["bids"]["COCONUTS"][-1]
                coco_bid_volume = self.stats["bidVolumes"]["COCONUTS"][-1]

                # print(f'Pina ask: {pina_ask}, Pina ask volume: {pina_ask_volume}, Coco bid: {coco_bid}, Coco bid volume: {coco_bid_volume}')
                # print(f'Pina position: {pinaPosition}, Coco position: {cocoPosition}')

                pina_market_order_size = min(-pina_ask_volume, self.POSITION_LIMIT["PINA_COLADAS"] - pinaPosition) * pinaPrice
                coco_market_order_size = min(coco_bid_volume, self.POSITION_LIMIT["COCONUTS"] + cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)

                # print(f'Pina adj order: {pina_adj_order}, Coco adj order: {coco_adj_order}, market order size: {market_order_size}, position deficit: {position_deficit}')
                
                pinaOrders.append(Order("PINA_COLADAS", pina_ask, pina_adj_order))
                # print(f'Pina colada BUY order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}, order price {pina_ask}')
                cocoOrders.append(Order("COCONUTS", coco_bid, -coco_adj_order))
                # print(f'Coconut SELL order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}, order price {coco_bid}')

            elif self.MODE == "LONG_COCO": #long coco, short pina
                pina_bid = self.stats["bids"]["PINA_COLADAS"][-1]
                pina_bid_volume = self.stats["bidVolumes"]["PINA_COLADAS"][-1]
                coco_ask = self.stats["asks"]["COCONUTS"][-1]
                coco_ask_volume = self.stats["askVolumes"]["COCONUTS"][-1]

                pina_market_order_size = min(pina_bid_volume, self.POSITION_LIMIT["PINA_COLADAS"] + pinaPosition) * pinaPrice
                coco_market_order_size = min(-coco_ask_volume, self.POSITION_LIMIT["COCONUTS"] - cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)

                pinaOrders.append(Order("PINA_COLADAS", pina_bid, -pina_adj_order))
                # print(f'Pina colada SELL order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                cocoOrders.append(Order("COCONUTS", coco_ask, coco_adj_order))
                # print(f'Coconut BUY order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')

            elif self.MODE == "NEUTRAL": #sell everything to 0
                if pinaPosition > 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["bids"]["PINA_COLADAS"][-1], -pinaPosition))
                    print(f'Pina colada SELL order placed at quantity {-pinaPosition}, price {self.stats["bids"]["PINA_COLADAS"][-1]}')
                elif pinaPosition < 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["asks"]["PINA_COLADAS"][-1], -pinaPosition))
                    print(f'Pina colada BUY order placed at quantity {-pinaPosition}, price {self.stats["asks"]["PINA_COLADAS"][-1]}')
                if cocoPosition > 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["bids"]["COCONUTS"][-1], -cocoPosition))
                    print(f'Coconut SELL order placed at quantity {-cocoPosition}, price {self.stats["bids"]["COCONUTS"][-1]}')
                elif cocoPosition < 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["asks"]["COCONUTS"][-1], -cocoPosition))
                    print(f'Coconut BUY order placed at quantity {-cocoPosition}, price {self.stats["asks"]["COCONUTS"][-1]}')
                    
            
            print(f'Mode: {self.MODE}')
            print(f'Pina Position: {pinaPosition*pinaPrice}, position amount {pinaPosition}')
            print(f'Coco Position: {cocoPosition*cocoPrice}, position amount {cocoPosition}')
            print(f'log ratio: {currentLogVal}')


            result["PINA_COLADAS"] = pinaOrders
            result["COCONUTS"] = cocoOrders    

        return result