#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:

    ## MARKET MAKING PARAMETERS
    RISK_ADJUSTMENT = {"BANANAS" : 0.1, "PEARLS" : 0.1, "COCONUTS" : 0, "PINA_COLADAS" : 0}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5, "COCONUTS" : 10, "PINA_COLADAS" : 10}
    HALF_SPREAD_SIZE = {"BANANAS": 2, "PEARLS": 3, "COCONUTS": 1, "PINA_COLADAS": 1}
    ############################

    ## MCGINLEY PARAMETERS
    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "count" : {},
        "acceptable_price" : {
            "PEARLS" : -1,
            "BANANAS" : -1,
            "COCONUTS" : -1,
            "PINA_COLADAS" : -1
        } 
    }
    ############################

    ## POSITION SIZING PARAMS
    MM_POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10, "COCONUTS" : 150, "PINA_COLADAS" : 150}
    MM_POSITION = {"BANANAS" : 0, "PEARLS" : 0, "COCONUTS" : 0, "PINA_COLADAS" : 0}
    MM_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}, "COCONUTS" : {"BUY": 0, "SELL": 0}, "PINA_COLADAS" : {"BUY": 0, "SELL": 0}}
    ############################
    LAST_TIMESTAMP = -100000

    SPIKE_WINDOW_SIZE = 7
    SPIKE_OUTLIERS = 5

    PRICES = {"BANANAS": [], "PEARLS": [], "COCONUTS": [], "PINA_COLADAS": []}
    SPREADS = {"BANANAS": [], "PEARLS": [], "COCONUTS": [], "PINA_COLADAS": []}

    def calc_ISMA(self, value): #this takes the last SPIKE_WINDOW_SIZE spreads and prices, and removes SPIKE_OUTLIERS prices that are associated with the lowest spreads

        if len(self.PRICES) < self.SPIKE_WINDOW_SIZE:
            return value
        prices = self.PRICES[-self.SPIKE_WINDOW_SIZE:]
        spreads = self.SPREADS[-self.SPIKE_WINDOW_SIZE:]
        #remove the prices associated with the lowest spreads
        prices = [x for _,x in sorted(zip(spreads,prices))]
        prices = prices[self.SPIKE_OUTLIERS:]
        #get the average of the remaining prices
        avg = sum(prices) / len(prices)
        return avg

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                ##GET TRADES
                try:
                    own_trades = state.own_trades[product]
                except:
                    own_trades = []
                ##############################

                ## CALCULATING THE POSITION SIZE OF MARKET MAKING
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MM_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MM_POSITION[product] -= trade.quantity
                ##############################

                ## CALCULATING STATS
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask_volume = order_depth.sell_orders[best_ask]
                value = (best_ask + best_bid)/2
                ##############################

                ## MARKET MAKING STRATEGY
                spike_SMA = self.calc_ISMA(value)
                value = spike_SMA
                skew = -self.MM_POSITION[product] * self.RISK_ADJUSTMENT[product]
                buy_quote = floor(value - self.HALF_SPREAD_SIZE[product] + skew)
                sell_quote = floor(value + self.HALF_SPREAD_SIZE[product] + skew)
                ##############################

                ## MARKET MAKING ORDERS
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))))
                self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                ##############################
                
                ## PRINT STATS
                # print(f'{product}:')
                
                try:
                    position = state.position[product]
                except:
                    position = 0
                
                # print(f'Actual position: {position}')
                # print('Estimated MM position: ', self.MM_POSITION[product])
                # print('Estimated MCGINLEY position: ', self.MCGINLEY_POSITION[product])
                ##############################
                
                result[product] = orders

        self.LAST_TIMESTAMP = state.timestamp
        
        # print('\n----------------------------------------------------------------------------------------------------\n')
        return result