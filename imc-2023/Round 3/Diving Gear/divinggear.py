from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

class Trader:

    POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10, "PINA_COLADAS": 300, "COCONUTS": 600, "DIVING_GEAR": 500, "BERRIES": 250}
    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "count" : {},
        "acceptable_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895,
            "PINA_COLADAS": 15000, 
            "COCONUTS": 8000,
            "DIVING_GEAR": 99000,
            "BERRIES": 4000
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

            mcginley_price = self.prices["acceptable_price"][product]

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

                n = 100
                k = 0.67
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

                mcginley_price = mcginley_price + (curr_price-mcginley_price)/(k * n * (curr_price/mcginley_price)**4)

                self.prices["acceptable_price"][product] = mcginley_price
                self.prices["avg_prices"][product].append(mcginley_price)
            
                try:
                    position = state.position[product]
                except:
                    position = 0

                # set acceptable price
                acceptable_price = self.prices["acceptable_price"][product]

                # based on pricing, make orders
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    if best_ask < acceptable_price:
                        # print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))

                if len(order_depth.buy_orders) > 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        # print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))))

                # print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')
                print(f'position for {product} is {position}')

                result[product] = orders

        return result