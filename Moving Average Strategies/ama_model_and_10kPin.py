from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

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
            if product == "BANANAS":
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

                    direction = curr_price - get_avg_price(n_lookback_index) # today's price - price n bars back
                    volatility = sum([abs(get_avg_price(j) - get_avg_price(j - 1)) for j in range(i, n_lookback_index, -1)])
                    
                    if volatility == 0:
                        efficiency_ratio = 0
                    else:
                        efficiency_ratio = abs(direction / volatility)

                    fast_ema_ratio = 2 / (2 + 1) # 2 / (k + 1) where k is small bucket (2 by default)
                    slow_ema_ratio = 2 / (30 + 1) # 2 / (l + 1) where l is large bucket (30 by default)
                    scaling_constant = (efficiency_ratio * (fast_ema_ratio - slow_ema_ratio) + slow_ema_ratio) ** 2

                    curr_average = scaling_constant * (curr_price - self.prices["acceptable_price"][product]) + self.prices["acceptable_price"][product]

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
                
            elif product == "PEARLS":
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 10000 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:

                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above

        return result