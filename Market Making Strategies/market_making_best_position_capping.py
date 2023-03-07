#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:
    # PROFIT_TARGET = 1
    #BEST
    # RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    # ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    # HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}
    MM_POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10}
    MM_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    MM_LAST_ORDER_PRICE = {"BANANAS" : int, "PEARLS" : int}
    LAST_TIMESTAMP = -100000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print('\n')
        result = {}

        for product in state.order_depths.keys():
            orders: list[Order] = []
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
                skew = -position * self.RISK_ADJUSTMENT[product]

                buy_quote = value - self.HALF_SPREAD_SIZE[product] + skew
                sell_quote = value + self.HALF_SPREAD_SIZE[product] + skew

    
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - position))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + position))))

                

                try:
                    own_trades = state.own_trades[product]
                    print(f'Own trades for {product}: {own_trades}')
                except:
                    own_trades = []
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION":
                            print(f'{trade.price}, {self.MM_LAST_ORDER_PRICE["BUY"]}')
                            print(trade.price == self.MM_LAST_ORDER_PRICE["BUY"])
                        if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE["BUY"]:
                            self.MM_POSITION[product] += trade.quantity
                        if trade.seller == "SUBMISSION":
                            print(f'{trade.price}, {self.MM_LAST_ORDER_PRICE["SELL"]}')
                            print(trade.price == self.MM_LAST_ORDER_PRICE["SELL"])
                        if trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE["SELL"]:
                            self.MM_POSITION[product] -= trade.quantity

                print('Actual position: ', position)
                print('Estimated MM position: ', self.MM_POSITION[product])

                self.MM_LAST_ORDER_PRICE = {"BUY": floor(buy_quote), "SELL": floor(sell_quote)}
                self.LAST_TIMESTAMP = state.timestamp
                result[product] = orders
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        return result