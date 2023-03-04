# THIS IS THE FILE YOU TRADE WITH. DATAMODEL.PY SHOWS THE DATA STRUCTURES THAT EACH TIMESTEP WILL USE>

# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import math

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}

        for product in state.order_depths.keys():
            if product == 'PEARLS':

                MAX_PRODUCT = 20
                TARGET_INVENTORY = 10

                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                # If order book is not empty execute the algorithm
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:

                    #average of best bid and ask
                    CURRENT_MID_PRICE = (min(order_depth.sell_orders.keys()) + max(order_depth.buy_orders.keys())) / 2
                    #Distance from target inventory
                    #Q = state.position[product] - TARGET_INVENTORY
                    Q = 1
                    #Inventory risk aversion parameter -- constant now but will be dynamic as algorithm is updated
                    GAMMA = 0.1
                    #Market volatility
                    SIGMA = 2
                    #Time left normalized (T-t), where T is normalized to 1 and t should be a fraction of time
                    #TIME_RATIO = 1 - state.timestamp / 200000
                    TIME_RATIO = 1
                    #Order book liquidity density
                    KAPPA = 1

                    RESERVATION_PRICE = CURRENT_MID_PRICE - (Q * GAMMA * (SIGMA ** 2) * TIME_RATIO)
                    OPTIMAL_TOTAL_SPREAD = (GAMMA * (SIGMA ** 2) * TIME_RATIO) + ((2 / GAMMA) * math.log(1 + GAMMA/KAPPA))

                    OPTIMAL_BID = RESERVATION_PRICE - (OPTIMAL_TOTAL_SPREAD / 2)
                    OPTIMAL_ASK = RESERVATION_PRICE + (OPTIMAL_TOTAL_SPREAD / 2)

                
                

                    

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    if best_ask < OPTIMAL_ASK:
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                if len(order_depth.buy_orders) > 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > OPTIMAL_BID:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {OPTIMAL_BID}, {OPTIMAL_ASK}')

        
        return result









""" 
                if len(order_depth.sell_orders) > 0:

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
                        orders.append(Order(product, best_bid, -best_bid_volume)) """

                # Add all the above orders to the result dict
                #result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        
        #return result
