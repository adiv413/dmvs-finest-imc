#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:

    products = ["AMETHYSTS", "STARFRUIT"]

    SIGMA = {"AMETHYSTS" : 1.4801221814861618, "STARFRUIT" : 14.273755401780505}
    GAMMA = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1}
    
    ## MARKET MAKING PARAMETERS
    RISK_ADJUSTMENT = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1}
    ORDER_VOLUME = {"AMETHYSTS" : 5, "STARFRUIT" : 5}
    HALF_SPREAD_SIZE = {"AMETHYSTS": 4, "STARFRUIT": 3}
    ############################

    ## POSITION SIZING PARAMS
    MM_POSITION_LIMIT = {"AMETHYSTS" : 20, "STARFRUIT" : 20}
    MM_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0}
    MM_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, "STARFRUIT" : {"BUY": 0, "SELL": 0}}
    LAST_TIMESTAMP = -100000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        traderData = state.traderData

        for product in self.products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            # self.MM_POSITION[product] = state.position[product]
            # print()
            # print(f'Buy Orders: {order_depth.buy_orders}')
            # print(f'Sell Orders: {order_depth.sell_orders}')
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
            #     ##GET TRADES
            #     try:
            #         own_trades = state.own_trades[product]
            #     except:
            #         own_trades = []
                ##############################

                # ## CALCULATING THE POSITION SIZE OF MARKET MAKING
                # for trade in own_trades:
                #     if trade.timestamp == self.LAST_TIMESTAMP:
                #         if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["BUY"]:
                #             self.MM_POSITION[product] += trade.quantity
                #         elif trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["SELL"]:
                #             self.MM_POSITION[product] -= trade.quantity
                # ##############################
                try:
                    self.MM_POSITION[product] = state.position[product]
                except:
                    self.MM_POSITION[product] = 0

                # CALCULATING STATS
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask_volume = order_depth.sell_orders[best_ask]
                value = (best_ask + best_bid)/2
                #############################
                # print(order_depth.buy_orders)

                # MARKET MAKING STRATEGY
                skew = -self.MM_POSITION[product] * self.RISK_ADJUSTMENT[product]
                buy_quote = round(value - self.HALF_SPREAD_SIZE[product] + skew)
                sell_quote = round(value + self.HALF_SPREAD_SIZE[product] + skew)
                #############################

                # MARKET MAKING ORDERS
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))))
                # self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                #############################
                
                # ## PRINT STATS
                # print(f'{product}:')
                
                # try:
                #     position = state.position[product]
                # except:
                #     position = 0
                
                # print(f'Actual position: {position}')
                # print('Estimated MM position: ', self.MM_POSITION[product])
                # print('Estimated MCGINLEY position: ', self.MCGINLEY_POSITION[product])
                # ##############################
                
                result[product] = orders

        
        print('\n----------------------------------------------------------------------------------------------------\n')
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0

        return result, conversions, traderData