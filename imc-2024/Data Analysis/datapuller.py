from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    products = ["AMETHYSTS", "STARFRUIT"]
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        # print(f'{state.timestamp} ')
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        
        result = {}
        traderData = state.traderData
        skipTimeStamp = True
        for product in self.products:
            timestamp = state.timestamp
            order_depth: OrderDepth = state.order_depths[product]
            if len(order_depth.sell_orders)>0:
                sell_orders = order_depth.sell_orders
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
            if len(order_depth.buy_orders) > 0:
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

        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        return result, conversions, traderData