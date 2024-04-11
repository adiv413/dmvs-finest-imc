#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor
import collections


class Trader:

    products = ["AMETHYSTS", "STARFRUIT"]
    POSITION_LIMIT = {"AMETHYSTS": 20, "STARFRUIT": 20}

    AMETHYST_PRICE = 10000
    STARFRUIT_PRICE = -1
    
    def market_make_amethyst(self, product, order_depth, position):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        buyReserve = min(20, 20-position)
        sellReserve = max(-20, -20-position)
        ## Market Taking
        #BUYING
        print(f'Position: {position}')
        for sellOrder in osell:
            if sellOrder < self.AMETHYST_PRICE:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
            elif sellOrder == self.AMETHYST_PRICE and position < 0:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
               
        #BUYING

        #SELLING    
        for buyOrder in obuy:
            if buyOrder > self.AMETHYST_PRICE:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
            elif buyOrder == self.AMETHYST_PRICE and position > 0:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
               
        # SELLING

        print(f'Position: {position}')
        ###################################################################

        ## Market Making
        best_bid = list(obuy.keys())[0]
        best_ask = list(osell.keys())[0]
        #sell order
        orders.append(Order(product, max(best_ask-1, self.AMETHYST_PRICE+1), sellReserve))
        print(f'Market Making Sell Order at {max(best_ask-1, self.AMETHYST_PRICE+1)} with volume {sellReserve}')
        #buy order
        orders.append(Order(product, min(best_bid+1, self.AMETHYST_PRICE-1), buyReserve))
        print(f'Market Making Buy Order at {min(best_bid+1, self.AMETHYST_PRICE-1)} with volume {buyReserve}')
        ###################################################################
        
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        traderData = state.traderData

        for product in self.products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            try:
                position = state.position[product]
            except:
                position = 0

            if product == 'AMETHYSTS':
                orders = self.market_make_amethyst(product, order_depth, position)
                result[product] = orders
                continue

            result[product] = orders

        
        print('\n----------------------------------------------------------------------------------------------------\n')
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0

        return result, conversions, traderData