#https://github.com/pavndutt/MarketMakerPython/blob/main/2_ForwardLooking_MM.ipynb
#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd


class Trader:
    trade_bps = 2
    hedge_bps = 0.5
    max_order_value = 10000
    hedge_threshold = 5
    order_size = 1


    #reference information
    prev_price = 0
    prev_bid = 0
    prev_ask = 0
    prev_hedge_bid = 0
    prev_hedge_ask = 0
    prev_notional_capacity_buy = 0
    prev_notional_capacity_sell = 0
    prev_timestamp = 0
    prev_hedge_flag = 0
    prev_bid_qty = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        trade_bps = trade_bps * 0.001
        hedge_bps = hedge_bps * 0.001

        # Initialize the method output dict as an empty dict
        result = {}
        for product in state.order_depths.keys():
            orders: list[Order] = []
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            prev_bid_qty = state.market_trades[product][-1].quantity

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0 and product == "BANANAS":
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                spot_price = (best_ask + best_bid)/2

                my_bid = (1-trade_bps)*spot_price
                my_ask = (1+trade_bps)*spot_price
                hedge_bid = (1-hedge_bps)*spot_price
                hedge_ask = (1+hedge_bps)*spot_price
                notional_capacity_buy = self.max_order_value/my_bid
                notional_capacity_sell = self.max_order_value/my_ask
                
                if self.prev_hedge_flag != 1:
                    if spot_price <= self.prev_bid:
                        trade = Order(product, my_bid, self.order_size)
                        orders.append(trade)
                else:
                    if spot_price >= self.prev_hedge_ask:
                        trade = Order(product, my_ask, -self.order_size)
                        orders.append(trade)
                if self.prev_hedge_flag != -1:
                    if spot_price >= self.prev_ask:
                        trade = Order(product, my_ask, -self.order_size)
                        orders.append(trade)
                else:
                    if spot_price <= self.prev_hedge_bid:
                        trade = Order(product, my_bid, self.order_size)
                        orders.append(trade)
                position = state.position[product]
                if position > self.hedge_threshold:
                    




                
                


        print("own trades: ", state.own_trades)
        
        return result