#https://github.com/mdibo/Avellaneda-Stoikov/blob/master/AvellanedaStoikovFinal.py
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import math


class Trader:
    sigma = math.sqrt(63.34561255627815)
    gamma = 0.2 # risk aversion
    k = 1.5
    T = 1.0
    num_steps = 1000
    q_max = 10
    
    

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0 and product=="BANANAS":
                try:
                    position = state.position[product]
                except:
                    position = 0
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2

                #time dependent version
                # timestamp = state.timestamp
                # reserve_price = mid_price - position * self.gamma * (self.sigma)**2 * (self.T - timestamp/200000)
                # spread = self.gamma * (self.sigma)**2 * (self.T - timestamp/200000) + (2/self.gamma) * ( math.log(1 + (self.gamma/self.k)))

                print(f'position: {position}')
                #time independent version
                w = 0.5 * (self.gamma)**2 * (self.sigma)**2 * (self.q_max+1)**2
                reserve_price_a = mid_price + (1/self.gamma) * math.log( 1 + ( (1-2*position) * (self.gamma)**2 * (self.sigma)**2) / \
                                                                        (2*w - (self.gamma)**2 * (position)**2 * (self.sigma)**2) )
                reserve_price_b = mid_price - (1/self.gamma) * math.log( 1 + ( (-1-2*position) * (self.gamma)**2 * (self.sigma)**2) / \
                                                                        (2*w - (self.gamma)**2 * (position)**2 * (self.sigma)**2) )
                reserve_price = (reserve_price_a + reserve_price_b) / 2
                spread = (2/self.gamma) * math.log( 1 + (self.gamma/self.k)) + 0.5 * self.gamma * (self.sigma)**2

                my_bid = reserve_price - spread/2
                my_ask = reserve_price + spread/2

                # print(f'mid_price: {mid_price}, reserve_price: {reserve_price}, spread: {spread}, my_bid: {my_bid}, my_ask: {my_ask}, actual spread: {best_bid - best_ask}')
                
                orders.append(Order(product, my_bid, 1))
                orders.append(Order(product, my_ask, -1))

                result[product] = orders
        
        return result