#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        spreadcutoff = 4
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            orders: list[Order] = []

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0 and product=="BANANAS":
                spread = min(order_depth.sell_orders.keys()) - max(order_depth.buy_orders.keys())
                if spread > spreadcutoff:
                    #send an order slightly above the best bid and slightly below the best ask
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    orders = []
                    orders.append(Order(product, best_bid + spread/3, 2))
                    orders.append(Order(product, best_ask - spread/3, -2))

                # Add all the above orders to the result dict
                result[product] = orders

        
        return result