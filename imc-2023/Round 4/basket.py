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
    POSITION_LIMIT = {"PICNIC_BASKET": 70, "BAGUETTE": 150, "DIP": 300, "UKULELE": 70}

    stats = {
        "asks" : {}, 
        "askVolumes" : {},
        "bids" : {},
        "bidVolumes" : {},
        "avg_prices" : {},
        "count" : {},
        "mcginley_price": {}
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
                self.stats["mcginley_price"][product] = 1

            self.stats["asks"][product].append(best_ask)
            self.stats["bids"][product].append(best_bid)
            self.stats["avg_prices"][product].append((best_ask + best_bid)/2)
            self.stats["count"][product] += 1
            self.stats["askVolumes"][product].append(best_ask_volume)
            self.stats["bidVolumes"][product].append(best_bid_volume)

            n = 20
            k = 0.65
            self.stats["mcginley_price"][product] = self.stats["mcginley_price"][product] + (
                self.stats["avg_prices"][product][-1] - self.stats["mcginley_price"][product])/(k * n * (self.stats["avg_prices"][product][-1] /self.stats["mcginley_price"][product])**4)


            try:
                position = state.position[product]
            except:
                position = 0
        

            if product == "PICNIC_BASKET":
                # BUY at timestep of 300k, sell at timestep of 500k
                # logger.print(self.timestep)

                if "DIP" in self.stats["mcginley_price"] and "BAGUETTE" in self.stats["mcginley_price"] and "UKULELE" in self.stats["mcginley_price"]:
                    market_price = 4*self.stats["mcginley_price"]["DIP"] + 2*self.stats["mcginley_price"]["BAGUETTE"] + self.stats["mcginley_price"]["UKULELE"]

                    if self.stats["avg_prices"]["PICNIC_BASKET"][-1] < market_price:
                        orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))
                        # logger.print("BUYING BUYING BUYING")
                        print(f'BUYING: Current position = {position}')
                    else:
                        orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))))
                        # logger.print("I AM IN THE RANGE")
                        print(f'SELLING: Current position = {position}')
                result["PICNIC_BASKET"] = orders
        # logger.flush(state, result)
        return result
