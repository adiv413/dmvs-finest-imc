from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

#this code will not execute any trades. It will just be inputted into the alg and will be used to download the data free of any intervention from our algorithm.
class Trader:
    products = ["DIVING_GEAR"]
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        skipTimeStamp = True
        for product in self.products:
            timestamp = state.timestamp
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0:
                sell_orders = order_depth.sell_orders
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
            
            if len(order_depth.buy_orders) != 0:
                buy_orders = order_depth.buy_orders
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
            
            spread = best_ask - best_bid
            if skipTimeStamp:
                skipTimeStamp = False
                print(f', {product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {spread}')
            else:
                print(f'{timestamp} , {product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {spread}')
            
            print(f'{timestamp}, {state.observations}')

            
        return result