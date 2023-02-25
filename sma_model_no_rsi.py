from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Simple Moving Average (SMA)

class Trader:

    prices = {
        "avg_prices" : {},
        "acceptable_price" : {} 
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

                curr_price = (best_ask + best_bid) / 2 

                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = []

                self.prices["avg_prices"][product].append(curr_price)
                self.prices["acceptable_price"][product] = sum(self.prices["avg_prices"][product]) / len(self.prices["avg_prices"][product])

                # set acceptable price
                acceptable_price = self.prices["acceptable_price"][product]

                # based on pricing, make orders
                if best_ask < acceptable_price:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_volume))

                if best_bid > acceptable_price:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

                result[product] = orders

        return result