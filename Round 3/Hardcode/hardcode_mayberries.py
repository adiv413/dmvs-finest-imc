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
    timestep = 0
    POSITION_LIMIT = {"BANANAS": 10, "PEARLS": 10, "BERRIES": 250}

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

            try:
                position = state.position[product]
            except:
                position = 0

            if(product == "BERRIES"):
                # BUY at timestep of 300k, sell at timestep of 500k
                logger.print(self.timestep)
                start, end, range = 1000, 6000, 100
                if(self.timestep >= start and self.timestep <= start + range):
                    result["BERRIES"] = Order("BERRIES", "BUY", best_ask, max(
                        0, min(-best_ask_volume, self.POSITION_LIMIT[product] - position)))
                    logger.print("I AM IN THE RANGE")
                elif(self.timestep >= end and self.timestep <= end + range):
                    result["BERRIES"] = Order("BERRIES", "SELL", best_bid, -max(
                        0, min(best_bid_volume, self.POSITION_LIMIT[product] + position)))
                    logger.print("I AM IN THE RANGE")
        self.timestep += 1
        logger.flush(state, result)
        return result
