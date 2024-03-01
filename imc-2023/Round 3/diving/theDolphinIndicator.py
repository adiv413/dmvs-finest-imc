from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
from math import log
import json



# class Logger:
#     def __init__(self) -> None:
#         self.logs = ""

#     def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
#         self.logs += sep.join(map(str, objects)) + end

#     def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
#         print(json.dumps({
#             "state": state,
#             "orders": orders,
#             "logs": self.logs,
#         }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

#         self.logs = ""


# logger = Logger()

class Trader:
    COUNT = 0
    POSITION_LIMIT = {"DIVING_GEAR": 50}

    stats = {
        "asks" : {}, 
        "askVolumes" : {},
        "bids" : {},
        "bidVolumes" : {},
        "avg_prices" : {},
        "count" : {}
    }

    LAST_DOLPHIN_SIGHTING = -1
    DOLPHIN_WINDOW1 = 100
    DOLPHIN_WINDOW2 = 200
    DOLPHIN_MODE = "NEUTRAL"




    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        order_depth: OrderDepth = state.order_depths
        self.COUNT += 1

        # print all the products
        # print(order_depth.keys())
        for product in [key for key in self.POSITION_LIMIT.keys()]:
            orders: List[Order] = []
            best_ask = min(order_depth[product].sell_orders.keys())
            best_ask_volume = order_depth[product].sell_orders[best_ask]
            best_bid = max(order_depth[product].buy_orders.keys())
            best_bid_volume = order_depth[product].buy_orders[best_bid]
            timestep = state.timestamp

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
            try:
                position = state.position[product]
            except:
                position = 0
            print('...')
            if product == "DIVING_GEAR":
                print(f'Dolphin sighting: {state.observations["DOLPHIN_SIGHTINGS"]}')
                # print(f'Diving Gear Mid Price: {self.stats["avg_prices"][product][-1]}')
                dSighting = state.observations["DOLPHIN_SIGHTINGS"]
                delta = dSighting - self.LAST_DOLPHIN_SIGHTING
                print(f'Delta: {delta}')
                if self.COUNT >= self.DOLPHIN_WINDOW2:
                    MA1 = sum(self.stats["avg_prices"][product][-self.DOLPHIN_WINDOW1:])/self.DOLPHIN_WINDOW1
                    MA2 = sum(self.stats["avg_prices"][product][-self.DOLPHIN_WINDOW2:])/self.DOLPHIN_WINDOW2
                    if delta < -5:
                        self.DOLPHIN_MODE = "NEW_SHORT"
                    elif delta > 5:
                        self.DOLPHIN_MODE = "NEW_LONG"

                    if self.DOLPHIN_MODE == "NEW_SHORT" and MA1 < MA2:
                        self.DOLPHIN_MODE = "SHORT"
                    elif self.DOLPHIN_MODE == "SHORT" and MA1 > MA2:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    elif self.DOLPHIN_MODE == "NEW_LONG" and MA1 > MA2:
                        self.DOLPHIN_MODE = "LONG"
                    elif self.DOLPHIN_MODE == "LONG" and MA1 < MA2:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    
                    if self.COUNT > 500:
                        self.DOLPHIN_MODE = "NEW_LONG"
                    if self.COUNT > 600:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    if self.COUNT > 700:
                        self.DOLPHIN_MODE = "NEW_SHORT"
                    if self.COUNT > 800:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    
                    if self.DOLPHIN_MODE == "NEW_SHORT" or self.DOLPHIN_MODE == "SHORT":
                        print("SHORTING: Current position = ", position)
                        orders.append(Order("DIVING_GEAR", best_bid, -(min(self.POSITION_LIMIT[product], self.POSITION_LIMIT[product] + position))))      
                    elif self.DOLPHIN_MODE == "NEW_LONG" or self.DOLPHIN_MODE == "LONG":
                        print("LONGING: Current position = ", position)
                        orders.append(Order("DIVING_GEAR", best_ask, self.POSITION_LIMIT[product] - position))
                    elif self.DOLPHIN_MODE == "NEUTRAL":
                        if position > 0:
                            print("SELLING: Current position = ", position)
                            orders.append(Order("DIVING_GEAR", best_bid, -position))
                        elif position < 0:
                            print("BUYING: Current position = ", position)
                            orders.append(Order("DIVING_GEAR", best_ask, -position))
                print("UPDATING DOLPHIN SIGHTING")
                self.LAST_DOLPHIN_SIGHTING = dSighting
                result["DIVING_GEAR"] = orders
                
        # logger.flush(state, result)
        print(result)
        return result
