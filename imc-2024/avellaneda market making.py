#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:

    products = ["AMETHYSTS", "STARFRUIT"]

    SIGMA = {"AMETHYSTS" : 1.4801221814861618, "STARFRUIT" : 14.273755401780505}
    GAMMA = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1}

    ## POSITION SIZING PARAMS
    MM_POSITION_LIMIT = {"AMETHYSTS" : 20, "STARFRUIT" : 20}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        traderData = state.traderData

        for product in self.products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                position = state.position[product]
                
                
                # MARKET MAKING ORDERS
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))))
                # self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                #############################
                
                result[product] = orders

        
        print('\n----------------------------------------------------------------------------------------------------\n')
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0

        return result, conversions, traderData