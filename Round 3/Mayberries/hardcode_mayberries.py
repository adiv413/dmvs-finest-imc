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
    POSITION_LIMIT = {"BERRIES": 250}

    stats = {
        "asks" : {}, 
        "askVolumes" : {},
        "bids" : {},
        "bidVolumes" : {},
        "avg_prices" : {},
        "count" : {}
    }

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        order_depth: OrderDepth = state.order_depths

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
            # print(product)
            # print(timestep)
            if product == "BERRIES":
                # BUY at timestep of 300k, sell at timestep of 500k
                # logger.print(self.timestep)
                start, end = 300000, 500000
                if(timestep >= start and timestep < end):
                    orders.append(Order("BERRIES", best_ask, self.POSITION_LIMIT[product] - position))
                    # logger.print("BUYING BUYING BUYING")
                    print(f'BUYING: Current position = {position}')
                elif(timestep >= end):
                    orders.append(Order("BERRIES", best_bid, -(min(self.POSITION_LIMIT[product], self.POSITION_LIMIT[product] + position))))
                    # logger.print("I AM IN THE RANGE")
                    print(f'SELLING: Current position = {position}')
            result["BERRIES"] = orders
        # logger.flush(state, result)
        return result
