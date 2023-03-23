#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import math


class Trader:
    PROFIT_TARGET = 1
    RISK_ADJUSTMENT = 0.15
    ORDER_VOLUME = 5
    HALF_SPREAD_SIZE = 3

    sigma = {
        "PEARLS": math.sqrt(2.2303229114558007),
        "BANANAS": math.sqrt(63.34561255627815),
    }
    gamma = 3  # risk aversion
    k = 1.5
    T = 1.0
    num_steps = 1000
    q_max = 2

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            orders: list[Order] = []
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())

                best_ask = min(order_depth.sell_orders.keys())

                value = (best_ask + best_bid)/2
                spread = best_ask - best_bid
                try:
                    position = state.position[product]
                except:
                    position = 0
                sig = self.sigma[product]
                w = 0.5 * (self.gamma)**2 * (sig)**2 * (self.q_max+1)**2
                sell_quote = value + (1/self.gamma) * math.log(1 + ((1-2*(position/10)) * (self.gamma)**2 * (sig)**2) /
                                                               (2*w - (self.gamma)**2 * ((position/10))**2 * (sig)**2)) + self.HALF_SPREAD_SIZE
                buy_quote = value + (1/self.gamma) * math.log(1 + ((-1-2*(position/10)) * (self.gamma)**2 * (sig)**2) /
                                                    (2*w - (self.gamma)**2 * ((position/10))**2 * (sig)**2)) - self.HALF_SPREAD_SIZE

                # buy_quote = value + (skew - spread/2+0.01)
                # sell_quote = value + (skew + spread/2-0.01)
    
                orders.append(Order(product, buy_quote, self.ORDER_VOLUME))
                orders.append(Order(product, sell_quote, -self.ORDER_VOLUME))

                print(f'position: {position}')

                result[product] = orders
        
        return result
