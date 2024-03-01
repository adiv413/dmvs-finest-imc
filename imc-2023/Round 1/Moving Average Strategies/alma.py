from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import math

# Mean Reversion with Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

class Trader:

    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "count" : {},
        "acceptable_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895
        } 
    }

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0: # if there are orders in the market, recompute acceptable price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]

                if product not in self.prices["asks"]:
                    self.prices["asks"][product] = []
                if product not in self.prices["bids"]:
                    self.prices["bids"][product] = []

                self.prices["asks"][product].append(best_ask)
                self.prices["bids"][product].append(best_bid)

                n = 10
                offset = 0.85
                sigma = 6
                get_avg_price = lambda x : (self.prices["asks"][product][x] + self.prices["bids"][product][x]) / 2 # gets average price at index
                curr_price = (best_ask + best_bid) / 2 

                # first iteration
                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = [curr_price]
                    self.prices["acceptable_price"][product] = curr_price

                    # don't place orders in the first iteration
                    result[product] = orders
                    return result
                
                i = len(self.prices["avg_prices"][product]) - 1 # index of current price
                n_lookback_index = max(i - n, 0) # make sure we don't accidentally lookback into the negative indices
                sum = 0

                for j in range(n_lookback_index, i):
                    sum += get_avg_price(j) * (math.e)**(((-1)*(j-offset)**2)/(sigma**2))

                alma = sum/n
                curr_average = alma

                self.prices["acceptable_price"][product] = curr_average
                self.prices["avg_prices"][product].append(curr_average)

            # set acceptable price
            acceptable_price = self.prices["acceptable_price"][product]

            # based on pricing, make orders
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                if best_ask < acceptable_price:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_volume))

            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

            result[product] = orders

        return result