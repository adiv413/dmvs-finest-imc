#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    ORDER_SIZE = 20
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
    
        result = {}
        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                
                orders.append(Order(product, 1000000, self.ORDER_SIZE))
                # orders.append(Order(product, -10000000, -self.ORDER_SIZE))
                orders.append(Order(product, -10000000, -self.ORDER_SIZE))

                result[product] = orders
        
        return result