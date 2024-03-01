from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm


class Trader:

    prices = {
        "asks": {},
        "bids": {},
        "avg_prices": {},
        "count": {},
    }

    POSITION_LIMIT = {"BANANAS": 20, "PEARLS": 20}
    PRELIM_NUMS = {"PEARLS": 10000,
                   "BANANAS": 4895}

    def ama(self, n, product, curr_price):
        # first iteration
        
        dict_key = "acceptable_price_" + str(n)
        if(dict_key not in self.prices):
            self.prices[dict_key] = {}
        if(product not in self.prices[dict_key]):
            self.prices[dict_key][product] = curr_price

        # index of current price
        i = len(self.prices["avg_prices"][product]) - 1
        get_avg_price = lambda x : (self.prices["asks"][product][x] + self.prices["bids"][product][x]) / 2
        # make sure we don't accidentally lookback into the negative indices
        n_lookback_index = max(i - n, 0)

        # today's price - price n bars back
        direction = curr_price - get_avg_price(n_lookback_index)
        volatility = sum([abs(get_avg_price(j) - get_avg_price(j - 1)) for j in range(i, n_lookback_index, -1)])

        if volatility == 0:
            efficiency_ratio = 0
        else:
            efficiency_ratio = abs(direction / volatility)

        # 2 / (k + 1) where k is small bucket (2 by default)
        fast_ema_ratio = 2 / (2 + 1)
        # 2 / (l + 1) where l is large bucket (30 by default)
        slow_ema_ratio = 2 / (30 + 1)
        scaling_constant = (
            efficiency_ratio * (fast_ema_ratio - slow_ema_ratio) + slow_ema_ratio) ** 2

        curr_average = scaling_constant * \
            (curr_price - self.prices[dict_key]
                [product]) + self.prices[dict_key][product]
        self.prices[dict_key][product] = curr_average
        self.prices["avg_prices"][product].append(curr_average)

        return 1 #success
    def get_ama(self, n, product):
        return self.prices["acceptable_price_" + str(n)][product]
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

            # if there are orders in the market, recompute acceptable price
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
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

                n, m = 10, 100
                # gets average price at index
                curr_price = (best_ask + best_bid) / 2
                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = [curr_price]

                    result[product] = orders
                    return result
                self.ama(n, product, curr_price) #long term average
                self.ama(m, product, curr_price)  # long term average
                


               
            # set acceptable price
            acceptable_price_short = self.get_ama(n, product)
            acceptable_price_long = self.get_ama(m, product)

            try:
                position = state.position[product]
            except:
                position = 0
            # based on pricing, make orders
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                if best_ask < acceptable_price_short and best_ask < acceptable_price_long:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(
                        0, min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))

            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price_short and best_bid > acceptable_price_long:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(
                        product, best_bid, -max(0, min(best_bid_volume, self.POSITION_LIMIT[product] + position))))

            result[product] = orders

        return result
